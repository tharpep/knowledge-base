"""Health check endpoint"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "personal-ai-assistant-api",
        "version": "0.1.0"
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check including LLM gateway status."""
    from ..main import gateway
    
    try:
        gateway_health = await gateway.health_check()
        return {
            "status": "healthy" if gateway_health["ok"] else "degraded",
            "service": "personal-ai-assistant-api", 
            "version": "0.1.0",
            "components": {
                "llm_gateway": gateway_health
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "personal-ai-assistant-api",
            "version": "0.1.0",
            "error": str(e)
        }
