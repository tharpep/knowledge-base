# MY-AI Personal Assistant

**Period:** August 2025 - Ongoing  
**Type:** Personal/Learning Project  
**Repository:** Current project (this codebase)

## Architecture & Features

**Backend:** FastAPI (Python) providing RESTful API services with OpenAI-compatible endpoints

**AI Capabilities:**
- Local-first AI assistant with privacy focus
- RAG (Retrieval-Augmented Generation) implementation with Qdrant vector database
- Integration with Ollama for local LLM inference
- Multi-provider support (Ollama, Anthropic Claude, Purdue GenAI Studio)
- Custom model tuning capabilities with version management
- Extensible tool integration framework with registry system
- Request logging and analytics with SQLite database

**Design Philosophy:** Privacy-focused, local-first architecture avoiding cloud dependencies where possible, with optional cloud fallbacks

## Technical Highlights

**Modular Architecture:**
- **RAG System** (`/rag`): Document ingestion, vector storage, retrieval, and generation
- **LLM Integration** (`/llm`): Gateway pattern with provider abstraction (local, cloud)
- **Agent Framework** (`/agents`): Tool system with registry, router, and base tool interface
- **CLI Interface** (`/cli`): Typer-based command-line interface with interactive chat
- **Core Services** (`/core`): Configuration management, schemas, utilities, prompt templates
- **External Connectors** (`/connectors`): Stubs for web search, drive, calendar integrations
- **Model Tuning** (`/tuning`): Fine-tuning pipeline with model registry and versioning

**Infrastructure & DevOps:**
- Docker-based deployment for reproducibility
- Docker Compose for local development with Ollama
- Comprehensive testing framework (pytest) with organized test suites
- Pre-commit hooks for code quality (ruff, black, mypy)
- Poetry for dependency management

**API Features:**
- OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/embeddings`, `/v1/models`)
- RAG-powered query endpoint with citations
- Document ingestion endpoint
- Health monitoring endpoints
- Request ID tracking for debugging and analytics

**Recent Enhancements:**
- Chat endpoint with optional RAG context integration
- Prompt template system with markdown files
- Configurable RAG retrieval (top-k, similarity threshold)
- Per-request prompt overrides for frontend flexibility

## Learning Objectives Achieved

Built practical experience with:
- AI/ML system architecture and design patterns
- RAG implementation and vector database integration
- Multi-provider LLM gateway design
- FastAPI RESTful API development
- Docker containerization and deployment
- Testing frameworks and code quality tools
- CLI development with Typer
- Configuration management with Pydantic Settings

**Status:** Ongoing development and experimentation - actively adding features like conversation summarization and enhanced RAG integration
