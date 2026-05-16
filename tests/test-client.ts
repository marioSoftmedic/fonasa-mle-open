import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const serverPath = path.join(__dirname, "../dist/index.js");

async function main() {
  const transport = new StdioClientTransport({
    command: "node",
    args: [serverPath],
  });

  const client = new Client(
    { name: "test-client", version: "1.0.0" },
    { capabilities: {} }
  );

  await client.connect(transport);
  console.log("✅ Conectado al servidor MCP");

  // Listar herramientas
  const tools = await client.listTools();
  console.log("\n🛠 Herramientas disponibles:");
  tools.tools.forEach(t => console.log(`- ${t.name}: ${t.description}`));

  // Probar buscar_examen
  console.log("\n🔍 Probando buscar_examen('HEMOGRAMA')...");
  const searchResult = await client.callTool({
    name: "buscar_examen",
    arguments: { query: "HEMOGRAMA", year: "2026" }
  });
  console.log("Resultado:", JSON.stringify(searchResult.content, null, 2));

  // Probar obtener_detalle_examen
  console.log("\n📄 Probando obtener_detalle_examen('0301045')...");
  const detailResult = await client.callTool({
    name: "obtener_detalle_examen",
    arguments: { code: "0301045", year: "2026" }
  });
  console.log("Resultado:", JSON.stringify(detailResult.content, null, 2));

  process.exit(0);
}

main().catch(console.error);
