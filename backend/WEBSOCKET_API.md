# WebSocket API Documentation

## Overview

The Multi-Agent Software Factory now uses **WebSocket** for real-time communication, providing live progress updates during project generation.

## Connection

Connect to the WebSocket endpoint:

```
ws://localhost:8000/ws
```

## Message Format

### Client → Server

```json
{
  "action": "build" | "list" | "details",
  "data": { ... }
}
```

### Server → Client

```json
{
  "type": "connected" | "progress" | "complete" | "error",
  "message": "...",
  "step": 1-10,
  "data": { ... },
  "error": "..."
}
```

## Actions

### 1. Build Project

Generate a complete software project with real-time progress updates.

**Request:**
```json
{
  "action": "build",
  "data": {
    "prompt": "Create a REST API for a todo list using FastAPI"
  }
}
```

**Response (Progress):**
```json
{
  "type": "progress",
  "step": 1,
  "message": "📝 Step 1: Analyzing user prompt..."
}
```

**Response (Complete):**
```json
{
  "type": "complete",
  "data": {
    "status": "success",
    "project_name": "Todo_List_REST_API",
    "project_path": "/path/to/project",
    "files_count": 25,
    "download_url": "/download/Todo_List_REST_API",
    "review_score": 8.5,
    "tests_passed": 15
  }
}
```

### 2. List Projects

Get a list of all generated projects.

**Request:**
```json
{
  "action": "list",
  "data": {}
}
```

**Response:**
```json
{
  "type": "complete",
  "data": {
    "projects": [
      {
        "name": "Todo_List_REST_API",
        "path": "/path/to/project",
        "files_count": 25,
        "size_bytes": 102400
      }
    ]
  }
}
```

### 3. Get Project Details

Get detailed information about a specific project.

**Request:**
```json
{
  "action": "details",
  "data": {
    "project_name": "Todo_List_REST_API"
  }
}
```

**Response:**
```json
{
  "type": "complete",
  "data": {
    "project_name": "Todo_List_REST_API",
    "project_path": "/path/to/project",
    "total_files": 25,
    "total_size_bytes": 102400,
    "files": [...],
    "readme": "# Todo List API\n..."
  }
}
```

## Workflow Steps

The build process includes 10 steps with progress updates:

1. 📝 Analyzing user prompt
2. 🔍 Planning research
3. 📊 Conducting market research
4. 🏗️ Planning implementation
5. 📚 Researching documentation
6. 💻 Implementing code
7. 🔎 Reviewing code
8. 🧪 Testing code
9. 📖 Writing documentation
10. 💾 Writing to disk

## Python Client Example

```python
import asyncio
import websockets
import json

async def build_project():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Wait for connection
        welcome = await websocket.recv()
        print(welcome)
        
        # Send build request
        request = {
            "action": "build",
            "data": {
                "prompt": "Create a todo list API"
            }
        }
        await websocket.send(json.dumps(request))
        
        # Receive updates
        while True:
            message = await websocket.recv()
            response = json.loads(message)
            
            if response["type"] == "progress":
                print(f"Step {response['step']}: {response['message']}")
            elif response["type"] == "complete":
                print("Done!", response["data"])
                break
            elif response["type"] == "error":
                print("Error:", response["error"])
                break

asyncio.run(build_project())
```

## JavaScript Client Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
  
  // Send build request
  ws.send(JSON.stringify({
    action: 'build',
    data: {
      prompt: 'Create a todo list API'
    }
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  
  if (response.type === 'progress') {
    console.log(`Step ${response.step}: ${response.message}`);
  } else if (response.type === 'complete') {
    console.log('Done!', response.data);
    ws.close();
  } else if (response.type === 'error') {
    console.error('Error:', response.error);
    ws.close();
  }
};
```

## REST Endpoints (Backwards Compatibility)

The following REST endpoints are still available:

- `GET /` - API information
- `GET /health` - Health check
- `POST /projects/build` - Build project (no real-time updates)
- `GET /projects/list` - List projects
- `GET /projects/{project_name}/details` - Get project details
- `GET /download/{project_name}` - Download project zip

## Error Handling

Errors are sent as:

```json
{
  "type": "error",
  "error": "Description of the error"
}
```

## Running the Example Client

```bash
# Install websockets
pip install websockets

# Run the example client
python examples/websocket_client.py
```

## Benefits of WebSocket API

1. **Real-time Updates**: See progress as each step completes
2. **Better UX**: No polling required
3. **Lower Latency**: Persistent connection
4. **Bidirectional**: Server can push updates anytime
5. **Efficient**: Less overhead than HTTP polling
