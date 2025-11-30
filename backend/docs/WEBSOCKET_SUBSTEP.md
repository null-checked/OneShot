# WebSocket Substep & Data Payloads

This document describes the most recent changes to the WebSocket API and the pipeline so clients can receive both human-friendly progress text and the actual outputs (objects/snippets) produced by agents and internal processes.

**Location**: `backend/src/api/v1/endpoints/websocket_handler.py`

---

**Goals of these changes**

- Forward real process outputs from the pipeline to WebSocket clients instead of only human-readable, hardcoded messages.
- Provide compact previews (snippets) for generated files so UIs can show expandable details without fetching entire files by default.
- Keep messages JSON-serializable and bounded in size by default; allow on-demand retrieval of full file contents (can be added as a follow-up).

---

**High-level behavior**

- The pipeline (`MultiAgentPipeline`) now passes a `data` payload to both `progress_callback` and `substep_callback` when available. The `data` payload contains the real output for that step (e.g., `requirements`, `research_plan`, `files + snippets`, `review_results`, `test_results`, `project_path`).
- The WebSocket handler captures those `data` payloads and forwards them in the `substep` and `progress` messages under the `data` key.
- The heartbeat message shows a short `last_substep` snippet so UIs can always show activity.

---

**Message Types & Schemas**

1) `connected`

  - Sent once on connection.
  - Example:

```json
{ "type": "connected", "message": "Connected to Multi-Agent Software Factory", "client_id": "client_123" }
```

2) `progress`

  - Sent to indicate high-level step progress.
  - Keys: `type`, `step`, `message`, optional `data`.
  - Example:

```json
{
  "type": "progress",
  "step": 6,
  "message": "💻 Implementing code...",
  "data": null
}
```

3) `substep`

  - Sent for detailed events inside a step (upcoming/start/done/file/written/error).
  - Keys: `type`, `step`, `substep`, `message`, optional `data`.
  - When `data` is present it contains the actual process output (objects, file lists, snippets, test results, etc.).
  - Examples:

File list + snippets (code generation done):

```json
{
  "type": "substep",
  "step": 6,
  "substep": "done",
  "message": "Generated 5 code files",
  "data": {
    "files": ["app.py","utils.py","models.py"],
    "snippets": {"app.py": "from fastapi import FastAPI\napp = FastAPI()\n..."}
  }
}
```

Per-file event:

```json
{
  "type": "substep",
  "step": 6,
  "substep": "file",
  "message": "Generated file: app.py",
  "data": {"file": "app.py", "snippet": "from fastapi import FastAPI\n..."}
}
```

4) `heartbeat`

  - Sent periodically while the pipeline runs.
  - Keys: `type`, `current_step`, `last_substep`.
  - Example:

```json
{ "type": "heartbeat", "current_step": 6, "last_substep": "file: Generated file: app.py..." }
```

5) `complete`

  - Sent when pipeline finishes for `build` or in response to `list` / `details`.
  - Contains final results (e.g., project path, download link, review/test summaries).

6) `error`

  - Sent on errors with an `error` string.

---

Design notes and rules

- `data` values are provided where available and will typically be JSON-serializable Python primitives (dicts, lists, strings, numbers).
- File contents are truncated to the first ~200 characters as `snippet` to avoid large WS payloads. If you need full file contents, consider adding a `details` action or a `file_get` request to fetch the entire file on demand.
- The pipeline schedules callbacks from worker threads into the main asyncio loop — the WebSocket handler uses `run_coroutine_threadsafe` to deliver messages safely.

---

Client recommendations (frontend/backends)

- Render both `message` (friendly label) and `data` (structured output). Use `message` for timelines and `data` for details when expanded.
- For `substep` with `data.snippets`: show an expandable view containing the snippet and a small copy / open-in-editor button.
- Respect `snippet` length limits. Provide a button to request full contents via either an HTTP endpoint `GET /project/{name}/file/{path}` or a WS `action: "file_details"` (server-side implementation suggested below).
- Use the `heartbeat` messages to show spinner/activity indicators so the UI doesn't appear stuck during long LLM calls.

---

Suggested follow-ups (optional)

1) Add a `file_details` WebSocket action or HTTP endpoint to return full file contents on-demand.
2) Add an explicit max-size policy for `data` (e.g., do not forward objects > 512KB) and provide a link/ID instead.
3) Add authentication & message signing for production WebSocket usage.

---

Quick test steps

1. Start backend server (from repository root):

```bash
cd backend
python3 -m uvicorn src.main:app --reload --port 8000
```

2. Open the WebSocket client (example HTML or Python client) and send:

```json
{ "action": "build", "data": { "prompt": "Create a small FastAPI app that ..." } }
```

3. Watch for `substep` messages that include `data` (snippets, files list, test/review results).

---

File created by automation: `backend/docs/WEBSOCKET_SUBSTEP.md`

If you want, I can now:

- Update the example HTML (`examples/test_client.html`) to render `data` payloads in an expandable UI.
- Add an on-demand `file_details` action in the WebSocket handler so the client can fetch full file contents.
- Add a small README section linking to this doc.

Pick one and I'll implement it next.
