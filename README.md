# IMT Mines Alès Chatbot - Agentic RAG with MCP

An AI-powered chatbot designed to assist international students at IMT Mines Alès with academic information, administrative procedures, and campus services. This project implements the **Agentic Retrieval-Augmented Generation (RAG)** system using the **Model Context Protocol (MCP)** and **LangGraph**.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-19.2.0-61DAFB.svg?logo=react)](https://react.dev/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12.3+-purple.svg)](https://github.com/jlowin/fastmcp)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.27+-orange.svg)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.7+-red.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---
## 🎥 Demo Video



https://github.com/user-attachments/assets/5bc3b84b-d52a-4f63-94f9-d4db74552800


---

## 📋 Table of Contents

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

## 🎯 Overview

This chatbot provides 24/7 assistance to international students by answering questions about:

- Course syllabi and academic requirements
- Administrative procedures and documentation
- Campus facilities and student services
- General information about IMT Mines Alès

The system achieves **9.26/10** overall score (evaluated by GPT-4o as judge), demonstrating:

- **8.91/10** Correctness
- **9.12/10** Completeness
- **10.00/10** Safety

---

## 🏗️ Architecture

The system consists of three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React + TS)                    │
│                     Port: 5173                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (FastAPI + LangGraph Agent)             │
│                     Port: 8000                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │   ReAct Agent (gpt-oss-20b via Groq)               │     │
│  │   • Reasoning & Tool Orchestration                 │     │
│  │   • Memory Persistence                             │     │
│  └────────────┬───────────────────────────────────────┘     │
└───────────────┼─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server (RAG Tools)                          │
│                     Port: 3000                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │   Tools:                                           │     │
│  │   • ingest_documents (PDF/URL)                     │     │
│  │   • retrieve_documents (Semantic Search)           │     │
│  │   • get_vector_store_info                          │     │
│  │   • clear_vector_store                             │     │
│  └────────────┬───────────────────────────────────────┘     │
└───────────────┼─────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│         ChromaDB Vector Store + BGE-M3 Embeddings            │
│         • Chunk Size: 1000 tokens                            │
│         • Overlap: 200 tokens                                │
│         • Top-K: 5 documents                                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **BGE-M3 Embeddings**: State-of-the-art multilingual embedding model for retrieval
- **ReAct Pattern**: Enables reasoning and action interleaving for complex queries
- **MCP Protocol**: Standardized interface for AI-to-tool communication
- **Low-Latency Inference**: Groq API provides sub-second response times
- **Stateful Agent**: LangGraph manages conversation history and context

---

## ✨ Features

- 🔍 **Semantic Search**: Retrieves relevant documents using dense vector embeddings
- 🤖 **ReAct Agent**: Reasons through complex multi-step queries
- 📚 **Document Management**: Ingest PDFs from local files, directories, or URLs
- 🌐 **Multilingual Support**: BGE-M3 handles multiple languages
- 💬 **Chat Interface**: Clean React-based UI with markdown rendering
- 🔒 **Safety First**: Achieves perfect 10/10 safety score in evaluations
- 📊 **Observable Reasoning**: Transparent agent thought process

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** (tested with Python 3.11)
- **Node.js 18+** and **npm**
- **Git**

### API Keys Required

You'll need API keys for:

- **Groq API**: For `gpt-oss-20b` model ([Get API key](https://console.groq.com/keys))
- **OpenAI API** (optional): For LLM-as-a-Judge

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Samreth99/agentic-mcp-imt.git
cd agentic-mcp-imt
```

### 2. Install UV Package Manager

UV is a fast Python package installer and resolver. Install it following the [official documentation](https://docs.astral.sh/uv/getting-started/installation/):

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create Virtual Environment

```bash
uv venv .venv
```

### 4. Activate Virtual Environment

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 5. Install Project Dependencies

```bash
uv pip install .
```

This will install all required dependencies including:

- LangChain & LangGraph
- FastAPI & Uvicorn
- ChromaDB
- Sentence Transformers
- And more...

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## 🏃 Running the Application

The application requires **three separate terminal windows**, each running a different component.

### Terminal 1: MCP Server (RAG Tools)

```bash
# Make sure virtual environment is activated
uv run -m mcp_server.server.tools.rag.rag_server
```

**Expected output:**

```
MCP Server running on http://localhost:3000
Vector store initialized with ChromaDB
```

### Terminal 2: Agent Backend Server

```bash
# Make sure virtual environment is activated
uv run -m agent.main
```

**Expected output:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 3: Frontend Development Server

```bash
cd frontend
npm run dev
```

**Expected output:**

```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Accessing the Application

Open your browser and navigate to:

```
http://localhost:5173
```

You should see the chat interface ready to accept queries!

---

## 📂 Project Structure

```
agentic-mcp-imt/
├── agent/                         # Backend agent implementation
│   ├── main.py                    # FastAPI application entry point
│   ├── agent_client.py            # Agent client for testing
│   ├── api/                       # FastAPI routes and services
│   ├── config/                    # Configuration files
│   │   └── prompts.py             # System prompts and templates
│   ├── evaluation/                # Evaluation
│   │   └── data_set.py            # Testset
│   │   └── llm_as_a_judge.py      # LLM-as-a-Judge Evalulation
│   ├── graph/                     # LangGraph implementation
│   │   └── graph_builder.py       # LangGraph ReAct agent logic
│   ├── schemas/                   # Pydantic schemas
│   └── utils/                     # Utility functions
│
├── mcp_server/                    # MCP server implementation
│   └── server/
│       └── tools/
│           └── rag/
│               ├── rag_server.py  # MCP RAG tool server
│               └── ingestion/     # Data ingestion pipeline
│                   └── vector_store.py # ChromaDB interface
│
├── frontend/                      # React TypeScript frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── api/                  # API services
│   │   └── App.tsx               # Main application
│   ├── package.json
│   └── vite.config.ts
│
├── evaluation_results.json        # Evaluation metrics
├── pyproject.toml                 # Python project configuration
├── docker-compose.yaml            # Docker orchestration
├── Dockerfile.backend             # Dockerfile for the backend
├── Dockerfile.mcp                 # Dockerfile for the MCP server
├── uv.lock                        # UV lock file
└── README.md                      # This file
```



## 🛠️ Technologies Used

### Backend

- **LangChain & LangGraph**: Agent orchestration and reasoning
- **FastAPI**: High-performance async web framework
- **ChromaDB**: Vector database for embeddings
- **BGE-M3**: Multilingual embedding model
- **Groq API**: Ultra-low latency LLM inference
- **Model Context Protocol (MCP)**: Standardized tool interface

### Frontend

- **React 18**: UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool
- **TailwindCSS**: Utility-first styling

### Infrastructure

- **UV**: Fast Python package management
- **Docker & Docker Compose**: Containerization
- **Uvicorn**: ASGI server

---

## 📊 Evaluation Results

Evaluated using **GPT-4o as a judge** on 33 test questions:

| Metric            | Agentic RAG MCP | Fine-Tuning Baseline |
| ----------------- | --------------- | -------------------- |
| **Correctness**   | 8.91/10 ⭐      | 5.32/10              |
| **Completeness**  | 9.12/10 ⭐      | 4.85/10              |
| **Safety**        | 10.00/10 ⭐     | 9.35/10              |
| **Overall Score** | **9.26/10** ⭐  | 6.17/10              |

### Key Findings

- ✅ **Grounded Responses**: RAG retrieval ensures factual accuracy
- ✅ **Comprehensive Answers**: Multi-document synthesis provides complete information
- ✅ **Perfect Safety**: Strong adherence to ethical guidelines
- ✅ **Scalable Architecture**: Easy to update knowledge base without retraining

---

## 🔮 Future Work

### Production Infrastructure

- [ ] PostgreSQL for user management
- [ ] MongoDB for conversation history
- [ ] OAuth 2.0 authentication
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Kubernetes deployment
- [ ] Monitoring and alerting

### Model Improvements

- [ ] **Hybrid Retrieval**: Combine BM25 sparse + dense embeddings
- [ ] **Reranking**: Cross-encoder for precision improvement
- [ ] **Adaptive-RAG**: Query complexity-aware retrieval
- [ ] **Self-RAG**: Self-reflective generation
- [ ] **RLHF**: Collect user feedback for continuous improvement

### Feature Extensions

- [ ] Schedule management MCP server
- [ ] Administrative procedures MCP server
- [ ] Event calendar integration
- [ ] Multilingual UI support
- [ ] Export conversation history

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Related Technologies

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [Groq API](https://groq.com/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216)

---

## 🙏 Acknowledgments

- IMT Mines Alès for providing the institutional knowledge base
- Anthropic for the Model Context Protocol specification
- LangChain team for the excellent agent framework
- Groq for providing ultra-fast LLM inference

---

<div align="center">
Made with ❤️ for international students at IMT Mines Alès
</div>
