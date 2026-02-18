"""Health check endpoints."""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "kb-service",
        "version": "0.1.0",
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check including system components."""
    from ..main import gateway
    from core.database import get_pool
    from core.config import get_config

    config = get_config()
    components: Dict[str, Any] = {}
    overall_status = "healthy"

    # LLM Gateway
    try:
        if gateway is None:
            components["llm_gateway"] = {"status": "unhealthy", "error": "Not initialized"}
            overall_status = "unhealthy"
        else:
            providers = gateway.get_available_providers()
            components["llm_gateway"] = {
                "status": "healthy" if providers else "degraded",
                "providers": providers,
            }
            if not providers:
                overall_status = "degraded"
    except Exception as e:
        components["llm_gateway"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "unhealthy"

    # PostgreSQL
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        components["database"] = {"status": "healthy"}
    except Exception as e:
        components["database"] = {"status": "unhealthy", "error": str(e)}
        if overall_status == "healthy":
            overall_status = "degraded"

    # KB (quick chunk count)
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM kb_chunks")
        components["kb"] = {"status": "healthy", "chunks": count}
    except Exception as e:
        components["kb"] = {"status": "unhealthy", "error": str(e)}
        if overall_status == "healthy":
            overall_status = "degraded"

    return {
        "status": overall_status,
        "service": "kb-service",
        "version": "0.1.0",
        "components": components,
    }
