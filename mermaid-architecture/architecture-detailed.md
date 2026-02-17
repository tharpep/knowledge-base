# Knowledge Base — Detailed Architecture

Specific structure: app lifecycle, routes, RAG pipeline, and database schema.

```mermaid
flowchart TB
    subgraph Entry["Entry & Lifecycle"]
        Main["app/main.py\ncreate_app(), lifespan"]
        Init["init_pool()\nSchema + migrations"]
        GatewayInit["AIGateway() singleton\n→ api-gateway /ai/v1/chat/completions"]
    end

    subgraph Routes["Routes (prefix /v1, auth)"]
        Health["health.py\nGET /health"]
        Query["query.py\nPOST /kb/search, GET /kb/stats"]
        Ingest["ingest.py\nPOST /kb/sync, GET /kb/sources, GET /kb/files\nDELETE /kb, DELETE /kb/files/{id}"]
        LLM["llm.py\nPOST /v1/chat/completions, GET /v1/models"]
        ConfigRoute["config.py\nGET /v1/config"]
    end

    subgraph RAG["RAG pipeline"]
        Sync["rag/sync.py\nsync_drive()\nlist_drive_files → download → parse → chunk → embed"]
        Loader["rag/loader.py\nlist_drive_files, download_file, parse_content\nPDF, DOCX, text, CSV, md"]
        Chunking["rag/chunking.py\nchunk_text (langchain-text-splitters)"]
        Embedder["rag/embedder.py\nembed_query, embed_documents\nVoyage, batch 96"]
        Retriever["rag/retriever.py\nretrieve()\ndense + FTS → RRF → Voyage rerank"]
        Reranker["rag/reranker.py\nrerank-2.5"]
        QueryProc["rag/query_processor.py\nOptional query expansion via gateway"]
    end

    subgraph DB["Database (core/database.py)"]
        Schema["kb_chunks\nid, content, embedding vector(1024), fts, drive_file_id, filename,\nsource_category, chunk_index, metadata"]
        Sources["kb_sources\nfile_id, filename, category, modified_time, last_synced, chunk_count, status"]
    end

    subgraph External["External"]
        Gateway["api-gateway\n/storage/files, /storage/files/{id}/content\n/ai/v1/chat/completions"]
        Voyage["Voyage AI\nembed, rerank"]
    end

    Main --> Init
    Main --> GatewayInit
    Main --> Routes
    Ingest --> Sync
    Query --> Retriever
    Sync --> Loader
    Sync --> Chunking
    Sync --> Embedder
    Sync --> Schema
    Sync --> Sources
    Retriever --> Embedder
    Retriever --> Reranker
    Retriever --> Schema
    Loader --> Gateway
    Embedder --> Voyage
    Reranker --> Voyage
    LLM --> Gateway
    QueryProc --> Gateway
```

**Key modules:**

| Module           | Role |
|------------------|------|
| `app/main.py`    | Lifespan: init_pool, AIGateway; mounts health, llm, query, ingest, config |
| `core/database.py` | asyncpg pool, kb_chunks + kb_sources schema, migrations |
| `core/config.py` | AppConfig (DATABASE_URL, VOYAGE_*, API_GATEWAY_*, etc.) |
| `rag/sync.py`    | Full/incremental Drive → kb_sources + kb_chunks |
| `rag/retriever.py` | Hybrid search: dense (HNSW) + FTS → RRF → rerank → threshold |
| `llm/gateway.py` | AIGateway: all LLM calls go to api-gateway |
