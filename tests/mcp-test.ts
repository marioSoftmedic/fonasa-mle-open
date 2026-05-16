import { Exam } from "../src/index.js";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "../data");

async function runTests() {
  console.log("🧪 Iniciando pruebas de validación de datos MLE 2026...");

  const data2026 = JSON.parse(await fs.readFile(path.join(DATA_DIR, "mle-2026.json"), "utf-8"));
  
  // 1. Prueba de integridad básica
  console.log(`- Total registros 2026: ${data2026.length}`);
  if (data2026.length < 2500) throw new Error("⚠️ El catálogo 2026 parece incompleto");

  // 2. Prueba de normalización de códigos (7 dígitos)
  const invalidCodes = data2026.filter((e: any) => e.code.length !== 7 || !/^\d+$/.test(e.code));
  if (invalidCodes.length > 0) {
    console.error("❌ Códigos mal formateados encontrados:", invalidCodes.slice(0, 5));
    throw new Error("Hay códigos que no cumplen el formato de 7 dígitos");
  }
  console.log("✅ Todos los códigos están normalizados a 7 dígitos.");

  // 3. Prueba de búsqueda (simulando herramienta buscar_examen)
  const query = "HEMOGRAMA";
  const results = data2026.filter((e: any) => e.name.includes(query));
  console.log(`- Búsqueda "${query}": ${results.length} resultados encontrados.`);
  if (results.length === 0) throw new Error("No se encontró el Hemograma en 2026");

  // 4. Validación de Precios (Hemograma 0301045)
  const hemograma = data2026.find((e: any) => e.code === "0301045");
  console.log("- Detalle Hemograma 0301045:", hemograma);
  if (hemograma.level1_total !== 3170) {
    throw new Error(`Precio Hemograma Nivel 1 incorrecto: ${hemograma.level1_total} (esperado 3170)`);
  }
  console.log("✅ Validación de precios exitosa para código 0301045.");

  console.log("\n🎉 ¡Todas las pruebas pasaron con éxito!");
}

runTests().catch(err => {
  console.error("\n❌ Falla en las pruebas:", err.message);
  process.exit(1);
});
