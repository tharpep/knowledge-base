# KB Service

Cloud-first personal knowledge base. Ingests documents from Google Drive, chunks and embeds them with Voyage AI, stores vectors in PostgreSQL + pgvector, and exposes a hybrid retrieval API (dense + FTS → RRF → rerank).

Deployed to GCP Cloud Run. All external access goes through the api-gateway `/kb/*` proxy — this service is internal.

## Architecture

```
Google Drive folders (General, Projects, Purdue, Career, Reference)
    ↓  api-gateway /storage
KB Service (this repo)
    ↓  chunk → embed (Voyage AI) → pgvector (Cloud SQL)
api-gateway /kb/* proxy
    ↓
Agent / local-mcp / any consumer
```

## API

All routes require `X-API-Key` header when `API_KEY` is set. Auth is disabled when `API_KEY` is empty (local dev).

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/kb/search` | Hybrid search (dense + FTS → RRF → rerank) |
| `POST` | `/v1/kb/sync` | Sync Drive folders into kb_chunks |
| `GET` | `/v1/kb/sources` | List tracked files with sync status |
| `GET` | `/v1/kb/files` | List indexed files with chunk counts |
| `GET` | `/v1/kb/stats` | Total chunk and file counts |
| `DELETE` | `/v1/kb` | Clear all indexed content |
| `DELETE` | `/v1/kb/files/{id}` | Remove a specific file |
| `POST` | `/v1/chat/completions` | OpenAI-compatible proxy with RAG injection |
| `GET` | `/health` | Health check (no auth) |

### Search request

```json
{
  "query": "how does auth refresh work?",
  "top_k": 5,
  "categories": ["projects", "general"],
  "threshold": 0.15,
  "expand_query": false
}
```

`categories` filters to specific Drive subfolders. Omit to search all.

## Setup

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL with pgvector (local: Docker; prod: GCP Cloud SQL)
- Voyage AI API key
- api-gateway running and accessible

### Local dev

```bash
# Install dependencies
poetry install

# Copy and fill in env vars
cp .env.example .env

# Start (auth disabled when API_KEY is empty)
poetry run uvicorn app.main:app --reload
```

### Environment variables

| Variable | Description |
|----------|-------------|
| `API_KEY` | Key callers must send. Empty = auth disabled. |
| `DATABASE_URL` | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `VOYAGE_API_KEY` | Voyage AI key for embeddings and reranking |
| `API_GATEWAY_URL` | api-gateway base URL |
| `API_GATEWAY_KEY` | api-gateway API key (for outbound LLM calls) |

See `.env.example` for all available settings.

## Project structure

```
app/
  main.py          — FastAPI app, lifespan, router registration
  dependencies.py  — API key auth
  routes/
    health.py      — /health
    query.py       — /v1/kb/search, /v1/kb/stats
    ingest.py      — /v1/kb/sync, /v1/kb/sources, /v1/kb/files
    llm.py         — /v1/chat/completions (RAG-injected)
    config.py      — /v1/config
core/
  config.py        — AppConfig (pydantic-settings)
  database.py      — asyncpg pool, schema init (kb_chunks + kb_sources)
rag/
  loader.py        — Drive file listing + download via api-gateway
  sync.py          — Drive → kb_chunks sync engine (incremental)
  chunking.py      — Text chunking (langchain-text-splitters)
  embedder.py      — Voyage AI embeddings
  reranker.py      — Voyage AI reranking
  retriever.py     — Hybrid retrieval (dense + FTS → RRF → rerank)
llm/
  gateway.py       — LLM client (proxies to api-gateway /ai)
```

## Deployment

Deploys to GCP Cloud Run via GitHub Actions on push to `main` (`.github/workflows/deploy.yml`).

One-time GCP setup:
```bash
gcloud artifacts repositories create kb-service \
  --repository-format=docker \
  --location=us-central1
```

Add `GCP_PROJECT_ID` and `GCP_SA_KEY` secrets to the GitHub repo. Set env vars on the Cloud Run service in the GCP console.
