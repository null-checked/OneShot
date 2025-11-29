"""
This module is the main entry point for the FastAPI application.
It defines the API endpoints for the Code Arena.
"""

import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any

from config import settings
from orchestrator import ArenaOrchestrator
from llm_client import create_llm_client

app = FastAPI(
    title="Multi-Agent Competitive Code Arena",
    description="A multi-agent system where LLM agents compete to solve programming problems.",
    version="0.1.0",
)

# --- Data Models ---
class ArenaRequest(BaseModel):
    """Request model for the arena endpoints."""
    problem: str
    model: str | None = None
    num_agents: int | None = None

# --- Health and Info Endpoints ---

@app.get("/api/health", tags=["Status"])
def health_check():
    """Checks if the configured LLM provider is available."""
    llm_client = create_llm_client()
    is_available = llm_client.is_available()
    return {"status": "ok" if is_available else "error", "provider": settings.LLM_PROVIDER}

@app.get("/api/models", tags=["Status"])
def get_models():
    """Gets a list of available models from the configured LLM provider."""
    llm_client = create_llm_client()
    models = llm_client.get_models()
    return {"models": models}
    
# --- Arena Endpoints ---

@app.post("/api/arena", tags=["Arena"])
async def run_arena_sync(request: ArenaRequest):
    """
    Runs the full arena workflow synchronously and returns the final result.
    This is useful for testing or for clients that don't support WebSockets.
    """
    loop = asyncio.get_event_loop()
    orchestrator = ArenaOrchestrator(settings)
    
    # Run the synchronous orchestrator in a thread to avoid blocking
    results = await loop.run_in_executor(None, orchestrator.run, request.problem)
    
    if "error" in results:
        return JSONResponse(status_code=500, content=results)
    return results

@app.websocket("/ws/arena")
async def run_arena_ws(websocket: WebSocket):
    """
    Runs the full arena workflow with real-time updates over a WebSocket connection.
    """
    await websocket.accept()
    
    try:
        initial_data = await websocket.receive_text()
        request = ArenaRequest.model_validate_json(initial_data)

        async def event_callback(event_type: str, data: Any):
            """Async callback to send events over the WebSocket."""
            await websocket.send_json({"type": event_type, "data": data})

        orchestrator = ArenaOrchestrator(settings, event_callback)
        
        loop = asyncio.get_event_loop()
        # Run the synchronous 'run' method in a thread pool executor
        await loop.run_in_executor(None, orchestrator.run, request.problem)
        
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket.")
    except Exception as e:
        # Send a final error message before closing
        await websocket.send_json({"type": "error", "data": {"message": f"An unexpected error occurred: {e}"}})
    finally:
        if websocket.client_state != 2: # STATE.DISCONNECTED
             await websocket.close()


# --- Main Entry Point ---

def main():
    """Starts the FastAPI server using uvicorn."""
    print(f"Starting server on {settings.HOST}:{settings.PORT}")
    print(f"Using LLM Provider: {settings.LLM_PROVIDER}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )

if __name__ == "__main__":
    main()