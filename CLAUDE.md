# CLAUDE.md - FONASA MLE Open Data

## Project Overview
Open-source initiative to provide clean access to Chilean medical exam catalogs (FONASA MLE).

- **Stack**: TypeScript (MCP Server), Python (Data Extraction), JSON (Storage)
- **Repo**: `@examya/fonasa-mle-open`

## Commands

### Data Extraction
```bash
# Layout 2026 (Inline strings)
python3 scripts/generate_json.py --input <path_to_xlsx> --output data/mle-2026.json --layout 2026

# Layout 2025 (Shared strings)
python3 scripts/generate_json.py --input <path_to_xlsx> --output data/mle-2025.json --layout 2025
```

### MCP Server
```bash
pnpm install
pnpm build
pnpm start # Starts stdio server
pnpm dev   # Runs via tsx
```

## Data Structure
JSON files in `data/` follow this schema:
```json
{
  "code": "0301045",
  "name": "HEMOGRAMA",
  "level1_total": 1680,
  "level1_copay": 1680,
  "level2_total": 2240,
  "level2_copay": 2240,
  "level3_total": 2800,
  "level3_copay": 2800
}
```

## Workflow
- Always normalize codes to 7 digits (Grupo+Subgrupo+Item).
- Use `lxml` for Python extraction scripts.
- Keep MCP tools simple: `buscar_examen` and `obtener_detalle_examen`.
