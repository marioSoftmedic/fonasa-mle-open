import json
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from lxml import etree
import zipfile

# Secure XML Parser to prevent XXE
SAFE_PARSER = etree.XMLParser(resolve_entities=False, no_network=True)

@dataclass
class Exam:
    code: str
    name: str
    level1_total: int
    level1_copay: int
    level2_total: int
    level2_copay: int
    level3_total: int
    level3_copay: int

def load_shared_strings(z):
    try:
        with z.open('xl/sharedStrings.xml') as f:
            tree = etree.parse(f, parser=SAFE_PARSER)
            ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
            return [t.text if t.text is not None else "" for t in tree.xpath(".//ns:t", namespaces={'ns': ns})]
    except KeyError:
        return []

def normalize_code(code):
    if not code: return None
    s = str(code).split('.')[0]
    # Check if there are non-digit characters (ignoring dots which we split)
    if any(not c.isdigit() for c in s):
        sys.stderr.write(f"⚠️ Código malformado detectado: {code}\n")
    clean = "".join(filter(str.isdigit, s))
    if not clean or len(clean) > 7: return None
    return clean.zfill(7)

def to_int(v):
    if v is None: return 0
    s = str(v).strip()
    if not s or s == "0": return 0
    
    # Handle Chilean format and potential XML float strings
    # If it has a comma, it's likely decimal (Chilean locale).
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "." in s:
        # Strip trailing zero decimals (.0, .00, etc)
        import re
        s = re.sub(r'\.0+$', '', s)
        
        # If dot remains and it looks like a float (e.g. 1.5), we keep it for float()
        # If it has 3 digits after dot, it's likely a thousands separator (1.680)
        parts = s.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3:
            s = s.replace(".", "")
            
    try:
        # float() handles scientific notation and remaining dots
        return int(round(float(s)))
    except (ValueError, TypeError):
        return 0

def parse_xlsx(xlsx_path: Path, layout: str):
    exams = []
    seen_codes = set()
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        shared_strings = load_shared_strings(z)
        sheet_files = sorted([f for f in z.namelist() if f.startswith('xl/worksheets/sheet') and f.endswith('.xml')])
        
        for sheet_file in sheet_files:
            print(f"  📄 Procesando {sheet_file}...")
            with z.open(sheet_file) as f:
                tree = etree.parse(f, parser=SAFE_PARSER)
                root = tree.getroot()
                rows = root.xpath(".//ns:row", namespaces={'ns': ns})
                
                for row_idx, row in enumerate(rows):
                    def val(col):
                        r_idx = row.get("r")
                        if r_idx is None: # Fallback if 'r' is missing
                             r_idx = str(row_idx + 1)
                        c = row.find(f"ns:c[@r='{col}{r_idx}']", namespaces={'ns': ns})
                        if c is None: return None
                        
                        raw_val = None
                        v_elem = c.find("ns:v", namespaces={'ns': ns})
                        if v_elem is not None:
                            raw_val = v_elem.text
                        
                        if c.get("t") == "s" and raw_val is not None:
                            try:
                                idx = int(raw_val)
                                return shared_strings[idx] if idx < len(shared_strings) else None
                            except ValueError:
                                return raw_val
                        
                        if c.get("t") == "inlineStr":
                            t = c.find(".//ns:t", namespaces={'ns': ns})
                            return t.text if t is not None else None
                            
                        return raw_val

                    if layout == "2026":
                        grupo, subgrupo, item = val("B"), val("C"), val("D")
                        nombre = val("O")
                        
                        g_norm = "".join(filter(str.isdigit, str(grupo))) if grupo else ""
                        sg_norm = "".join(filter(str.isdigit, str(subgrupo))) if subgrupo else ""
                        it_norm = "".join(filter(str.isdigit, str(item))) if item else ""
                        
                        if not (g_norm and sg_norm and it_norm and nombre) or it_norm == "000":
                            continue
                            
                        # Robust code generation: avoid truncation, ensure correct digits
                        if len(g_norm) > 2 or len(sg_norm) > 2 or len(it_norm) > 3:
                            sys.stderr.write(f"⚠️ Fila {row.get('r')} saltada: Código fuera de rango ({g_norm}-{sg_norm}-{it_norm})\n")
                            continue
                            
                        code = f"{g_norm.zfill(2)}{sg_norm.zfill(2)}{it_norm.zfill(3)}"
                        if not code.isdigit(): continue
                        
                        prices = [val("P"), val("Q"), val("R"), val("S"), val("T"), val("U")]
                        final_prices = [to_int(p) for p in prices]
                    else:
                        raw_code = val("A")
                        code = normalize_code(raw_code)
                        if not code: continue
                        
                        name_b = val("B")
                        name_c = val("C")
                        
                        # Detect layout 2025:
                        # Layout 1 (Lab): B has name, C-H has prices.
                        # Layout 2 (Proc): B is short numeric (Pabellon), C has name, K-V has prices.
                        
                        # If name_b is numeric and short, it's likely Pabellon (Layout 2)
                        b_is_numeric = str(name_b).isdigit() if name_b else False
                        
                        if name_b and not b_is_numeric and len(str(name_b)) >= 2:
                            nombre = str(name_b)
                            prices = [val("C"), val("D"), val("E"), val("F"), val("G"), val("H")]
                            final_prices = [to_int(p) for p in prices]
                        elif name_c and len(str(name_c)) >= 2:
                            nombre = str(name_c)
                            # Sum Honorarios (K-P) and Procedimientos (Q-V)
                            h = [to_int(val(c)) for c in ["K", "L", "M", "N", "O", "P"]]
                            p = [to_int(val(c)) for c in ["Q", "R", "S", "T", "U", "V"]]
                            final_prices = [h[i] + p[i] for i in range(6)]
                        else:
                            continue

                    if code in seen_codes: continue
                    if len(nombre.strip()) < 2 or code == "0000000": continue
                    if final_prices[0] == 0: continue

                    exams.append(asdict(Exam(
                        code=code,
                        name=nombre.strip(),
                        level1_total=final_prices[0],
                        level1_copay=final_prices[1],
                        level2_total=final_prices[2],
                        level2_copay=final_prices[3],
                        level3_total=final_prices[4],
                        level3_copay=final_prices[5]
                    )))
                    seen_codes.add(code)
                    
    return exams

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--layout", choices=["2025", "2026"], required=True)
    args = parser.parse_args()

    print(f"🚀 Procesando {args.input} ({args.layout})...")
    exams = parse_xlsx(args.input, args.layout)
    
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(exams, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Extraídos {len(exams)} exámenes en {args.output}")

if __name__ == "__main__":
    main()
