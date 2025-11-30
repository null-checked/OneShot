"""
WebSocket handler for the Multi-Agent Software Factory.
Replaces REST endpoints with real-time WebSocket communication.
"""

from fastapi import WebSocket, WebSocketDisconnect
from pathlib import Path
import json
import asyncio
from typing import Dict, Any

from src.core.pipeline import MultiAgentPipeline
from src.settings import get_pipeline_agent, fs_writer
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

        # Detect pipeline type and handle accordingly
        from src.core.architect_pipeline import ArchitectPipeline

        if isinstance(pipeline, ArchitectPipeline):
            # New architect-based pipeline
            await manager.send_progress(client_id, 1, "[PLAN] Architect Agent - Analyzing and Planning...")
            final_state = await run_architect_pipeline_with_progress(pipeline, prompt, client_id)

            # Extract results from architect pipeline
            project_path = final_state.get("project_path", "")
            test_results = final_state.get("test_results", {})
            success = final_state.get("success", False)

            if project_path and Path(project_path).exists():
                summary = fs_writer.get_project_summary(Path(project_path))

                # Create zip
                await manager.send_progress(client_id, 10, "Creating project archive...")
                create_project_zip(project_path)

                # Extract test metrics
                tests_passed = test_results.get("tests_passed", 0)
                tests_total = test_results.get("tests_run", 0)

                # Send completion
                response_data = {
                    "status": "success" if success else "completed_with_issues",
                    "project_name": summary["project_name"],
                    "project_path": project_path,
                    "files_count": summary["total_files"],
                    "download_url": f"/download/{summary['project_name']}",
                    "tests_passed": tests_passed,
                    "tests_total": tests_total,
                    "agents_used": len(final_state.get("agent_results", [])),
                    "all_criteria_met": final_state.get("criteria_results", {}).get("all_criteria_met", False)
                }

                await manager.send_complete(client_id, response_data)
            else:
                await manager.send_error(client_id, "Project generation failed: Unknown error")

        else:
            # Old multi-agent pipeline
            await manager.send_progress(client_id, 1, "[NOTE] Step 1: Analyzing user prompt...")
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
    """
    # Hook into pipeline steps to send progress
    original_step1 = pipeline._step1_analyze_prompt
    original_step2 = pipeline._step2_plan_research
    original_step3 = pipeline._step3_market_research
    original_step4 = pipeline._step4_plan_implementation
    original_step5 = pipeline._step5_research_documentation
    original_step6 = pipeline._step6_implement_code
    original_step7 = pipeline._step7_review_code
    original_step8 = pipeline._step8_test_code
    original_step9 = pipeline._step9_write_documentation
    original_step10 = pipeline._step10_write_to_disk

    async def wrapped_step(step_num: int, step_name: str, original_func, state):
        await manager.send_progress(client_id, step_num, step_name)
        return original_func(state)

    # Wrap each step
    pipeline._step1_analyze_prompt = lambda s: wrapped_step(1, "[NOTE] Analyzing prompt...", original_step1, s)
    pipeline._step2_plan_research = lambda s: wrapped_step(2, "[SEARCH] Planning research...", original_step2, s)
    pipeline._step3_market_research = lambda s: wrapped_step(3, "[DATA] Conducting market research...", original_step3, s)
    pipeline._step4_plan_implementation = lambda s: wrapped_step(4, "[ARCH] Planning implementation...", original_step4, s)
    pipeline._step5_research_documentation = lambda s: wrapped_step(5, "[DOCS] Researching documentation...", original_step5, s)
    pipeline._step6_implement_code = lambda s: wrapped_step(6, "[CODE] Implementing code...", original_step6, s)
    pipeline._step7_review_code = lambda s: wrapped_step(7, "[CHECK] Reviewing code...", original_step7, s)
    pipeline._step8_test_code = lambda s: wrapped_step(8, "[TEST] Testing code...", original_step8, s)
    pipeline._step9_write_documentation = lambda s: wrapped_step(9, "[READ] Writing documentation...", original_step9, s)
    pipeline._step10_write_to_disk = lambda s: wrapped_step(10, "[SAVE] Writing to disk...", original_step10, s)

    # Run pipeline synchronously (we'll handle async in a thread)
    import concurrent.futures
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        final_state = await loop.run_in_executor(executor, pipeline.run, prompt)

    return final_state


async def run_architect_pipeline_with_progress(pipeline, prompt: str, client_id: str) -> Dict[str, Any]:
    """
    Run the architect pipeline and send progress updates via WebSocket.
    """
    from src.core.architect_pipeline import ArchitectPipeline

    # We can't easily hook into the architect pipeline like the old one,
    # so we'll run it in a thread and send periodic updates
    import concurrent.futures

    # Progress messages for different stages
    stage_messages = [
        (1, "[PLAN] Architect Agent - Analyzing requirements..."),
        (2, "[AGENT] Initializing worker agents..."),
        (3, "[CODE] Generating code files..."),
        (4, "[TEST] Running tests..."),
        (5, "[OK] Verifying success criteria..."),
        (6, "[SAVE] Writing project to disk...")
    ]

    current_stage = 0

    async def send_next_progress():
        nonlocal current_stage
        if current_stage < len(stage_messages):
            step, message = stage_messages[current_stage]
            await manager.send_progress(client_id, step, message)
            current_stage += 1

    # Send initial progress
    await send_next_progress()

    # Run pipeline in executor
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the pipeline
        future = loop.run_in_executor(executor, pipeline.run, prompt)

        # Send progress updates while waiting
        while not future.done():
            await asyncio.sleep(2)  # Update every 2 seconds
            await send_next_progress()

        # Get the result
        final_state = await future

    # Send final progress
    await manager.send_progress(client_id, 7, "[DONE] Generation complete!")

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
