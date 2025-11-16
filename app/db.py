"""
Database utilities for request logging

Stores request metadata in SQLite for tracing and debugging.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path("./data/api_logs.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_database() -> None:
    """Initialize the SQLite database and create tables if they don't exist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    provider TEXT,
                    model TEXT,
                    response_time_ms REAL,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    total_tokens INTEGER,
                    error_type TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on request_id for fast lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_id ON requests(request_id)
            """)
            
            # Create index on timestamp for time-based queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON requests(timestamp)
            """)
            
            # Create index on endpoint for endpoint-based queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_endpoint ON requests(endpoint)
            """)
            
            conn.commit()
            logger.info(f"Database initialized at {DB_PATH}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@contextmanager
def get_db_connection():
    """Get a database connection with proper error handling."""
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def log_request(
    request_id: str,
    endpoint: str,
    method: str = "POST",
    status_code: Optional[int] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    response_time_ms: Optional[float] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    error_type: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Log a request to the database.
    
    Args:
        request_id: Unique request identifier
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        status_code: HTTP status code
        provider: AI provider used (if applicable)
        model: Model used (if applicable)
        response_time_ms: Response time in milliseconds
        prompt_tokens: Number of prompt tokens (if applicable)
        completion_tokens: Number of completion tokens (if applicable)
        total_tokens: Total tokens used (if applicable)
        error_type: Type of error if request failed
        error_message: Error message if request failed
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requests (
                    request_id, timestamp, endpoint, method, status_code,
                    provider, model, response_time_ms,
                    prompt_tokens, completion_tokens, total_tokens,
                    error_type, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_id, timestamp, endpoint, method, status_code,
                provider, model, response_time_ms,
                prompt_tokens, completion_tokens, total_tokens,
                error_type, error_message
            ))
            conn.commit()
            
    except sqlite3.IntegrityError:
        # Request ID already exists (shouldn't happen, but handle gracefully)
        logger.warning(f"Request ID {request_id} already exists in database")
    except Exception as e:
        # Don't fail the request if logging fails
        logger.error(f"Failed to log request {request_id}: {e}")


def get_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a request by its request ID.
    
    Args:
        request_id: Request identifier
        
    Returns:
        Dictionary with request data or None if not found
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM requests WHERE request_id = ?
            """, (request_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    except Exception as e:
        logger.error(f"Failed to retrieve request {request_id}: {e}")
        return None


def get_recent_requests(limit: int = 100) -> list[Dict[str, Any]]:
    """
    Get recent requests, ordered by timestamp descending.
    
    Args:
        limit: Maximum number of requests to return
        
    Returns:
        List of request dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM requests 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except Exception as e:
        logger.error(f"Failed to retrieve recent requests: {e}")
        return []

