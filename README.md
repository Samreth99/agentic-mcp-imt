# IMT Mines Alès Chatbot — Agentic RAG + Knowledge Graph with MCP

An AI-powered chatbot designed to assist international students at IMT Mines Alès with academic information, administrative procedures, and campus services. This project implements an **Agentic RAG + Knowledge Graph** system using the **Model Context Protocol (MCP)**, **LangGraph**, and **Apache Jena Fuseki**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react)](https://reactjs.org/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.3+-purple.svg)](https://github.com/jlowin/fastmcp)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27+-orange.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.7+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Fuseki](https://img.shields.io/badge/Apache%20Jena%20Fuseki-SPARQL-red.svg)](https://jena.apache.org/documentation/fuseki2/)
[![LangSmith](https://img.shields.io/badge/LangSmith-Tracing-green.svg)](https://smith.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Demo Video

https://github.com/user-attachments/assets/5bc3b84b-d52a-4f63-94f9-d4db74552800

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Evaluation Results](#evaluation-results)
- [Future Work](#future-work)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This chatbot provides 24/7 assistance to international students by answering questions about:

- Course syllabi, ECTS credits, and academic requirements
- Professor information and teaching assignments
- Evaluation methods and coefficients
- Administrative procedures and campus services
- General information about IMT Mines Alès programs

The system combines two complementary knowledge retrieval strategies:

- **Vector RAG** — semantic search over full PDF text for open-ended contextual questions
- **Knowledge Graph** — structured SPARQL queries over a Fuseki triplestore for precise factual lookups (ECTS, professors, evaluations, prerequisites, semesters)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                    │
│                        Port: 5173                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           Backend — FastAPI + LangGraph ReAct Agent          │
│                        Port: 8000                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ReAct Agent (gpt-oss-20b via Groq)                  │   │
│  │  • Autonomous tool selection (RAG vs KG)             │   │
│  │  • Multi-step reasoning & tool orchestration         │   │
│  │  • LangSmith tracing & observability                 │   │
│  └────────┬──────────────────────────┬──────────────────┘   │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐  ┌───────────────────────────────────┐
│  RAG MCP Server       │  │  KG MCP Server                    │
│  Port: 3000           │  │  Port: 3001                       │
│                       │  │                                   │
│  • retrieve_documents │  │  • query_knowledge_graph          │
│  • ingest_documents   │  │    (NL → SPARQL → Fuseki)         │
│  • get_vector_store_  │  │  • sparql_query (direct)          │
│    info               │  │  • build_knowledge_graph          │
│  • clear_vector_store │  │    (PDF → triples → Fuseki)       │
└──────────┬────────────┘  │  • get_kg_statistics              │
           │               └──────────────┬────────────────────┘
           ▼                              ▼
┌───────────────────────┐  ┌───────────────────────────────────┐
│  ChromaDB             │  │  Apache Jena Fuseki               │
│  BGE-M3 Embeddings    │  │  SPARQL 1.1 Triplestore           │
│  • Chunk: 1000 tokens │  │  Port: 3030                       │
│  • Overlap: 200       │  │  Dataset: /imt                    │
│  • Top-K: 5 docs      │  │  IMT OWL Ontology                 │
└───────────────────────┘  └───────────────────────────────────┘
```

### Key Design Decisions

- **Hybrid retrieval**: RAG handles open-ended questions; KG handles structured fact lookups — the ReAct agent decides autonomously
- **NL→SPARQL with self-correction**: LLM generates SPARQL, retries on failure with the error fed back as context
- **Deduplication at ingestion**: Fuseki tracks processed PDFs to prevent re-ingestion and entity drift
- **BGE-M3 Embeddings**: Multilingual embedding model for cross-language retrieval
- **MCP Protocol**: Standardized interface allowing the agent to call both RAG and KG tools uniformly
- **LangSmith tracing**: Full observability over every agent step, tool call, and LLM invocation

### IMT Knowledge Graph Ontology

The KG uses a formal OWL ontology (`mcp_server/server/tools/kg/ontology/imt_ontology.ttl`) with:

**Classes**: `imt:Module`, `imt:Course`, `imt:Professor`, `imt:Evaluation`, `imt:Program`, `imt:Track`, `imt:Semester`, `imt:Laboratory`, `imt:FAQEntry`

**Key properties**: `ects`, `supervisedHours`, `lectureHours`, `evaluationType`, `evaluationCoefficient`, `personName`, `semesterCode`, `taughtBy`, `responsibleProfessor`, `hasEvaluation`, `inSemester`, `partOfProgram`, `hasPrerequisite`

---

## Features

- **Semantic Search**: Dense vector retrieval over 138 IMT PDF course guides
- **Knowledge Graph Queries**: Precise structured answers via NL→SPARQL pipeline
- **ReAct Agent**: Autonomously selects the right tool for each question type
- **PDF Ingestion**: LLM-based triple extraction from PDFs directly into Fuseki
- **Deduplication**: Fuseki-tracked ingestion log prevents re-processing PDFs
- **Multilingual**: BGE-M3 handles French and English course content
- **Observable**: LangSmith traces every agent step for evaluation and debugging
- **Chat Interface**: React UI with live tool status indicators

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **Docker**
- **Git**

### API Keys Required

```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key        # for LLM-as-a-Judge evaluation
FUSEKI_URL=http://localhost:3030/imt
FUSEKI_USER=your_fuseki_username
FUSEKI_PASSWORD=your_fuseki_password
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=agentic-mcp
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Samreth99/agentic-mcp-imt.git
cd agentic-mcp-imt
```

### 2. Install UV Package Manager

```powershell
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Install Dependencies

```bash
uv venv .venv
uv pip install .
```

### 4. Install Frontend Dependencies

```bash
cd frontend && npm install && cd ..
```

### 5. Start Apache Jena Fuseki

```bash
docker run -d --name fuseki -p 3030:3030 \
  -e ADMIN_PASSWORD=your_password \
  -v ${PWD}/fuseki-data:/fuseki \
  stain/jena-fuseki
```

Then open `http://localhost:3030`, log in as `admin/<your_password>`, and create a dataset named **`imt`** (Persistent TDB2).

---

## Running the Application

### Local Development (4 terminals)

```bash
# Terminal 1 — RAG MCP Server (port 3000)
uv run -m mcp_server.server.tools.rag.rag_server

# Terminal 2 — KG MCP Server (port 3001)
uv run -m mcp_server.server.tools.kg.kg_server

# Terminal 3 — Agent Backend (port 8000)
uv run -m agent.main

# Terminal 4 — Frontend (port 5173)
cd frontend && npm run dev
```

### Build the Knowledge Graph (one-time)

Ask the chatbot:

> _"Build the knowledge graph from `<path-to-pdf-ingestion-dataset>`"_

Or run directly:

```bash
uv run python -c "
from mcp_server.server.tools.kg.triple_extractor import process_directory, make_llm
result = process_directory('pdf_ingestion_dataset', make_llm())
print(result)
"
```

### Docker Deployment

```bash
docker compose up --build
```

Services started: `fuseki` (3030) → `rag_server` (3000) + `kg_server` (3001) → `api_server` (8000).

---

## Project Structure

```
agentic-mcp-imt/
├── agent/
│   ├── main.py                        # FastAPI entry point
│   ├── agent_client.py                # MCP client + LangGraph agent init
│   ├── api/                           # Routes and services
│   ├── config/
│   │   └── prompts.py                 # System prompt (RAG + KG tool guidance)
│   ├── evaluation/
│   │   ├── data_set.py                # 33-question evaluation dataset
│   │   └── llm_as_a_judge.py          # GPT-4o judge evaluation runner
│   └── graph/
│       └── graph_builder.py           # LangGraph ReAct agent
│
├── mcp_server/
│   ├── config/
│   │   ├── kg_constants.py            # Fuseki URL, credentials, LLM config
│   │   └── setting.py
│   └── server/tools/
│       ├── rag/
│       │   ├── rag_server.py          # RAG MCP server (port 3000)
│       │   └── ingestion/             # ChromaDB + BGE-M3 pipeline
│       └── kg/
│           ├── kg_server.py           # KG MCP server (port 3001)
│           ├── triple_extractor.py    # PDF → SPARQL INSERT → Fuseki
│           ├── sparql_executor.py     # NL → SPARQL → Fuseki → rows
│           └── ontology/
│               └── imt_ontology.ttl   # OWL ontology for IMT domain
│
├── frontend/                          # React + TypeScript UI
├── docker-compose.yaml                # Fuseki + RAG + KG + API services
├── Dockerfile.backend                 # Agent backend image
├── Dockerfile.mcp                     # RAG server image
├── Dockerfile.kg                      # KG server image
├── pyproject.toml
└── README.md
```

---

## Technologies Used

### Backend

- **LangChain & LangGraph** — agent orchestration and ReAct reasoning
- **FastAPI** — async REST API
- **ChromaDB** — vector database
- **BGE-M3** — multilingual embedding model
- **Groq API** — low-latency LLM inference (`gpt-oss-20b`)
- **Apache Jena Fuseki** — SPARQL 1.1 RDF triplestore
- **FastMCP** — MCP server framework
- **LangSmith** — agent tracing and observability

### Frontend

- **React 18 + TypeScript**
- **Vite**
- **TailwindCSS**

### Infrastructure

- **Docker & Docker Compose**
- **UV** — Python package management

---

## Evaluation Results

Evaluated using **GPT-4o as a judge** on 33 test questions covering course content, administrative procedures, and student services.

| Metric            | Agentic RAG + KG | Fine-Tuning Baseline |
| ----------------- | ---------------- | -------------------- |
| **Correctness**   | 8.30/10          | 5.32/10              |
| **Completeness**  | 8.61/10          | 4.85/10              |
| **Safety**        | 9.97/10          | 9.35/10              |
| **Overall Score** | **8.83/10**      | 6.17/10              |

### Key Findings

- **+2.66 points overall** vs fine-tuning — retrieval-augmented generation significantly outperforms a fine-tuned model on this domain
- **Grounded responses**: RAG + KG retrieval prevents hallucination of course facts
- **Structured precision**: Knowledge Graph enables exact answers to structured queries (ECTS, professors, evaluations) that RAG alone cannot reliably produce
- **Near-perfect safety**: Strong ethical guardrails maintained across all question types
- **No retraining needed**: Knowledge base updates (new PDFs) require only re-ingestion, not model retraining

---

## Future Work

### Layer 1 — Knowledge Graph Construction

- [ ] **Automatic ontology generation** — derive the domain ontology directly from the PDF corpus using an LLM, eliminating the need to author `imt_ontology.ttl` by hand; the inferred ontology adapts automatically as the document set grows

### Layer 2 — Decision Validation

- [ ] **Harness layer around KG generation** — because each LLM call is stochastic, individual triple-extraction runs can produce inconsistent or contradictory triples; a validation harness would:
  - Intercept every proposed action (triple insertion, SPARQL write) before it reaches Fuseki
  - Validate the proposed triples against the ontology rules (domain/range constraints, cardinality, required properties)
  - Approve or reject each action before execution
  - Log every decision with a structured explanation (rule violated, confidence score, corrective suggestion)

### Layer 3 — Extended Evaluation

- [ ] **Richer LLM-as-a-Judge metrics** — extend the existing GPT-4o judge framework beyond Correctness / Completeness / Safety with:
  - `sparql_validity` — rate of syntactically and semantically valid SPARQL generated
  - `tool_selection` — accuracy of the agent's choice between RAG and KG tools per question type
  - `hop_accuracy` — correctness of multi-hop reasoning chains across KG relations (e.g., course → professor → laboratory)

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Resources

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/)
- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216)
- [Groq API](https://groq.com/)
- [LangSmith](https://smith.langchain.com/)

---

<div align="center">
Made with ❤️ for international students at IMT Mines Alès
</div>
