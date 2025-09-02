# My-AI
Personal AI Assistant - Local-First Intelligence Platform

## Overview
A privacy-focused personal AI assistant that runs locally first, with optional cloud fallbacks. Built around Retrieval Augmented Generation (RAG) with your personal documents and integrated tools for productivity.

## Architecture
- **Local-First**: Primary processing using local models (Ollama/vLLM)
- **Cloud Fallback**: Optional external APIs (GPT/Claude) when needed
- **Tool-Based**: Extensible system with read-only integrations
- **Privacy-Centric**: Your data stays local by default

## Core Features
### Phase 0 (MVP)
- 📚 **RAG Answer**: Search and cite from your personal document corpus
- 🔍 **Drive Search**: Find files across connected storage
- 🌐 **Web Search**: Fetch public references with attribution

### Phase 1 (Planned)
- 📅 **Calendar Integration**: Read events and scheduling data
- 🎵 **Spotify Lookup**: Access playlists and music data

### Phase 2 (Future)
- 💰 **Banking Read-Only**: Financial insights (optional, secure)

## API Endpoints
- `POST /v1/query` - Main query interface
- `POST /v1/ingest` - Add documents to knowledge base
- `POST /v1/chat` - Direct LLM gateway (local models)
- `POST /v1/embeddings` - Vectorize text for RAG

## Quick Start
*Coming soon - implementation in progress*

## Security & Privacy
- ✅ Local processing by default
- ✅ No secrets in logs
- ✅ Parameterized queries only
- ✅ User data stays on your machine
- ✅ Optional cloud features require explicit consent

## Development Roadmap

### ✅ Step 0: Planning & Contracts (Complete)
- Software contracts and guardrails defined
- API surfaces and tool allowlists established
- Tier-2 routing strategy documented

### 🚧 Step 1: API Scaffolding (In Progress)
- Repository structure: `apps/api`, `packages/core`, `packages/rag`, `packages/llms`, `packages/agents`, `packages/connectors`
- Basic `/v1/query` endpoint with placeholder responses
- Health check endpoint

### 📋 Step 2: Local LLM Gateway (Planned)
- Ollama/vLLM integration for local models
- `/v1/chat` and `/v1/embeddings` endpoints
- Configurable local/cloud model switching

### 📋 Step 3: RAG MVP (Planned)
- Document ingestion and chunking pipeline
- SQLite + FAISS/sqlite-vec storage
- Cited answer retrieval from personal corpus

### 📋 Step 4: AI Router (Planned)
- Natural language to `{tool, args}` JSON routing
- Schema validation and clarification flows
- Bounded LLM call counts (1-2 per request)

### 📋 Step 5: Tool Integration (Planned)
- Drive search, web search, calendar lookup
- Read-only tool implementations
- Tool execution transcripts and logging

### 📋 Step 6: Memory System (Planned)
- Short-term session memory
- Local storage with purge capabilities
- Foundation for future long-term memory

### 📋 Step 7: Dynamic Corpus (Future)
- AI-proposed document updates
- Human approval workflow
- Provenance tracking and diff management

## Project Structure
```
apps/
  api/              # Personal API server
packages/
  core/             # Shared utilities and types
  rag/              # Retrieval augmented generation
  llms/             # LLM gateway and model management
  agents/           # AI routing and tool orchestration
  connectors/       # External service integrations
```

## Development Status
🚧 **Step 0 Complete, Step 1 In Progress** - See `/Documentation/software contract/` for detailed specifications

## Contributing
This is a personal project following a structured development path. See documentation for implementation details and architecture decisions.
