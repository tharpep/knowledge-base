"""FastAPI startup - Personal AI Assistant API"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from llm.gateway import AIGateway

from .routes import health, llm, query, ingest
from .db import init_database, log_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global gateway instance
gateway: AIGateway = None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Get request ID from header or generate one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            # Generate request ID if not provided
            import uuid
            request_id = f"req_{uuid.uuid4().hex[:12]}"
        
        # Start timing
        start_time = time.time()
        
        # Process request
        response = None
        status_code = 500
        error_type = None
        error_message = None
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            error_type = type(e).__name__
            error_message = str(e)
            raise
        finally:
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log request (non-blocking)
            try:
                log_request(
                    request_id=request_id,
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    response_time_ms=response_time_ms,
                    error_type=error_type,
                    error_message=error_message
                )
            except Exception as e:
                logger.error(f"Failed to log request: {e}")
        
        # Add request ID to response header
        if response:
            response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global gateway
    
    # Startup
    logger.info("Starting Personal AI Assistant API")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue anyway - logging is non-critical
    
    # Initialize gateway
    gateway = AIGateway()
    logger.info("AI Gateway initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Personal AI Assistant API")
    if gateway:
        try:
            await gateway.__aexit__(None, None, None)
        except Exception:
            pass  # Gateway might not have been entered


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Personal AI Assistant API",
        description="OpenAI-compatible API for personal AI assistant",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Include routes
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(llm.router, prefix="/v1", tags=["llm"])
    app.include_router(query.router, prefix="/v1", tags=["rag"])
    app.include_router(ingest.router, prefix="/v1", tags=["ingest"])
    
    return app


app = create_app()
