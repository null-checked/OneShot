# Multi-Agent Competitive Code Arena

## Project Overview

Build a **multi-agent system** where multiple LLM "agents" with different coding personalities compete to solve the same programming problem. A judge evaluates their solutions, and a synthesizer creates a hybrid "best-of" solution.

The system should support:
1. **Local LLMs** via Ollama (default)
2. **OpenAI API** as alternative
3. **Self-hosted** via any OpenAI-compatible endpoint (vLLM, LocalAI, etc.)

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, WebSockets
- **Frontend**: React + Vite + TailwindCSS
- **LLM**: Ollama (local) or OpenAI API
- **Execution**: Subprocess sandboxing (simple) or Docker (production)

---

## Project Structure

```
code-arena/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration and environment variables
│   ├── llm_client.py           # Unified LLM client (Ollama/OpenAI/custom)
│   ├── agents.py               # Agent personalities and generation logic
│   ├── problem_parser.py       # Problem analysis and test case generation
│   ├── executor.py             # Sandboxed code execution
│   ├── judge.py                # Solution scoring and ranking
│   ├── synthesizer.py          # Hybrid solution creation
│   ├── orchestrator.py         # Main arena flow coordination
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Arena.jsx       # Main arena container
│   │   │   ├── ProblemInput.jsx
│   │   │   ├── AgentCard.jsx   # Individual agent display
│   │   │   ├── CodeViewer.jsx  # Syntax-highlighted code
│   │   │   ├── TestRunner.jsx  # Test execution visualization
│   │   │   ├── Scoreboard.jsx  # Rankings display
│   │   │   └── PixelGrid.jsx   # Pixel-based code visualization
│   │   ├── hooks/
│   │   │   └── useArenaSocket.js
│   │   └── utils/
│   │       └── codeToPixels.js # Convert code to pixel representation
│   ├── package.json
│   └── vite.config.js
│
├── .env.example
├── docker-compose.yml          # Optional Docker setup
└── README.md
```

---

## Backend Implementation Details

### 1. Configuration (`config.py`)

Create a configuration system that supports multiple LLM providers:

```
Environment variables to support:
- LLM_PROVIDER: "ollama" | "openai" | "custom"
- OLLAMA_BASE_URL: default "http://localhost:11434"
- OLLAMA_MODEL: default "qwen2.5-coder:7b"
- OPENAI_API_KEY: for OpenAI provider
- OPENAI_MODEL: default "gpt-4o-mini"
- CUSTOM_BASE_URL: for self-hosted OpenAI-compatible APIs
- CUSTOM_MODEL: model name for custom provider
- CUSTOM_API_KEY: optional API key for custom provider
```

Use pydantic-settings for configuration management.

### 2. LLM Client (`llm_client.py`)

Create an abstract base class and implementations for different providers:

**Interface:**
```python
class BaseLLMClient(ABC):
    def generate(self, prompt: str, system: str = None, temperature: float = 0.7) -> str
    def generate_stream(self, prompt: str, system: str = None) -> Generator[str, None, None]
    def is_available(self) -> bool
```

**Implementations needed:**
1. `OllamaClient` - Uses `/api/generate` and `/api/chat` endpoints
2. `OpenAIClient` - Uses official `openai` Python package
3. `OpenAICompatibleClient` - For vLLM, LocalAI, LM Studio (uses `/v1/chat/completions`)

**Factory function:**
```python
def create_llm_client(config: Settings) -> BaseLLMClient
```

### 3. Agent Personalities (`agents.py`)

Define 3-4 agent personalities with distinct coding approaches:

**Agent 1: "RecursiveRex"**
- Color: #3498db (blue)
- Approach: Recursion, divide-and-conquer, memoization
- System prompt emphasizes breaking problems into subproblems

**Agent 2: "DynamicDana"**
- Color: #2ecc71 (green)
- Approach: Dynamic programming, bottom-up solutions, tabulation
- System prompt emphasizes subproblems and recurrence relations

**Agent 3: "GreedyGus"**
- Color: #e74c3c (red)
- Approach: Greedy algorithms, single-pass solutions, two pointers
- System prompt emphasizes simple, efficient iterative solutions

**Agent 4: "DataStructDave"** (optional)
- Color: #9b59b6 (purple)
- Approach: Clever data structure selection (hashmaps, heaps, etc.)
- System prompt emphasizes choosing the right data structure

**CodingAgent class should:**
- Take a personality and LLM client
- Have `generate_solution(problem: dict) -> dict` method
- Return: thinking, approach_name, time_complexity, space_complexity, code
- Handle JSON extraction from potentially messy LLM responses

### 4. Problem Parser (`problem_parser.py`)

**ProblemParser class should:**
- Take user's natural language problem description
- Use LLM to generate structured problem spec
- Return dict with:
  - title: short name
  - description: clear problem statement
  - function_signature: Python function signature with type hints
  - constraints: list of constraints
  - test_cases: list of {input: [...args], expected: result}
    - Include 5-8 test cases: basic cases, edge cases, larger inputs

**Important:** Use lower temperature (0.3) for more consistent output.

### 5. Code Executor (`executor.py`)

**Sandboxed execution using subprocess:**

```python
def execute_in_sandbox(
    code: str,
    function_name: str,
    test_cases: List[dict],
    timeout_seconds: float = 5.0
) -> TestSuiteResult
```

**TestSuiteResult dataclass:**
- agent_name: str
- total_tests: int
- passed_tests: int
- results: List[ExecutionResult]
- avg_time_ms: float
- max_memory_kb: int
- has_errors: bool

**ExecutionResult dataclass:**
- passed: bool
- actual_output: Any
- expected_output: Any
- execution_time_ms: float
- error: Optional[str]

**Implementation approach:**
1. Create temporary Python file with user's code + test runner
2. Execute with subprocess.run() with timeout
3. Capture stdout as JSON result
4. Parse and return structured result
5. Clean up temp file

**Security considerations:**
- Use timeout to prevent infinite loops
- Consider using `resource` module to limit memory (Linux only)
- For production: use Docker containers instead

### 6. Judge (`judge.py`)

**Judge class should evaluate solutions on three criteria:**

1. **Correctness Score (50% weight)**
   - (passed_tests / total_tests) * 100

2. **Performance Score (30% weight)**
   - Normalize execution times across all solutions
   - Fastest = 100, slowest = 0

3. **Code Quality Score (20% weight)**
   - Simple heuristics: line count, has docstring, has comments, line length
   - Or use AST analysis for complexity metrics

**Output: List[JudgeScore]** with:
- agent_name, correctness_score, performance_score, code_quality_score
- total_score (weighted sum)
- rank (1-based)
- analysis (text summary)

### 7. Synthesizer (`synthesizer.py`)

**Synthesizer class should:**
- Take all solutions and their scores
- Use LLM to analyze strengths/weaknesses of each
- Create a hybrid solution combining best ideas
- Return dict with:
  - synthesis_reasoning: explanation of what was taken from each
  - improvements: list of improvements made
  - approach: name of final approach
  - time_complexity, space_complexity
  - code: the hybrid solution

### 8. Orchestrator (`orchestrator.py`)

**Main flow coordination:**

```python
class ArenaOrchestrator:
    def __init__(self, config, event_callback=None)
    def run(self, problem_description: str) -> dict
```

**Stages:**
1. **Parse** - Convert user input to structured problem
2. **Generate** - Each agent creates a solution (can be parallel with threads)
3. **Execute** - Run each solution against test cases
4. **Judge** - Score and rank solutions
5. **Synthesize** - Create hybrid solution
6. **Return** - Complete results

**Event emission** for real-time UI updates:
- "status" - current stage
- "problem_parsed" - problem details
- "agent_start" - agent beginning work
- "agent_complete" - agent finished
- "test_results" - per-agent test results
- "scores" - final rankings
- "synthesis_complete" - hybrid solution ready

### 9. FastAPI Server (`main.py`)

**Endpoints:**

```
GET  /api/health         - Check if LLM is available
GET  /api/models         - List available models (for Ollama)
POST /api/arena          - Synchronous arena run (returns all at once)
WS   /ws/arena           - WebSocket for real-time updates
```

**WebSocket protocol:**
- Client sends: `{"problem": "...", "model": "...", "num_agents": 3}`
- Server sends: `{"type": "event_type", "data": {...}}` for each event
- Final message: `{"type": "final_results", "data": {...}}`

---

## Frontend Implementation Details

### 1. Main App (`App.jsx`)

- State: problem input, arena status, results
- Two main views: input form and arena display
- Handle WebSocket connection lifecycle

### 2. Arena Component (`Arena.jsx`)

Main container with layout:
```
┌────────────────────────────────────────────────┐
│  Problem Title & Description                   │
├────────────┬────────────┬────────────┬─────────┤
│  Agent 1   │  Agent 2   │  Agent 3   │ Hybrid  │
│  Card      │  Card      │  Card      │ Card    │
├────────────┴────────────┴────────────┴─────────┤
│  Scoreboard / Rankings                         │
└────────────────────────────────────────────────┘
```

### 3. AgentCard Component (`AgentCard.jsx`)

Display for each agent:
- Name and color indicator
- Current status (thinking, coding, testing, done)
- Approach name and complexity
- Mini code preview or pixel visualization
- Test results (passed/total with progress bar)
- Score breakdown when available

**States:**
- `idle` - waiting to start
- `thinking` - generating solution
- `testing` - running tests
- `complete` - finished with results

### 4. Pixel Visualization (`PixelGrid.jsx`)

Convert code to visual pixel representation:

**Approach 1: Token-based coloring**
- Each token type gets a color (keywords=blue, strings=green, numbers=orange, etc.)
- Display as small colored squares in a grid
- Animate by revealing pixels as code "streams"

**Approach 2: Line-based blocks**
- Each line = one row of pixels
- Width based on line length
- Color based on line type (function def, loop, condition, return)

**Approach 3: AST-based visualization**
- Parse code to AST
- Visualize structure as nested colored blocks
- Shows code "shape" at a glance

Recommend **Approach 1** for hackathon - simpler and more visually interesting.

### 5. Test Runner Visualization (`TestRunner.jsx`)

Show test execution as animated sequence:
- Row of circles/squares for each test case
- Animate from gray → yellow (running) → green/red (pass/fail)
- Show execution time on hover

### 6. Scoreboard (`Scoreboard.jsx`)

Rankings display:
- Sorted by total score
- Show breakdown: correctness, performance, quality
- Highlight winner with animation
- Compare with hybrid solution score

### 7. WebSocket Hook (`useArenaSocket.js`)

Custom React hook for WebSocket management:

```javascript
function useArenaSocket() {
  // Returns: { connect, disconnect, status, events, sendProblem }
  // Handles reconnection, message parsing, event buffering
}
```

---

## Pixel Animation Specification

### Code-to-Pixels Algorithm

```javascript
function codeToPixels(code) {
  // 1. Tokenize the code (simple regex-based)
  // 2. Map each token to a color based on type:
  //    - keywords (def, if, for, while, return): #3498db
  //    - strings: #2ecc71
  //    - numbers: #e67e22
  //    - operators: #9b59b6
  //    - comments: #7f8c8d
  //    - identifiers: #ecf0f1
  //    - whitespace: transparent
  // 3. Return 2D array of colors representing the code
}
```

### Animation Sequence

1. **Generation phase**: Pixels appear row by row (typewriter effect)
2. **Testing phase**: Flash/pulse effect on the code block
3. **Result phase**: Border glow (green=pass, red=fail)
4. **Winner phase**: Winning agent's code gets highlight animation

---

## API Response Formats

### Problem Parsed Event
```json
{
  "type": "problem_parsed",
  "data": {
    "title": "Two Sum",
    "description": "Given an array of integers...",
    "function_signature": "def two_sum(nums: List[int], target: int) -> List[int]",
    "test_count": 6
  }
}
```

### Agent Complete Event
```json
{
  "type": "agent_complete",
  "data": {
    "agent": "RecursiveRex",
    "approach_name": "Recursive with memoization",
    "thinking": "Break down into subproblems...",
    "complexity": "O(n)",
    "code": "def two_sum(nums, target):\n    ..."
  }
}
```

### Test Results Event
```json
{
  "type": "test_results",
  "data": {
    "agent": "RecursiveRex",
    "passed": 5,
    "total": 6,
    "avg_time_ms": 1.23,
    "results": [
      {"passed": true, "time_ms": 0.5},
      {"passed": true, "time_ms": 0.8},
      {"passed": false, "time_ms": 5000, "error": "TIMEOUT"}
    ]
  }
}
```

### Scores Event
```json
{
  "type": "scores",
  "data": {
    "rankings": [
      {
        "rank": 1,
        "agent": "DynamicDana",
        "total": 87.5,
        "correctness": 100,
        "performance": 85,
        "quality": 70,
        "analysis": "DP approach with O(n) time"
      }
    ]
  }
}
```

---

## Environment Setup

### .env.example
```
# LLM Provider: "ollama", "openai", or "custom"
LLM_PROVIDER=ollama

# Ollama settings (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b

# OpenAI settings (if using OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Custom OpenAI-compatible endpoint (if using vLLM, LocalAI, etc.)
CUSTOM_BASE_URL=http://localhost:8000
CUSTOM_MODEL=deepseek-coder
CUSTOM_API_KEY=

# Server settings
HOST=0.0.0.0
PORT=8000
```

### requirements.txt
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
websockets>=12.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
openai>=1.0.0
```

### package.json (frontend dependencies)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-syntax-highlighter": "^15.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "vite": "^5.0.0"
  }
}
```

---

## Running Instructions

### Local with Ollama
```bash
# 1. Install and start Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# 2. Pull a coding model
ollama pull qwen2.5-coder:7b

# 3. Start backend
cd backend
pip install -r requirements.txt
python main.py

# 4. Start frontend
cd frontend
npm install
npm run dev
```

### With OpenAI API
```bash
# 1. Set environment variable
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-your-key

# 2. Start backend
cd backend
python main.py

# 3. Start frontend
cd frontend
npm run dev
```

---

## Implementation Priority for Hackathon

### Must Have (MVP)
1. LLM client with Ollama + OpenAI support
2. 3 agent personalities
3. Problem parser
4. Code executor (basic subprocess)
5. Simple judge (correctness only)
6. Basic React UI showing agents and results

### Should Have
1. WebSocket real-time updates
2. Pixel visualization
3. Full judge with all scoring
4. Synthesizer for hybrid solution

### Nice to Have
1. Streaming code generation display
2. Animated test runner
3. Code diff view for hybrid
4. Docker sandboxing
5. Multiple language support

---

## Testing the System

### Test Problem 1 (Easy)
```
Write a function that returns the sum of all even numbers in a list.
```

### Test Problem 2 (Medium)
```
Given an array of integers, find two numbers that add up to a target value. Return their indices.
```

### Test Problem 3 (Hard)
```
Find the longest palindromic substring in a given string.
```

---

## Notes for Implementation

1. **JSON Extraction**: Local LLMs often add extra text around JSON. Always use robust extraction that finds `{...}` in the response.

2. **Timeout Handling**: Set reasonable timeouts (5s per test, 60s for LLM generation).

3. **Error Recovery**: If one agent fails, continue with others. Show partial results.

4. **Model Flexibility**: Different models have different capabilities. Simpler prompts work better with smaller models.

5. **Streaming**: For better UX, stream the code generation to show "typing" effect.

6. **Caching**: Consider caching problem parsing results to speed up re-runs.
