"""Voyage AI reranker — wraps rerank-2.5 for KB retrieval."""

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

import voyageai

from core.config import get_config

if TYPE_CHECKING:
    from rag.retriever import Chunk

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


async def rerank(query: str, chunks: list["Chunk"], top_k: int) -> list["Chunk"]:
    """Rerank chunks using Voyage rerank-2.5. Returns top_k in relevance order."""
    if not chunks:
        return []

    config = get_config()
    client = _get_client()
    documents = [c.content for c in chunks]

    result = await asyncio.to_thread(
        client.rerank,
        query,
        documents,
        model=config.rerank_model,
        top_k=min(top_k, len(chunks)),
    )

    reranked = []
    for r in result.results:
        chunk = chunks[r.index]
        chunk.rerank_score = r.relevance_score
        reranked.append(chunk)
    return reranked
