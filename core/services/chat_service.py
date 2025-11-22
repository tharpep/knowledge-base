"""
Chat Service - Shared business logic for chat functionality

This service encapsulates the common chat logic used by both CLI and API,
including RAG retrieval, prompt formatting, and message preparation.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from core.config import AppConfig
from core.prompts import get_prompt, format_prompt

logger = logging.getLogger(__name__)


@dataclass
class ChatMessageResult:
    """Result of preparing a chat message with RAG context."""
    formatted_message: str
    rag_results: List[Tuple[str, float]]
    rag_context_text: Optional[str] = None


class ChatService:
    """
    Shared chat service for CLI and API.
    
    Handles RAG retrieval, prompt formatting, and message preparation
    in a consistent way across both interfaces.
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize chat service.
        
        Args:
            config: Application configuration
        """
        self.config = config
    
    def prepare_chat_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        use_rag: Optional[bool] = None,
        rag_top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        system_prompt: Optional[str] = None,
        rag_prompt_template: Optional[str] = None
    ) -> ChatMessageResult:
        """
        Prepare a chat message with optional RAG context.
        
        This method:
        1. Retrieves RAG context if enabled
        2. Formats the user message with RAG context (if available)
        3. Returns the formatted message and RAG results
        
        Args:
            user_message: The user's message/query
            conversation_history: List of previous messages (role/content dicts)
            use_rag: Whether to use RAG (overrides config if provided)
            rag_top_k: Number of documents to retrieve (overrides config if provided)
            similarity_threshold: Minimum similarity score (overrides config if provided)
            system_prompt: Custom system prompt (overrides default if provided)
            rag_prompt_template: Custom RAG prompt template (overrides default if provided)
        
        Returns:
            ChatMessageResult with formatted message and RAG results
        """
        # Use provided values or fall back to config
        use_rag = use_rag if use_rag is not None else self.config.chat_rag_enabled
        rag_top_k = rag_top_k if rag_top_k is not None else self.config.chat_rag_top_k
        similarity_threshold = (
            similarity_threshold 
            if similarity_threshold is not None 
            else self.config.chat_rag_similarity_threshold
        )
        
        rag_results: List[Tuple[str, float]] = []
        rag_context_text: Optional[str] = None
        
        # Retrieve RAG context if enabled
        if use_rag:
            rag_results, rag_context_text = self._retrieve_rag_context(
                query=user_message,
                top_k=rag_top_k,
                similarity_threshold=similarity_threshold
            )
        
        # Format the user message with RAG context if available
        formatted_message = self._format_user_message(
            user_message=user_message,
            rag_context_text=rag_context_text,
            system_prompt=system_prompt,
            rag_prompt_template=rag_prompt_template
        )
        
        return ChatMessageResult(
            formatted_message=formatted_message,
            rag_results=rag_results,
            rag_context_text=rag_context_text
        )
    
    def _retrieve_rag_context(
        self,
        query: str,
        top_k: int,
        similarity_threshold: float
    ) -> Tuple[List[Tuple[str, float]], Optional[str]]:
        """
        Retrieve RAG context for a query.
        
        Args:
            query: User query/message
            top_k: Number of documents to retrieve
            similarity_threshold: Minimum similarity score
        
        Returns:
            Tuple of (rag_results, rag_context_text)
            rag_results: List of (document_text, similarity_score) tuples
            rag_context_text: Combined context text, or None if no results
        """
        try:
            from rag.rag_setup import BasicRAG
            
            rag = BasicRAG()
            
            # Log RAG usage if logging enabled
            if self.config.log_output:
                logger.info(
                    f"Chat RAG - Enabled: True, Top-K: {top_k}, "
                    f"Threshold: {similarity_threshold}"
                )
            
            # Retrieve RAG context
            rag_results = rag.get_context_for_chat(
                query=query,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # Format context text if results found
            if rag_results:
                rag_context_text = "\n\n".join([doc for doc, _ in rag_results])
                if self.config.log_output:
                    logger.info(
                        f"Chat RAG - Using {len(rag_results)} documents as context"
                    )
            else:
                rag_context_text = None
                if self.config.log_output:
                    logger.info(
                        "Chat RAG - No documents retrieved (all below threshold)"
                    )
            
            return rag_results, rag_context_text
            
        except Exception as e:
            # Log error but continue without RAG
            logger.warning(
                f"RAG retrieval failed, continuing without RAG context: {e}",
                exc_info=self.config.log_output
            )
            return [], None
    
    def _format_user_message(
        self,
        user_message: str,
        rag_context_text: Optional[str],
        system_prompt: Optional[str] = None,
        rag_prompt_template: Optional[str] = None
    ) -> str:
        """
        Format user message with optional RAG context.
        
        Args:
            user_message: The user's message
            rag_context_text: RAG context text (if available)
            system_prompt: Custom system prompt (overrides default)
            rag_prompt_template: Custom RAG prompt template (overrides default)
        
        Returns:
            Formatted message string ready for LLM
        """
        if rag_context_text:
            # Format with RAG context clearly separated
            if rag_prompt_template:
                template = rag_prompt_template
            else:
                template = get_prompt("llm_with_rag")
            
            return format_prompt(
                template,
                rag_context=rag_context_text,
                user_message=user_message
            )
        else:
            # No RAG - use regular format
            if system_prompt:
                system = system_prompt
            else:
                system = get_prompt("llm")
            
            return f"{system}\n\nUser: {user_message}"

