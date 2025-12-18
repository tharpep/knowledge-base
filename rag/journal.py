"""
Journal Manager for Project Mnemosyne
Handles chat history storage and retrieval in Qdrant (Tier 2: The Journal).
"""

import logging
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel

from rag.vector_store import VectorStore
from core.config import get_config
from core.model_registry import get_configured_model

logger = logging.getLogger(__name__)

# Collection name for journal entries
JOURNAL_COLLECTION = "myai_journal"


class JournalEntry(BaseModel):
    """
    Schema for a journal entry stored in Qdrant payload.
    
    Attributes:
        role: Message role ('user' or 'assistant')
        content: Full message content
        session_id: Unique session identifier
        timestamp: ISO format timestamp
    """
    role: Literal["user", "assistant"]
    content: str
    session_id: str
    timestamp: str


class JournalManager:
    """
    Manages chat history storage and retrieval.
    
    The Journal stores full message content in Qdrant's payload,
    enabling semantic search over conversation history.
    """
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize the Journal Manager.
        
        Args:
            vector_store: Optional VectorStore instance. If not provided,
                         creates one using config settings.
        """
        self.config = get_config()
        
        # Use provided vector store or create new one
        if vector_store is not None:
            self.vector_store = vector_store
        else:
            self.vector_store = VectorStore(
                use_persistent=self.config.rag_use_persistent,
                qdrant_host=self.config.qdrant_host,
                qdrant_port=self.config.qdrant_port
            )
        
        # Get embedding model info from registry
        self.model_info = get_configured_model("journal")
        self.embedding_dim = self.model_info.dimension or 384
        
        # Embedding model will be initialized lazily
        self._embedder = None
        
        # Ensure collection exists
        self._setup_collection()
        
        logger.info(f"JournalManager initialized with model: {self.model_info.name}")
    
    def _setup_collection(self) -> None:
        """Create journal collection if it doesn't exist."""
        self.vector_store.setup_collection(
            collection_name=JOURNAL_COLLECTION,
            embedding_dim=self.embedding_dim
        )
    
    @property
    def embedder(self):
        """Lazy-load the embedding model."""
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.model_info.name)
            logger.info(f"Loaded embedding model: {self.model_info.name}")
        return self._embedder
    
    # =========================================================================
    # Storage Methods (Phase 2B)
    # =========================================================================
    
    async def add_entry(
        self,
        role: Literal["user", "assistant"],
        content: str,
        session_id: str
    ) -> bool:
        """
        Add a chat message to the journal.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Full message content
            session_id: Session identifier
            
        Returns:
            True if entry was added successfully
        """
        # TODO: Implement in Phase 2B
        # 1. Generate embedding
        # 2. Create JournalEntry with timestamp
        # 3. Upsert to Qdrant
        raise NotImplementedError("Phase 2B: add_entry")
    
    async def generate_session_name(self, messages: list[dict]) -> str:
        """
        Generate a descriptive name for a session using LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Generated session name
        """
        # TODO: Implement in Phase 2B
        raise NotImplementedError("Phase 2B: generate_session_name")
    
    # =========================================================================
    # Retrieval Methods (Phase 2C)
    # =========================================================================
    
    async def get_recent_context(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> list[JournalEntry]:
        """
        Retrieve relevant chat history for context.
        
        Args:
            query: Search query for semantic matching
            session_id: Optional session filter
            limit: Maximum entries to return
            
        Returns:
            List of relevant JournalEntry objects
        """
        # TODO: Implement in Phase 2C
        raise NotImplementedError("Phase 2C: get_recent_context")
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete all entries for a session.
        
        Args:
            session_id: Session identifier to delete
            
        Returns:
            True if deletion was successful
        """
        # TODO: Implement in Phase 2C
        raise NotImplementedError("Phase 2C: delete_session")
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_stats(self) -> dict:
        """Get journal collection statistics."""
        return self.vector_store.get_collection_stats(JOURNAL_COLLECTION)
