# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands

```bash
# Install dependencies
make install              # or: poetry install

# Dev server (http://localhost:8000)
make dev                  # uvicorn with --reload

# CLI (after `poetry shell`)
myai chat                 # Interactive chat
myai serve                # Start API server
myai ingest --folder ./data/corpus
myai config               # Show config
myai setup                # Initial setup

# Testing
make test                 # All tests (pytest tests/ -v)
make test-api             # API route tests only
make test-ai              # AI provider tests only
make test-rag             # RAG system tests only
make test-tuning          # Tuning tests only
pytest tests/tests_api/test_specific.py -v  # Single test file

# Code quality
make lint                 # ruff check + mypy
make format               # black + ruff --fix

# Docker
make docker-dev           # docker-compose up --build
```

## Architecture

**Local-first personal AI assistant** with FastAPI backend, multi-provider LLM gateway, and sophisticated RAG pipeline. Python 3.11+, managed with Poetry.

### Core Layers

- **`app/`** — FastAPI application. `main.py` handles lifespan (init DB, gateway, RAG, tools), CORS, request logging middleware. Routes under `app/routes/` expose an OpenAI-compatible API (`/v1/chat/completions`).

- **`llm/`** — Multi-provider LLM gateway. `gateway.py` routes requests across providers (Ollama local, Anthropic cloud, Purdue academic) with automatic fallback. Each provider implements `base_client.py` interface.

- **`rag/`** — Three-stage RAG pipeline:
  1. **Ingestion**: `document_ingester.py` → `document_parser.py` (PDF/DOCX/TXT) → `chunking.py` (semantic chunking)
  2. **Storage**: `vector_store.py` (Qdrant) with dense (BGE-M3) + sparse (BM25) hybrid vectors
  3. **Retrieval**: `retriever.py` → `query_processor.py` (query expansion) → hybrid search → `reranker.py` (cross-encoder reranking)

  `rag_setup.py` contains `ContextEngine`, the main orchestrator composing all RAG components.

- **`agents/`** — Extensible tool system. `tool_registry.py` manages allowlist-based tool registration/execution. Tools extend `base_tool.py`. Currently includes `RAGAnswerTool`.

- **`core/`** — Shared infrastructure:
  - `config.py`: Pydantic Settings config loaded from `.env` (~350 lines, all tunables)
  - `prompts/`: Markdown system prompt templates (rag.md, llm.md, llm_with_rag.md, etc.)
  - `schemas/`: Pydantic request/response models
  - `session_store.py`: SQLite session/message persistence
  - `profile_manager.py`: User profile for LLM context injection

- **`cli/`** — Typer CLI (`myai` entry point). Commands in `cli/commands/`.

### Data Storage

- **Qdrant** (`data/qdrant_db/`): Vector collections — `library_docs` (document corpus) and `journal_entries` (chat history)
- **SQLite** (`data/sessions.db`): Session metadata + messages
- **SQLite** (`data/api_logs.db`): Request logging with token usage tracking
- **File blobs**: `data/library_blob/` (ingested docs), `data/journal_blob/` (exported sessions)

### Key Patterns

- **Provider gateway with fallback**: `llm/gateway.py` selects provider based on config/request, falls back to `PROVIDER_FALLBACK` on failure
- **Singleton config**: `core/config.py` uses `@lru_cache` for single `AppConfig` instance from `.env`
- **Session auto-ingest**: When switching sessions, previous session messages auto-ingest into Journal vector collection
- **Hybrid search**: Dense semantic (BGE-M3 1024d) + sparse lexical (BM25) with configurable weight (`HYBRID_SPARSE_WEIGHT`)
- **Two RAG knowledge sources**: Library (documents, permanent) and Journal (chat history) — independently configurable

### External Dependencies

- **Ollama** on `localhost:11434` for local LLM inference
- **Qdrant** on `localhost:6333` for vector storage
- **Redis** on `localhost:6379` for ARQ job queue (async ingestion)
- All configurable via `.env`; `docker-compose.yml` orchestrates the full stack
