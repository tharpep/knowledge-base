"""
Session Store for Journal Sessions
Persists session metadata in SQLite for durable names and fast lookups.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path("./data/sessions.db")


class SessionStore:
    """
    Manages session metadata in SQLite.
    
    Sessions are identified by session_id (UUID) which matches
    the session_id stored in Qdrant payloads.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize session store."""
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Create sessions table if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_activity 
                ON sessions(last_activity DESC)
            """)
            conn.commit()
            logger.info(f"Session store initialized at {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Session store error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def upsert_session(self, session_id: str, name: Optional[str] = None) -> None:
        """
        Create or update a session.
        
        Args:
            session_id: Unique session identifier
            name: Optional friendly name for the session
        """
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if session exists
            cursor.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update last_activity
                cursor.execute("""
                    UPDATE sessions SET last_activity = ? WHERE session_id = ?
                """, (now, session_id))
                if name:
                    cursor.execute("""
                        UPDATE sessions SET name = ? WHERE session_id = ?
                    """, (name, session_id))
            else:
                # Insert new session
                cursor.execute("""
                    INSERT INTO sessions (session_id, name, created_at, last_activity, message_count)
                    VALUES (?, ?, ?, ?, 0)
                """, (session_id, name, now, now))
            
            conn.commit()
    
    def increment_message_count(self, session_id: str) -> None:
        """Increment the message count for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions SET message_count = message_count + 1 
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
    
    def set_session_name(self, session_id: str, name: str) -> None:
        """Set or update the friendly name for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions SET name = ? WHERE session_id = ?
            """, (name, session_id))
            conn.commit()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a single session by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List sessions ordered by last activity (most recent first)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                ORDER BY last_activity DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0


# Singleton instance
_session_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    """Get the global SessionStore instance."""
    global _session_store
    if _session_store is None:
        _session_store = SessionStore()
    return _session_store
