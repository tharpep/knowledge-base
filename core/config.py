"""Application configuration via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration — cloud-first KB service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ===== API Gateway =====
    api_gateway_url: str = Field(
        default="https://api-gateway-252332699398.us-central1.run.app",
        description="API gateway base URL for LLM calls",
    )
    api_gateway_key: str = Field(
        default="",
        description="API key for the gateway (X-API-Key header)",
    )
    default_model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="Default model sent to the gateway for LLM calls",
    )

    # ===== Database =====
    database_url: str = Field(
        default="",
        description="PostgreSQL connection string (asyncpg format)",
    )

    # ===== Embeddings =====
    cohere_api_key: Optional[str] = Field(
        default=None,
        description="Cohere API key for cloud embeddings and reranking",
    )
    embedding_model: str = Field(
        default="embed-v4.0",
        description="Cohere embedding model name",
    )

    # ===== Hybrid Search =====
    hybrid_sparse_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for FTS in hybrid search (0=dense only, 1=FTS only)",
    )

    # ===== Reranking =====
    rerank_enabled: bool = Field(
        default=True,
        description="Enable Cohere reranking after retrieval",
    )
    rerank_candidates: int = Field(
        default=30,
        ge=5,
        le=100,
        description="Number of candidates to retrieve before reranking",
    )
    rerank_model: str = Field(
        default="rerank-v4",
        description="Cohere reranking model name",
    )

    # ===== Query Expansion =====
    query_expansion_enabled: bool = Field(
        default=True,
        description="Enable LLM-based query expansion for better retrieval",
    )

    # ===== KB (knowledge base) =====
    kb_table_name: str = Field(
        default="kb_chunks",
        description="Table name for KB chunks",
    )
    kb_clear_on_ingest: bool = Field(
        default=True,
        description="Clear table before ingesting new documents",
    )
    kb_chunk_size: int = Field(
        default=1000,
        ge=100,
        le=5000,
        description="Maximum characters per chunk",
    )
    kb_chunk_overlap: int = Field(
        default=100,
        ge=0,
        le=500,
        description="Overlap characters between chunks",
    )

    # ===== Chat Context =====
    chat_context_enabled: bool = Field(
        default=True,
        description="Master switch: enable RAG context injection in chat",
    )
    chat_kb_enabled: bool = Field(
        default=True,
        description="Enable KB (document RAG) context in chat",
    )
    chat_kb_top_k: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Top-k chunks to retrieve from KB",
    )
    chat_kb_similarity_threshold: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for KB context",
    )
    chat_kb_use_cache: bool = Field(
        default=True,
        description="Cache KB results for similar queries",
    )

    # ===== Logging =====
    log_output: bool = Field(
        default=True,
        description="Enable verbose logging for RAG and system operations",
    )

    # ===== Ollama (local dev only — never deployed) =====
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL (local dev only)",
    )
    ollama_timeout: float = Field(
        default=5.0,
        description="Ollama connection timeout in seconds",
    )
    model_ollama: str = Field(
        default="llama3.1:8b",
        description="Default Ollama model (local dev only)",
    )


@lru_cache()
def get_config() -> AppConfig:
    """Get application configuration (singleton, cached)."""
    return AppConfig()
