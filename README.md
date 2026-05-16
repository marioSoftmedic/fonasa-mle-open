# FONASA MLE Open Data & MCP Server

Este proyecto tiene como objetivo democratizar el acceso al catálogo de exámenes de la **Modalidad Libre Elección (MLE) de FONASA** en Chile. 

Proporcionamos los datos limpios en formato JSON y un servidor **MCP (Model Context Protocol)** para que agentes de IA y desarrolladores puedan consultar códigos, descripciones y precios oficiales de forma sencilla.

## 🚀 Propósito
- **Interoperabilidad**: Facilitar el mapeo de prestaciones médicas a códigos estándares.
- **Transparencia**: Acceso rápido a los precios de los 3 niveles de convenio.
- **Comunidad**: Un recurso gratuito y actualizado anualmente (cada marzo).

## 🛠 Tech Stack
- **Lenguaje**: TypeScript (Node.js)
- **Protocolo**: MCP SDK (Model Context Protocol)
- **Data**: JSON estáticos (generados vía Python desde fuentes oficiales)

## 📁 Estructura
- `data/`: Contiene los catálogos anuales en formato JSON (mle-2025.json, mle-2026.json).
- `src/`: Servidor MCP para consultas en lenguaje natural.
- `scripts/`: Herramientas de extracción y normalización desde fuentes oficiales (XLSX).

## 📅 Roadmap
- [ ] Generar JSON para MLE 2025 y 2026.
- [ ] Implementar servidor MCP básico (search y detail).
- [ ] Publicar como paquete NPM.
- [ ] GitHub Action para actualización automática.

---
_Impulsado por la comunidad y el equipo de Examya._
