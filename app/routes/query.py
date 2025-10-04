"""RAG Query API routes - Main query interface with RAG"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class QueryRequest(BaseModel):
    """RAG query request."""
    question: str = Field(..., description="Question to answer using RAG")
    context_limit: Optional[int] = Field(None, ge=1, le=20, description="Number of documents to retrieve for context")
    summarize: Optional[bool] = Field(False, description="Whether to summarize the response")


class QueryResponse(BaseModel):
    """RAG query response."""
    answer: str = Field(..., description="Generated answer")
    citations: List[str] = Field(default_factory=list, description="Source document citations")
    context_docs: List[str] = Field(default_factory=list, description="Retrieved context documents")
    context_scores: List[float] = Field(default_factory=list, description="Relevance scores for context")
    model_used: str = Field(..., description="Model used for generation")
    provider_used: str = Field(..., description="AI provider used")


@router.post("/query", response_model=QueryResponse)
async def rag_query(request: QueryRequest) -> QueryResponse:
    """Main RAG query endpoint - answers questions using retrieved context."""
    from ..main import gateway
    from rag.rag_setup import BasicRAG
    
    try:
        # Initialize RAG system
        rag = BasicRAG()
        
        # Query with RAG
        answer, context_docs, context_scores = rag.query(
            question=request.question,
            context_limit=request.context_limit
        )
        
        # Get provider info
        providers = gateway.get_available_providers()
        provider_used = providers[0] if providers else "unknown"
        model_used = gateway.rag_config.model_name
        
        # Generate citations (simple for now)
        citations = [f"Document {i+1}" for i in range(len(context_docs))]
        
        return QueryResponse(
            answer=answer,
            citations=citations,
            context_docs=context_docs,
            context_scores=context_scores,
            model_used=model_used,
            provider_used=provider_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/ingest")
async def ingest_documents(folder_path: str = "./data/documents") -> Dict[str, Any]:
    """Ingest documents into the RAG system."""
    from rag.rag_setup import BasicRAG
    from rag.document_ingester import DocumentIngester
    
    try:
        # Initialize RAG system
        rag = BasicRAG()
        
        # Initialize ingester
        ingester = DocumentIngester(rag)
        
        # Ingest documents
        result = ingester.ingest_folder(folder_path)
        
        return {
            "success": result["success"],
            "processed": result["processed"],
            "failed": result["failed"],
            "files": result["files"],
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")


@router.get("/stats")
async def get_rag_stats() -> Dict[str, Any]:
    """Get RAG system statistics."""
    from rag.rag_setup import BasicRAG
    
    try:
        rag = BasicRAG()
        stats = rag.get_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
