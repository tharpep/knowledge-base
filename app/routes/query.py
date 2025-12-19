"""
RAG Statistics API routes

This module provides the stats endpoint:
- Library statistics: /v1/stats (Library system statistics)
"""

import uuid
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


# ===== Library Statistics Endpoint =====

@router.get("/stats")
async def get_library_stats() -> Dict[str, Any]:
    """Get Library system statistics."""
    from rag.rag_setup import get_rag
    
    # Generate request ID for tracing
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    try:
        engine = get_rag()
        stats = engine.get_stats()
        stats["request_id"] = request_id
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "message": f"Failed to get stats: {str(e)}",
                    "type": "internal_error",
                    "code": "server_error"
                },
                "request_id": request_id
            }
        )
