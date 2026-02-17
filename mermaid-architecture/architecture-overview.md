# Knowledge Base — Architecture Overview

High-level view for quickly understanding the codebase.

```mermaid
flowchart LR
    subgraph Input["Inputs"]
        Gateway["api-gateway\n/storage/files"]
        Client["API clients\n/v1/kb/*"]
    end

    subgraph KB["knowledge-base service"]
        API["FastAPI\n/v1"]
        Ingest["Ingest\nsync, sources, files"]
        Query["Query\nsearch, stats"]
        LLM["LLM\nchat/completions + RAG"]
        DB[(PostgreSQL\npgvector)]
    end

    subgraph External["External"]
        Voyage["Voyage AI\nembeddings, rerank"]
        AIGw["api-gateway\n/ai, /storage"]
    end

    Gateway --> Ingest
    Client --> Ingest
    Client --> Query
    Client --> LLM
    Ingest --> DB
    Query --> DB
    LLM --> DB
    Ingest --> Voyage
    Query --> Voyage
    LLM --> AIGw
```

**In one sentence:** FastAPI service that syncs documents from the gateway’s Drive, embeds and stores them in Postgres+pgvector, and exposes search and an OpenAI-compatible chat with RAG.
