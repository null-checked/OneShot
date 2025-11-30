# Migration from REST to WebSocket API

## Summary

The Multi-Agent Software Factory backend has been converted from REST to **WebSocket** for real-time communication while maintaining REST endpoints for backwards compatibility.

## What Changed

### 1. New WebSocket Handler
**File**: `src/api/v1/endpoints/websocket_handler.py`
- Main WebSocket endpoint at `/ws`
- Handles three actions: `build`, `list`, `details`
- Sends real-time progress updates during project generation
- WebSocketManager class for connection management

### 2. Updated Main Application
**File**: `src/main.py`
- Added WebSocket route: `app.add_api_websocket_route("/ws", websocket_endpoint)`
- Updated root endpoint documentation to reflect WebSocket API
- Kept existing REST endpoints for backwards compatibility

### 3. Updated Router
**File**: `src/api/v1/router.py`
- Imported websocket_endpoint handler
- REST endpoints remain functional

### 4. Dependencies
**File**: `pyproject.toml`
- Added `websockets>=15.1` package

### 5. Documentation
- **WEBSOCKET_API.md**: Complete WebSocket API documentation
- **README_NEW.md**: Updated README with WebSocket information
- **examples/websocket_client.py**: Python client example
- **examples/test_client.html**: Browser-based test client

## New Features

### Real-time Progress Updates
Projects are generated through 10 steps, each sending a progress update:

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

### WebSocket Message Types

**Client → Server:**
```json
{
  "action": "build" | "list" | "details",
  "data": { ... }
}
```

**Server → Client:**
```json
{
  "type": "connected" | "progress" | "complete" | "error",
  "step": 1-10,
  "message": "...",
  "data": { ... }
}
```

## How to Use

### 1. Install Dependencies
```bash
pip install -e .
```

### 2. Start Server
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Connect via WebSocket
**Endpoint**: `ws://localhost:8000/ws`

### 4. Test with Examples

**Python Client:**
```bash
python examples/websocket_client.py
```

**Browser Client:**
Open `examples/test_client.html` in a web browser

## Backwards Compatibility

All existing REST endpoints still work:
- `POST /projects/build` - Build without real-time updates
- `GET /projects/list` - List projects
- `GET /projects/{name}/details` - Get details
- `GET /download/{name}` - Download zip
- `GET /health` - Health check

## Benefits

✅ **Real-time feedback** - See progress as it happens  
✅ **Better UX** - No polling required  
✅ **Lower latency** - Persistent connection  
✅ **Bidirectional** - Server pushes updates instantly  
✅ **Efficient** - Less overhead than HTTP polling  

## Migration Guide for Clients

### Before (REST):
```python
import requests

response = requests.post('http://localhost:8000/projects/build', 
                        json={'prompt': 'Create a todo API'})
result = response.json()
```

### After (WebSocket):
```python
import asyncio
import websockets
import json

async def build():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.recv()  # Welcome
        await ws.send(json.dumps({
            'action': 'build',
            'data': {'prompt': 'Create a todo API'}
        }))
        
        while True:
            msg = json.loads(await ws.recv())
            if msg['type'] == 'progress':
                print(f"Step {msg['step']}: {msg['message']}")
            elif msg['type'] == 'complete':
                print('Done!', msg['data'])
                break

asyncio.run(build())
```

## Testing

1. Start the server
2. Open `examples/test_client.html` in browser
3. Click "Connect & Build"
4. Watch real-time progress updates
5. Try "List Projects" to see generated projects

## Files Created/Modified

### Created:
- `src/api/v1/endpoints/websocket_handler.py`
- `examples/websocket_client.py`
- `examples/test_client.html`
- `WEBSOCKET_API.md`
- `README_NEW.md`
- `MIGRATION.md` (this file)

### Modified:
- `src/main.py` - Added WebSocket route
- `src/api/v1/router.py` - Imported WebSocket handler
- `pyproject.toml` - Added websockets dependency

### Unchanged:
- All REST endpoints still functional
- Core pipeline logic unchanged
- Agent implementations unchanged
- File system writer unchanged

## Next Steps

1. Update frontend to use WebSocket
2. Add authentication to WebSocket
3. Add rate limiting
4. Add WebSocket reconnection logic
5. Add unit tests for WebSocket handler

## Questions?

See `WEBSOCKET_API.md` for detailed API documentation.
