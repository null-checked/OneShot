"""
WebSocket handler for the Multi-Agent Software Factory.
Replaces REST endpoints with real-time WebSocket communication.
"""

from fastapi import WebSocket, WebSocketDisconnect
from pathlib import Path
import concurrent.futures
import json
import asyncio
from typing import Dict, Any

from src.core.pipeline import MultiAgentPipeline
from src.settings import get_pipeline_agent, fs_writer, settings
from src.api.v1.helpers import create_project_zip


class WebSocketManager:
    """Manages WebSocket connections and message routing."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, client_id: str, message: dict):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def send_progress(self, client_id: str, step: int, message: str, data: Any = None):
        """Send progress update to client."""
        await self.send_message(client_id, {
            "type": "progress",
            "step": step,
            "message": message,
            "data": data
        })

    async def send_error(self, client_id: str, error: str):
        """Send error message to client."""
        await self.send_message(client_id, {
            "type": "error",
            "error": error
        })

    async def send_complete(self, client_id: str, data: dict):
        """Send completion message to client."""
        await self.send_message(client_id, {
            "type": "complete",
            "data": data
        })


manager = WebSocketManager()


async def handle_build_project(websocket: WebSocket, client_id: str, data: dict):
    """
    Handle project build request via WebSocket.
    Sends real-time progress updates for each step.
    """
    prompt = data.get("prompt")
    if not prompt:
        await manager.send_error(client_id, "Missing 'prompt' field")
        return

    try:
        await manager.send_progress(client_id, 0, "Starting project generation...")

        # Get pipeline
        pipeline = get_pipeline_agent()

        # Send initial progress
        await manager.send_progress(client_id, 1, "📝 Step 1: Analyzing user prompt...")

        # Run pipeline with progress updates
        final_state = await run_pipeline_with_progress(pipeline, prompt, client_id)

        # Extract results
        project_path = final_state.get("project_path", "")
        requirements = final_state.get("requirements", {})
        review_results = final_state.get("review_results", {})
        test_results = final_state.get("test_results", {})
        error = final_state.get("error", "")

        if project_path and Path(project_path).exists():
            summary = fs_writer.get_project_summary(Path(project_path))

            # Create zip
            await manager.send_progress(client_id, 10, "Creating project archive...")
            create_project_zip(project_path)

            # Extract test metrics
            tests_passed = None
            if test_results and "test_results" in test_results:
                test_info = test_results["test_results"]
                if isinstance(test_info, dict):
                    tests_passed = test_info.get("passed", test_info.get("total_tests"))

            # Send completion
            response_data = {
                "status": "success" if not error else "completed_with_errors",
                "project_name": summary["project_name"],
                "project_path": project_path,
                "files_count": summary["total_files"],
                "download_url": f"/download/{summary['project_name']}",
                "review_score": review_results.get("overall_score") if review_results else None,
                "tests_passed": tests_passed,
                "error": error if error else None
            }

            await manager.send_complete(client_id, response_data)
        else:
            await manager.send_error(client_id, f"Project generation failed: {error or 'Unknown error'}")

    except Exception as e:
        await manager.send_error(client_id, f"Build failed: {str(e)}")


async def run_pipeline_with_progress(pipeline: MultiAgentPipeline, prompt: str, client_id: str) -> Dict[str, Any]:
    """
    Run the pipeline and send progress updates via WebSocket.
    Uses the pipeline's built-in progress callback.
    """
    
    # Get the main event loop before starting the executor
    main_loop = asyncio.get_running_loop()
    
    # Create a sync callback that works from any thread
    def progress_callback(step_num: int, message: str):
        """Callback that sends progress updates to the WebSocket client."""
        try:
            # Schedule the coroutine to run in the main event loop
            asyncio.run_coroutine_threadsafe(
                manager.send_progress(client_id, step_num, message),
                main_loop
            )
        except Exception as e:
            print(f"Error sending progress update: {e}")
    
    # Create a new pipeline instance with the progress callback
    pipeline_with_progress = MultiAgentPipeline(
        openai_api_key=settings.OPENAI_API_KEY,
        progress_callback=progress_callback
    )
    
    # Run pipeline in executor to avoid blocking
    final_state = await main_loop.run_in_executor(None, pipeline_with_progress.run, prompt)
    
    return final_state


async def handle_list_projects(websocket: WebSocket, client_id: str, data: dict):
    """List all generated projects."""
    projects_dir = Path("generated_projects")

    if not projects_dir.exists():
        await manager.send_complete(client_id, {"projects": []})
        return

    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir():
            summary = fs_writer.get_project_summary(item)
            projects.append({
                "name": item.name,
                "path": str(item),
                "files_count": summary["total_files"],
                "size_bytes": summary["total_size_bytes"]
            })

    await manager.send_complete(client_id, {"projects": projects})


async def handle_project_details(websocket: WebSocket, client_id: str, data: dict):
    """Get detailed information about a generated project."""
    project_name = data.get("project_name")
    if not project_name:
        await manager.send_error(client_id, "Missing 'project_name' field")
        return

    project_path = Path("generated_projects") / project_name

    if not project_path.exists():
        await manager.send_error(client_id, "Project not found")
        return

    summary = fs_writer.get_project_summary(project_path)

    # Read README if it exists
    readme_content = None
    readme_path = project_path / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except Exception:
            pass

    result = {
        "project_name": summary["project_name"],
        "project_path": summary["project_path"],
        "total_files": summary["total_files"],
        "total_size_bytes": summary["total_size_bytes"],
        "files": summary["files"],
        "readme": readme_content
    }

    await manager.send_complete(client_id, result)


async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """
    Main WebSocket endpoint.
    
    Message format (from client):
    {
        "action": "build" | "list" | "details",
        "data": { ... }
    }
    
    Response format (to client):
    {
        "type": "progress" | "complete" | "error",
        "step": int (for progress),
        "message": str (for progress),
        "data": { ... } (for complete),
        "error": str (for error)
    }
    """
    if not client_id:
        client_id = f"client_{id(websocket)}"

    await manager.connect(websocket, client_id)

    try:
        # Send welcome message
        await manager.send_message(client_id, {
            "type": "connected",
            "message": "Connected to Multi-Agent Software Factory",
            "client_id": client_id
        })

        while True:
            # Receive message
            message = await websocket.receive_json()
            action = message.get("action")
            data = message.get("data", {})

            # Route to appropriate handler
            if action == "build":
                await handle_build_project(websocket, client_id, data)
            elif action == "list":
                await handle_list_projects(websocket, client_id, data)
            elif action == "details":
                await handle_project_details(websocket, client_id, data)
            else:
                await manager.send_error(client_id, f"Unknown action: {action}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        await manager.send_error(client_id, f"Error: {str(e)}")
        manager.disconnect(client_id)
