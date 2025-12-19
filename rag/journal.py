"""
Journal Manager for Project Mnemosyne
Handles chat history storage and retrieval in Qdrant (Tier 2: The Journal).
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel
from qdrant_client.models import PointStruct

from rag.vector_store import VectorStore
from core.config import get_config
from core.model_registry import get_configured_model
from core.session_store import get_session_store

logger = logging.getLogger(__name__)


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
                use_persistent=self.config.storage_use_persistent,
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
            collection_name=self.config.journal_collection_name,
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
        """
        try:
            # Generate embedding for the content
            embedding = self.embedder.encode(content).tolist()
            
            # Create entry with timestamp
            entry = JournalEntry(
                role=role,
                content=content,
                session_id=session_id,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Create point for Qdrant
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=entry.model_dump()
            )
            
            # Upsert to collection
            added = self.vector_store.add_points(self.config.journal_collection_name, [point])
            
            if added > 0:
                logger.debug(f"Added journal entry: {role} in session {session_id}")
                # Sync with SQLite session store
                try:
                    session_store = get_session_store()
                    session_store.upsert_session(session_id)
                    session_store.increment_message_count(session_id)
                except Exception as e:
                    logger.warning(f"Failed to sync session to SQLite: {e}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to add journal entry: {e}")
            return False
    
    async def generate_session_name(self, messages: list[dict]) -> str:
        """
        Generate a descriptive name for a session using LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Generated session name (short, descriptive title)
        """
        from llm.gateway import AIGateway
        
        # Build a summary of the conversation for naming
        conversation_summary = "\n".join([
            f"{m.get('role', 'unknown')}: {m.get('content', '')[:200]}"
            for m in messages[:5]  # Use first 5 messages max
        ])
        
        prompt = f"""Generate a short, descriptive title (3-6 words) for this conversation. 
Return ONLY the title, no quotes or explanation.

Conversation:
{conversation_summary}

Title:"""
        
        try:
            gateway = AIGateway()
            response = gateway.chat(prompt)
            
            # Clean up response - take first line, strip quotes/whitespace
            session_name = response.strip().split('\n')[0].strip('"\'')
            
            # Limit length
            if len(session_name) > 50:
                session_name = session_name[:47] + "..."
            
            return session_name
            
        except Exception as e:
            logger.warning(f"Failed to generate session name via LLM: {e}")
            # Fallback to timestamp-based name
            return f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    
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
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        try:
            # Generate query embedding
            query_vector = self.embedder.encode(query).tolist()
            
            # Build optional filter for session_id
            query_filter = None
            if session_id:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=session_id)
                        )
                    ]
                )
            
            # Search with filter
            results = self.vector_store.client.query_points(
                collection_name=self.config.journal_collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit
            ).points
            
            # Convert to JournalEntry objects
            entries = []
            for hit in results:
                try:
                    entry = JournalEntry(**hit.payload)
                    entries.append(entry)
                except Exception as e:
                    logger.warning(f"Failed to parse journal entry: {e}")
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to retrieve journal context: {e}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete all entries for a session.
        
        Args:
            session_id: Session identifier to delete
            
        Returns:
            True if deletion was successful
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        try:
            # Delete by payload filter
            self.vector_store.client.delete(
                collection_name=self.config.journal_collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=session_id)
                        )
                    ]
                )
            )
            
            # Also delete from SQLite session store
            try:
                session_store = get_session_store()
                session_store.delete_session(session_id)
            except Exception as e:
                logger.warning(f"Failed to delete session from SQLite: {e}")
            
            logger.info(f"Deleted journal entries for session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def list_sessions(self, limit: int = 100) -> list[dict]:
        """
        List all unique session IDs in the journal.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of dicts with session_id and entry_count
        """
        try:
            # Scroll through all points to collect unique session_ids
            # Note: This is acceptable for personal use with limited chat history
            all_points, _ = self.vector_store.client.scroll(
                collection_name=self.config.journal_collection_name,
                limit=10000,  # Reasonable upper bound for personal use
                with_payload=["session_id", "timestamp"]
            )
            
            # Aggregate by session_id
            sessions = {}
            for point in all_points:
                session_id = point.payload.get("session_id")
                if session_id:
                    if session_id not in sessions:
                        sessions[session_id] = {
                            "session_id": session_id,
                            "entry_count": 0,
                            "last_activity": None
                        }
                    sessions[session_id]["entry_count"] += 1
                    
                    # Track most recent timestamp
                    timestamp = point.payload.get("timestamp")
                    if timestamp:
                        if sessions[session_id]["last_activity"] is None or timestamp > sessions[session_id]["last_activity"]:
                            sessions[session_id]["last_activity"] = timestamp
            
            # Sort by last_activity descending, return as list
            sorted_sessions = sorted(
                sessions.values(),
                key=lambda s: s["last_activity"] or "",
                reverse=True
            )[:limit]
            
            return sorted_sessions
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def clear_all(self) -> bool:
        """
        Clear all entries from the journal.
        
        Returns:
            True if successful
        """
        try:
            # Recreate the collection (fastest way to clear)
            self.vector_store.client.delete_collection(self.config.journal_collection_name)
            self._setup_collection()
            logger.info("Cleared all journal entries")
            return True
        except Exception as e:
            logger.error(f"Failed to clear journal: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get journal collection statistics."""
        return self.vector_store.get_collection_stats(self.config.journal_collection_name)
