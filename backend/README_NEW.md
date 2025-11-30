# Multi-Agent Software Factory - Backend

## Overview

AI-powered software project generator using **WebSocket** for real-time communication.

## Features

- ⚡ **WebSocket API**: Real-time progress updates during project generation
- 🤖 **9-Step Workflow**: Automated project creation from prompt to deployment-ready code
- 📡 **REST Fallback**: Backwards compatible REST endpoints
- 📦 **File Download**: Download generated projects as zip files

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at `http://localhost:8000`

WebSocket endpoint: `ws://localhost:8000/ws`

## API Documentation

### WebSocket API (Primary)

Connect to: `ws://localhost:8000/ws`

**See [WEBSOCKET_API.md](./WEBSOCKET_API.md) for complete documentation.**

Quick example:
```python
import asyncio
import websockets
import json

async def build():
    async with websockets.connect("ws://localhost:8000/ws") as ws:
        await ws.recv()  # Welcome message
        await ws.send(json.dumps({
            "action": "build",
            "data": {"prompt": "Create a todo API"}
        }))
        
        while True:
            msg = json.loads(await ws.recv())
            if msg["type"] == "progress":
                print(f"Step {msg['step']}: {msg['message']}")
            elif msg["type"] == "complete":
                print("Done!", msg["data"])
                break

asyncio.run(build())
```

### REST Endpoints (Legacy Support)

- `GET /` - API information
- `GET /health` - Health check
- `POST /projects/build` - Build project (no real-time updates)
- `GET /projects/list` - List all projects
- `GET /projects/{project_name}/details` - Get project details
- `GET /download/{project_name}` - Download project as zip

## Example Client

Run the included example client:

```bash
python examples/websocket_client.py
```

## Project Structure

```
backend/
├─ examples/
│  └─ websocket_client.py      # Example WebSocket client
├─ src/
│  ├─ api/
│  │  └─ v1/
│  │     ├─ endpoints/
│  │     │  ├─ healthcheck.py
│  │     │  ├─ project_router.py    # REST endpoints
│  │     │  └─ websocket_handler.py # WebSocket handler
│  │     └─ router.py
│  ├─ core/                    # Business logic
│  │  ├─ agents.py
│  │  ├─ builder.py
│  │  ├─ pipeline.py
│  │  └─ ...
│  ├─ main.py                  # FastAPI app
│  └─ settings.py
├─ generated_projects/         # Output directory
├─ pyproject.toml
├─ README.md
└─ WEBSOCKET_API.md           # Full API docs
```

## Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key-here
APP_HOST=0.0.0.0
APP_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

## Workflow Steps

The system generates projects through 10 automated steps:

1. 📝 Analyze user prompt
2. 🔍 Plan research
3. 📊 Conduct market research
4. 🏗️ Plan implementation
5. 📚 Research documentation
6. 💻 Implement code
7. 🔎 Review code
8. 🧪 Test code
9. 📖 Write documentation
10. 💾 Write to disk

Each step sends a progress update via WebSocket!

## Benefits of WebSocket

- **Real-time feedback**: See progress as it happens
- **Better UX**: No polling required
- **Lower latency**: Persistent connection
- **Bidirectional**: Server pushes updates instantly
- **Efficient**: Less overhead than HTTP polling

## Development

```bash
# Install in development mode
pip install -e .

# Run with auto-reload
uvicorn src.main:app --reload

# Run tests
pytest
```

## License

See LICENSE file for details.
