import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from agent.api.routes import chat, health
from agent.api.services.agent_service import get_agent_service
from agent.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.
    """
    logger.info("Starting up AGENTIC_MCP API...")
    service = get_agent_service()
    try:
        await service.initialize_agent()
        logger.info("Agent initialized successfully on startup")
    except Exception as e:
        logger.warning(f"Agent initialization deferred: {e}")
    
    yield
    
    logger.info("Shutting down AGENTIC_MCP API...")
    await service.shutdown()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    """
    app = FastAPI(
        title="AGENTIC_MCP API",
        description="AI Assistant API for IMT Mines Alès using LangGraph and MCP",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router)
    app.include_router(chat.router)

    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": "AGENTIC_MCP API",
            "description": "AI Assistant for IMT Mines Alès",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "agent.main:app",
        host="0.0.0.0",
        port=8000
    )
