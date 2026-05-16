import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, "../data");

interface Exam {
  code: string;
  name: string;
  level1_total: number;
  level1_copay: number;
  level2_total: number;
  level2_copay: number;
  level3_total: number;
  level3_copay: number;
}

const server = new Server(
  {
    name: "fonasa-mle-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

async function loadData(year: string): Promise<Exam[]> {
  try {
    const filePath = path.join(DATA_DIR, `mle-${year}.json`);
    const content = await fs.readFile(filePath, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    return [];
  }
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "buscar_examen",
        description: "Busca exámenes en el catálogo de FONASA por nombre o código.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Nombre o código del examen (ej: HEMOGRAMA o 0301045)" },
            year: { type: "string", description: "Año del catálogo (2025 o 2026)", default: "2026" },
          },
          required: ["query"],
        },
      },
      {
        name: "obtener_detalle_examen",
        description: "Obtiene el detalle completo de precios de un examen por su código exacto.",
        inputSchema: {
          type: "object",
          properties: {
            code: { type: "string", description: "Código FONASA de 7 dígitos" },
            year: { type: "string", description: "Año del catálogo", default: "2026" },
          },
          required: ["code"],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "buscar_examen") {
    const { query, year = "2026" } = args as { query: string; year?: string };
    const data = await loadData(year);
    
    const normalizedQuery = query.toUpperCase();
    const results = data.filter(
      (e) => e.name.includes(normalizedQuery) || e.code.includes(query)
    ).slice(0, 10);

    return {
      content: [
        {
          type: "text",
          text: results.length > 0 
            ? JSON.stringify(results, null, 2) 
            : `No se encontraron exámenes para "${query}" en el catálogo ${year}.`,
        },
      ],
    };
  }

  if (name === "obtener_detalle_examen") {
    const { code, year = "2026" } = args as { code: string; year?: string };
    const data = await loadData(year);
    const exam = data.find((e) => e.code === code);

    return {
      content: [
        {
          type: "text",
          text: exam 
            ? JSON.stringify(exam, null, 2) 
            : `No se encontró el examen con código ${code} en el catálogo ${year}.`,
        },
      ],
    };
  }

  throw new Error("Herramienta no encontrada");
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("FONASA MLE MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
