# WebSocket API Quick Reference

## Connection
```
ws://localhost:8000/ws
```

## Build Project
```json
→ {"action": "build", "data": {"prompt": "Create a todo API"}}
← {"type": "progress", "step": 1, "message": "📝 Analyzing..."}
← {"type": "progress", "step": 2, "message": "🔍 Planning..."}
...
← {"type": "complete", "data": {"project_name": "...", "files_count": 25}}
```

## List Projects
```json
→ {"action": "list", "data": {}}
← {"type": "complete", "data": {"projects": [...]}}
```

## Get Details
```json
→ {"action": "details", "data": {"project_name": "MyProject"}}
← {"type": "complete", "data": {"project_name": "...", "files": [...]}}
```

## Python Quick Start
```python
import asyncio, websockets, json

async def build():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        await ws.recv()  # Welcome
        await ws.send(json.dumps({'action': 'build', 
                                  'data': {'prompt': 'Create API'}}))
        while True:
            msg = json.loads(await ws.recv())
            if msg['type'] == 'complete': break
            print(msg)

asyncio.run(build())
```

## JavaScript Quick Start
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.type === 'connected') {
    ws.send(JSON.stringify({action: 'build', 
                            data: {prompt: 'Create API'}}));
  }
  console.log(msg);
};
```

## Test Files
- Browser: `examples/test_client.html`
- Python: `examples/websocket_client.py`

## Full Docs
- `WEBSOCKET_API.md` - Complete API documentation
- `MIGRATION.md` - Migration guide from REST
