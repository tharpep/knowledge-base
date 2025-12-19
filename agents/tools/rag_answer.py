"""
RAG Answer Tool

Retrieves and cites answers from the ingested document corpus (RAG knowledge base).
"""

import time
from typing import Any, Dict, Optional
from ..base_tool import BaseTool, ToolResult, ToolSchema
import logging

logger = logging.getLogger(__name__)


class RAGAnswerTool(BaseTool):
    """
    Tool for answering questions using RAG (Retrieval Augmented Generation).
    
    Searches the ingested document corpus and returns answers with citations.
    """
    
    def __init__(self):
        """Initialize RAG Answer tool."""
        self._rag = None  # Lazy initialization
    
    def _get_rag(self):
        """Lazy load RAG system."""
        if self._rag is None:
            from rag.rag_setup import get_rag
            self._rag = get_rag()
        return self._rag
    
    @property
    def name(self) -> str:
        """Tool identifier."""
        return "rag_answer"
    
    @property
    def description(self) -> str:
        """Tool description."""
        return "Retrieve and cite answers from the ingested document corpus (RAG knowledge base). Returns answers with source citations."
    
    @property
    def read_only(self) -> bool:
        """RAG answer is read-only."""
        return True
    
    @property
    def idempotent(self) -> bool:
        """RAG answer is idempotent."""
        return True
    
    def get_schema(self) -> ToolSchema:
        """Get tool schema."""
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Question to answer using RAG"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of documents to retrieve (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters for document search",
                        "additionalProperties": True
                    }
                },
                "required": ["query"]
            },
            returns={
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "Generated answer"
                    },
                    "answer_snippets": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "chunk_id": {"type": "string"},
                                "doc_uri": {"type": "string"},
                                "text": {"type": "string"},
                                "score": {"type": "number"}
                            }
                        }
                    },
                    "citations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Source document URIs"
                    }
                },
                "required": ["answer", "citations"]
            },
            read_only=self.read_only,
            idempotent=self.idempotent
        )
    
    async def execute(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """
        Execute RAG query.
        
        Args:
            query: Question to answer
            top_k: Number of documents to retrieve
            filters: Optional filters for document search
            
        Returns:
            ToolResult with answer and citations
        """
        start_time = time.time()
        
        try:
            # Validate query
            if not query or not query.strip():
                return ToolResult(
                    success=False,
                    error="Query cannot be empty"
                )
            
            # Get RAG system
            rag = self._get_rag()
            
            # Execute RAG query
            answer, context_docs, context_scores = rag.query(
                question=query,
                context_limit=top_k
            )
            
            # Build answer snippets
            answer_snippets = []
            citations = []
            
            for i, (doc, score) in enumerate(zip(context_docs, context_scores)):
                snippet = {
                    "chunk_id": f"chunk_{i}",
                    "doc_uri": f"doc_{i}",
                    "text": doc[:200] if len(doc) > 200 else doc,  # Truncate long docs
                    "score": float(score) if isinstance(score, (int, float)) else 0.0
                }
                answer_snippets.append(snippet)
                citations.append(f"Document {i+1}")
            
            execution_time = (time.time() - start_time) * 1000
            
            return ToolResult(
                success=True,
                data={
                    "answer": answer,
                    "answer_snippets": answer_snippets,
                    "citations": citations
                },
                execution_time_ms=execution_time,
                citations=citations
            )
            
        except Exception as e:
            logger.error(f"RAG answer tool execution failed: {e}", exc_info=True)
            return ToolResult(
                success=False,
                error=f"RAG query failed: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

