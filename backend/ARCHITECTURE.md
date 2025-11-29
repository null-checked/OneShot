# Architecture Documentation

## System Overview

The Multi-Agent Software Factory is a sophisticated AI-powered system that generates complete software projects from natural language descriptions. It uses a multi-agent architecture orchestrated by LangGraph to ensure high-quality, production-ready code output.

## Core Concepts

### Multi-Agent System

Each agent in the system has a specific responsibility and expertise:

- **Specialization**: Each agent focuses on one aspect (analysis, research, coding, etc.)
- **Sequential Execution**: Agents execute in a predefined order via LangGraph
- **State Sharing**: All agents read and write to a shared `WorkflowState`
- **Modularity**: Agents can be modified or replaced independently

### LangGraph Orchestration

LangGraph provides the workflow engine:

```python
workflow = StateGraph(WorkflowState)
workflow.add_node("step1", agent1.execute)
workflow.add_edge("step1", "step2")
# ... more nodes and edges
compiled_graph = workflow.compile()
```

Benefits:
- **Deterministic Flow**: Clear execution order
- **State Management**: Automatic state passing between nodes
- **Error Handling**: Centralized error capture
- **Debuggability**: Easy to trace execution

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
│                     (main.py)                               │
│                                                             │
│  Endpoints: /build, /download, /projects, /health          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Agent Pipeline                           │
│              (core/pipeline.py)                             │
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │          LangGraph State Machine                 │      │
│  │                                                  │      │
│  │  State: WorkflowState (Dict)                    │      │
│  │  - user_prompt                                  │      │
│  │  - requirements                                 │      │
│  │  - research_plan                                │      │
│  │  - market_research                              │      │
│  │  - implementation_plan                          │      │
│  │  - code_files                                   │      │
│  │  - review_results                               │      │
│  │  - test_results                                 │      │
│  │  - documentation_files                          │      │
│  │  - project_path                                 │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│  Sequential Agent Execution:                               │
│                                                             │
│  1. PromptAnalyzerAgent                                    │
│  2. ResearchPlannerAgent                                   │
│  3. MarketResearcherAgent                                  │
│  4. ImplementationPlannerAgent                             │
│  5. DocumentationResearcherAgent                           │
│  6. CodeImplementerAgent                                   │
│  7. CodeReviewerAgent                                      │
│  8. CodeTesterAgent                                        │
│  9. DocumentationWriterAgent                               │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Specialized Modules                            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Builder    │  │   Reviewer   │  │    Tester    │     │
│  │  (builder.py)│  │(reviewer.py) │  │  (tester.py) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────────────────────────┐   │
│  │  Doc Writer  │  │    Filesystem Writer             │   │
│  │(doc_writer.py)│  │  (filesystem_writer.py)          │   │
│  └──────────────┘  └──────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   OpenAI GPT-4                              │
│                   (LangChain)                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Generated Project Output                       │
│              (generated_projects/)                          │
│                                                             │
│  project_name/                                             │
│  ├── main.py                                               │
│  ├── requirements.txt                                      │
│  ├── README.md                                             │
│  ├── ARCHITECTURE.md                                       │
│  ├── tests/                                                │
│  └── ...                                                   │
│                                                             │
│  project_name.zip                                          │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI Server (`main.py`)

**Responsibilities:**
- Expose REST API endpoints
- Handle HTTP requests/responses
- Manage API lifecycle (startup/shutdown)
- Coordinate background tasks (zip creation)

**Key Features:**
- Async request handling
- Automatic API documentation (Swagger/ReDoc)
- File streaming for downloads
- Background task processing

### 2. Multi-Agent Pipeline (`core/pipeline.py`)

**Responsibilities:**
- Orchestrate agent execution
- Manage workflow state
- Handle errors and logging
- Coordinate file generation

**Key Components:**

#### WorkflowState
```python
class WorkflowState(TypedDict):
    user_prompt: str              # Input from user
    requirements: Dict            # Extracted requirements
    research_plan: Dict           # Research strategy
    market_research: Dict         # Market analysis
    implementation_plan: Dict     # Architecture plan
    documentation_research: Dict  # Tech docs
    code_files: Dict[str, str]   # Generated code
    review_results: Dict          # Code review
    test_results: Dict            # Test results
    documentation_files: Dict     # Docs
    project_path: str             # Output location
    error: str                    # Error messages
```

#### LangGraph Workflow
- **Nodes**: Each agent is a node
- **Edges**: Define execution order
- **Entry Point**: PromptAnalyzerAgent
- **End Point**: After filesystem write

### 3. Agent Modules (`core/agents.py`)

#### Agent Base Pattern
```python
class AgentName:
    SYSTEM_PROMPT = """Agent-specific instructions"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def execute(self, inputs) -> outputs:
        # Agent logic
        messages = [SystemMessage(...), HumanMessage(...)]
        response = self.llm.invoke(messages)
        return parsed_response
```

#### Agent Responsibilities

1. **PromptAnalyzerAgent**
   - Input: User prompt (string)
   - Output: Structured requirements (JSON)
   - Extracts: project name, features, tech stack, constraints

2. **ResearchPlannerAgent**
   - Input: Requirements
   - Output: Research plan
   - Plans: market research, documentation needs

3. **MarketResearcherAgent**
   - Input: Research plan, requirements
   - Output: Market insights
   - Provides: competitor analysis, trends, recommendations

4. **ImplementationPlannerAgent**
   - Input: Requirements, market research
   - Output: Implementation plan
   - Defines: architecture, file structure, modules

5. **DocumentationResearcherAgent**
   - Input: Implementation plan
   - Output: Technical documentation
   - Gathers: framework docs, API references, examples

6. **CodeImplementerAgent**
   - Input: Implementation plan, requirements, docs
   - Output: Code files
   - Generates: Complete source code files

7. **CodeReviewerAgent**
   - Input: Code files, requirements
   - Output: Review report
   - Checks: quality, security, best practices

8. **CodeTesterAgent**
   - Input: Code files, requirements
   - Output: Test files and results
   - Creates: Unit tests, integration tests

9. **DocumentationWriterAgent**
   - Input: Requirements, implementation plan, code
   - Output: Documentation files
   - Writes: README, ARCHITECTURE, USAGE, CONTRIBUTING

### 4. Specialized Modules

#### ProjectBuilder (`core/builder.py`)
- Generates actual code using LLM
- Handles multiple file types
- Creates project structure
- Manages dependencies

#### CodeReviewer (`core/reviewer.py`)
- Reviews code against best practices
- Identifies security issues
- Scores code quality
- Suggests improvements

#### CodeTester (`core/tester.py`)
- Generates pytest test files
- Simulates test execution
- Provides coverage metrics
- Creates test reports

#### DocumentationWriter (`core/doc_writer.py`)
- Generates markdown documentation
- Creates comprehensive READMEs
- Writes architecture docs
- Produces usage guides

#### FilesystemWriter (`core/filesystem_writer.py`)
- Writes files to disk
- Creates directory structures
- Generates zip archives
- Provides project summaries

## Data Flow

### Request Flow
```
1. HTTP POST /build → FastAPI endpoint
2. Validate request and API key
3. Initialize MultiAgentPipeline
4. Create WorkflowState with user_prompt
5. Execute LangGraph workflow
6. Each agent updates state sequentially
7. FilesystemWriter writes output
8. Return BuildResponse to client
```

### State Evolution
```
Initial State:
{
  user_prompt: "Create a REST API...",
  requirements: {},
  ...
}

After Step 1 (Prompt Analyzer):
{
  user_prompt: "Create a REST API...",
  requirements: {
    project_name: "rest_api",
    features: [...],
    tech_stack: [...]
  },
  ...
}

After Step 6 (Code Implementer):
{
  ...
  code_files: {
    "main.py": "code content...",
    "models.py": "code content...",
    ...
  },
  ...
}

Final State:
{
  ...
  project_path: "generated_projects/rest_api",
  error: ""
}
```

## Design Patterns

### 1. Chain of Responsibility
Each agent processes state and passes to next agent.

### 2. Strategy Pattern
Different code generation strategies for different project types.

### 3. Factory Pattern
`ProjectBuilder` creates appropriate file structures.

### 4. State Pattern
`WorkflowState` maintains system state throughout pipeline.

### 5. Observer Pattern
Logging and monitoring throughout execution.

## Error Handling

### Error Propagation
```python
try:
    result = agent.execute(state)
    state["field"] = result
except Exception as e:
    state["error"] = f"Step X error: {str(e)}"
    # Continue to next step
```

### Fallback Mechanisms
- If LLM fails to return valid JSON, use fallback structures
- If code generation fails, create basic template
- Errors are logged but don't stop pipeline

## Scalability Considerations

### Current Limitations
- Sequential execution (no parallelization)
- Single OpenAI API key
- Local file storage only

### Future Improvements
- Parallel agent execution where possible
- Multiple LLM provider support
- Cloud storage integration (S3, GCS)
- Caching of common patterns
- WebSocket for real-time progress updates

## Security

### API Key Management
- Environment variable storage
- Per-request key override option
- Never logged or exposed

### Code Generation Safety
- LLM-generated code reviewed by agent
- No arbitrary code execution
- Sandboxed file writing

### File System
- Restricted to `generated_projects/` directory
- Path sanitization
- Zip file size limits

## Performance

### Typical Execution Time
- Simple CLI tool: 2-3 minutes
- Web API: 3-5 minutes
- Complex application: 5-10 minutes

### Bottlenecks
1. OpenAI API latency (network + processing)
2. Sequential agent execution
3. Large code file generation

### Optimization Strategies
- Prompt engineering for concise responses
- Caching common architectural patterns
- Streaming responses where possible

## Monitoring and Logging

### Log Levels
- Console output with emoji indicators
- Step-by-step progress tracking
- Error capture and reporting

### Metrics
- Total execution time
- Per-agent execution time
- File count and size
- Code review scores
- Test coverage

## Deployment

### Local Development
```bash
python main.py
```

### Production Deployment
```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Using gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing Strategy

### Unit Tests
Test individual agents and modules in isolation.

### Integration Tests
Test complete pipeline with mock LLM responses.

### End-to-End Tests
Test actual project generation with real API.

## Maintenance

### Adding New Features
1. Define new agent in `agents.py`
2. Add node to pipeline in `pipeline.py`
3. Update `WorkflowState` if needed
4. Add tests for new functionality

### Updating Prompts
Modify `SYSTEM_PROMPT` constants in agent classes.

### Changing LLM
Update `ChatOpenAI` initialization in `pipeline.py`.

---

**Last Updated**: November 2025  
**Version**: 1.0.0
