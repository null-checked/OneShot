"""
Example WebSocket client for the Multi-Agent Software Factory.
Demonstrates how to connect and interact with the WebSocket API.
"""

import asyncio
import websockets
import json


async def build_project(uri: str, prompt: str):
    """
    Example: Build a project with real-time progress updates.
    
    Args:
        uri: WebSocket URI (e.g., "ws://localhost:8000/ws")
        prompt: Project description prompt
    """
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        
        # Wait for connection message
        welcome = await websocket.recv()
        print(f"Server: {welcome}")
        
        # Send build request
        request = {
            "action": "build",
            "data": {
                "prompt": prompt
            }
        }
        await websocket.send(json.dumps(request))
        print(f"Sent build request: {prompt[:50]}...")
        
        # Receive progress updates and final result
        while True:
            try:
                message = await websocket.recv()
                response = json.loads(message)
                
                msg_type = response.get("type")
                
                if msg_type == "progress":
                    step = response.get("step")
                    message = response.get("message")
                    print(f"[Step {step}] {message}")
                    
                elif msg_type == "complete":
                    data = response.get("data")
                    print("\n✅ Project generation complete!")
                    print(f"Project: {data.get('project_name')}")
                    print(f"Files: {data.get('files_count')}")
                    print(f"Path: {data.get('project_path')}")
                    print(f"Download: {data.get('download_url')}")
                    if data.get('review_score'):
                        print(f"Review Score: {data.get('review_score')}")
                    if data.get('tests_passed'):
                        print(f"Tests Passed: {data.get('tests_passed')}")
                    break
                    
                elif msg_type == "error":
                    error = response.get("error")
                    print(f"\n❌ Error: {error}")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break


async def list_projects(uri: str):
    """
    Example: List all generated projects.
    
    Args:
        uri: WebSocket URI (e.g., "ws://localhost:8000/ws")
    """
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        
        # Wait for connection message
        welcome = await websocket.recv()
        print(f"Server: {welcome}")
        
        # Send list request
        request = {
            "action": "list",
            "data": {}
        }
        await websocket.send(json.dumps(request))
        print("Requesting project list...")
        
        # Receive response
        message = await websocket.recv()
        response = json.loads(message)
        
        if response.get("type") == "complete":
            projects = response.get("data", {}).get("projects", [])
            print(f"\n📁 Found {len(projects)} projects:")
            for project in projects:
                print(f"  - {project['name']} ({project['files_count']} files)")
        else:
            print(f"Error: {response.get('error')}")


async def get_project_details(uri: str, project_name: str):
    """
    Example: Get details for a specific project.
    
    Args:
        uri: WebSocket URI (e.g., "ws://localhost:8000/ws")
        project_name: Name of the project
    """
    async with websockets.connect(uri) as websocket:
        print("Connected to server")
        
        # Wait for connection message
        welcome = await websocket.recv()
        print(f"Server: {welcome}")
        
        # Send details request
        request = {
            "action": "details",
            "data": {
                "project_name": project_name
            }
        }
        await websocket.send(json.dumps(request))
        print(f"Requesting details for: {project_name}")
        
        # Receive response
        message = await websocket.recv()
        response = json.loads(message)
        
        if response.get("type") == "complete":
            data = response.get("data", {})
            print(f"\n📦 Project Details:")
            print(f"Name: {data.get('project_name')}")
            print(f"Files: {data.get('total_files')}")
            print(f"Size: {data.get('total_size_bytes')} bytes")
            print(f"Path: {data.get('project_path')}")
            if data.get('readme'):
                print(f"\nREADME preview:\n{data['readme'][:200]}...")
        else:
            print(f"Error: {response.get('error')}")


async def main():
    """Main function with usage examples."""
    # Configuration
    WS_URI = "ws://localhost:8000/ws"
    
    print("=" * 70)
    print("Multi-Agent Software Factory - WebSocket Client Examples")
    print("=" * 70)
    
    # Example 1: Build a project
    print("\n1. Building a project...")
    await build_project(
        WS_URI,
        "Create a simple REST API for a todo list using FastAPI and SQLite"
    )
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Example 2: List projects
    print("\n2. Listing all projects...")
    await list_projects(WS_URI)
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Example 3: Get project details (replace with actual project name)
    print("\n3. Getting project details...")
    await get_project_details(WS_URI, "Todo_List_REST_API")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped")
    except Exception as e:
        print(f"Error: {e}")
