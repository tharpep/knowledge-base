"""Voyage AI embedding client for kb_chunks ingestion and retrieval."""

import asyncio
import logging
from typing import Optional

import voyageai

from core.config import get_config

logger = logging.getLogger(__name__)

_client: Optional[voyageai.Client] = None


def _get_client() -> voyageai.Client:
    global _client
    if _client is None:
        config = get_config()
        if not config.voyage_api_key:
            raise RuntimeError("VOYAGE_API_KEY not set")
        _client = voyageai.Client(api_key=config.voyage_api_key)
    return _client


async def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed a batch of document chunks for storage. Uses input_type='document'."""
    if not texts:
        return []
    config = get_config()
    client = _get_client()
    result = await asyncio.to_thread(
        client.embed, texts, model=config.embedding_model, input_type="document"
    )
    return result.embeddings


async def embed_query(text: str) -> list[float]:
    """Embed a single query string for retrieval. Uses input_type='query'."""
    config = get_config()
    client = _get_client()
    result = await asyncio.to_thread(
        client.embed, [text], model=config.embedding_model, input_type="query"
    )
    return result.embeddings[0]
