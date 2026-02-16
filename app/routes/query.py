"""KB query routes — search kb_chunks via hybrid retrieval."""

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.database import get_pool
from rag.retriever import retrieve

logger = logging.getLogger(__name__)

router = APIRouter()


class KBQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    candidates: Optional[int] = None
    threshold: Optional[float] = None
    expand_query: bool = False


class KBChunkResult(BaseModel):
    content: str
    filename: str
    drive_file_id: str
    chunk_index: int
    rerank_score: float
    dense_score: float
    rrf_score: float


class KBQueryResponse(BaseModel):
    results: list[KBChunkResult]
    count: int
    query: str
    expanded_query: Optional[str] = None


@router.post("/kb/query", response_model=KBQueryResponse)
async def query_kb(body: KBQueryRequest):
    """Search kb_chunks using hybrid retrieval (dense + FTS → RRF → Voyage rerank)."""
    query = body.query.strip()
    if not query:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty")

    try:
        expanded_query = None

        if body.expand_query:
            from rag.query_processor import QueryProcessor
            qp = QueryProcessor()
            expanded_query = await asyncio.to_thread(qp.expand, query)
            query = expanded_query

        chunks = await retrieve(
            query=query,
            top_k=body.top_k,
            candidates=body.candidates,
            threshold=body.threshold,
        )

        return KBQueryResponse(
            results=[
                KBChunkResult(
                    content=c.content,
                    filename=c.filename,
                    drive_file_id=c.drive_file_id,
                    chunk_index=c.chunk_index,
                    rerank_score=c.rerank_score,
                    dense_score=c.dense_score,
                    rrf_score=c.rrf_score,
                )
                for c in chunks
            ],
            count=len(chunks),
            query=body.query,
            expanded_query=expanded_query,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"KB query failed: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/kb/stats")
async def kb_stats():
    """Return total chunk count and distinct file count from kb_chunks."""
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT COUNT(*) AS chunk_count,
                       COUNT(DISTINCT drive_file_id) AS file_count
                FROM kb_chunks
                """
            )
        return {
            "chunk_count": row["chunk_count"],
            "file_count": row["file_count"],
        }
    except Exception as e:
        logger.error(f"Failed to get KB stats: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
