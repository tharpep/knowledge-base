"""Memory Management API routes - Journal session management"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/memory/sessions")
async def list_sessions(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum sessions to return")
):
    """
    List all chat sessions in the journal.
    
    Returns:
        Dictionary with:
        - sessions: List of session metadata (session_id, name, message_count, last_activity)
        - total: Total number of sessions
    """
    from core.session_store import get_session_store
    
    try:
        session_store = get_session_store()
        sessions = session_store.list_sessions(limit=limit)
        
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.delete("/memory/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete all journal entries for a specific session.
    
    Args:
        session_id: The session identifier to delete
        
    Returns:
        Confirmation of deletion
    """
    from rag.rag_setup import get_rag
    
    try:
        context_engine = get_rag()
        
        if not context_engine._journal_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Journal is not initialized"
            )
        
        success = await context_engine._journal_manager.delete_session(session_id)
        
        if success:
            return {
                "status": "deleted",
                "session_id": session_id
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete session"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/memory/stats")
async def get_memory_stats():
    """
    Get statistics about journal memory.
    
    Returns:
        Dictionary with journal statistics
    """
    from rag.rag_setup import get_rag
    
    try:
        context_engine = get_rag()
        
        if not context_engine._journal_manager:
            return {
                "initialized": False,
                "message": "Journal is not initialized"
            }
        
        stats = context_engine._journal_manager.get_stats()
        
        return {
            "initialized": True,
            **stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get memory stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
