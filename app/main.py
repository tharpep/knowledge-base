"""FastAPI startup - Personal AI Assistant API"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from llm.gateway import AIGateway

from .routes import health, llm, query, ingest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global gateway instance
gateway: AIGateway = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application lifecycle."""
    global gateway
    
    # Startup
    logger.info("Starting Personal AI Assistant API")
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
    
    # Include routes
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(llm.router, prefix="/v1", tags=["llm"])
    app.include_router(query.router, prefix="/v1", tags=["rag"])
    app.include_router(ingest.router, prefix="/v1", tags=["ingest"])
    
    return app


app = create_app()
