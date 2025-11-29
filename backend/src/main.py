import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager

from src.api.v1.router import routers
from src.settings import settings

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Multi-Agent Software Factory",
        "version": "1.0.0",
        "description": "AI-powered software project generator",
        "endpoints": {
            "/build": "POST - Generate a software project from a prompt",
            "/download/{project_name}": "GET - Download generated project as zip",
            "/projects": "GET - List all generated projects",
            "/project/{project_name}/details": "GET - Get detailed project information",
            "/health": "GET - Health check"
        },
        "workflow_steps": [
            "1. Analyze user prompt",
            "2. Plan research",
            "3. Conduct market research",
            "4. Plan implementation",
            "5. Research documentation",
            "6. Implement code",
            "7. Review code",
            "8. Test code",
            "9. Write documentation"
        ]
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Modern replacement for @app.on_event("startup").
    """
    logger.info("🚀 Starting up application...")
    
    # Initialize DB connections or ML models here
    yield   
    # Clean up resources here
    logger.info("🛑 Shutting down application...")

def create_app() -> FastAPI:  # pragma: no cover
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        lifespan=lifespan,
    )
    logger.info("Adding CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        # Use your actual frontend URL(s)
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    logger.info("Including routers...")
    app.include_router(routers)
    return app


app = create_app()

def start():  # pragma: no cover
    uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=settings.RELOAD)


if __name__ == "__main__":  # pragma: no cover
    start()
