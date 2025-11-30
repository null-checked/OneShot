# Architect-Based Multi-Agent Pipeline

## Overview

The new architect-based pipeline is a redesigned backend implementation that uses an intelligent architect agent to dynamically define and coordinate the project generation process.

## Key Improvements Over Previous Implementation

### Previous Implementation (10-Step Fixed Pipeline)
- ✗ Fixed 10-step sequential workflow
- ✗ All agents executed regardless of project needs
- ✗ Tests were simulated, not actually executed
- ✗ No retry logic for failed agents
- ✗ No dynamic adaptation to project complexity

### New Implementation (Architect-Based Pipeline)
- ✅ **Architect Agent** analyzes prompt and defines implementation structure
- ✅ **Dynamic Worker Agents** created based on project needs (2-6 agents)
- ✅ **Real Code Execution** - tests actually run and get real output
- ✅ **Retry Logic** - up to 5 retries per agent if errors occur
- ✅ **Success Criteria Validation** - verifies project meets requirements
- ✅ **Adaptive** - agent count and structure adapts to project complexity

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Prompt                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 1: Architect Agent                                     │
│  • Analyzes user prompt                                      │
│  • Defines worker agents needed (name, role, instructions)   │
│  • Defines tests to perform                                  │
│  • Defines success criteria                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 2: Dynamic Worker Agents                               │
│  • Agents initialized based on architect's plan              │
│  • Each agent generates specific files                       │
│  • Retry logic: up to 5 attempts per agent                   │
│  • Validation after each attempt                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3: Write to Filesystem                                 │
│  • All files written to project directory                    │
│  • Standard files added (README, requirements.txt, .gitignore)│
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4: Testing Agent                                       │
│  • Executes tests defined by architect                       │
│  • Real code execution with actual output                    │
│  • Syntax checks, unit tests, integration tests              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 5: Verify Success Criteria                             │
│  • Validates all criteria are met                            │
│  • Returns final success/failure status                      │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Architect Agent (`src/core/architect_agent.py`)

**Responsibility**: Analyzes user prompt and creates implementation plan

**Output Structure**:
```python
{
    "project_name": "my_project",
    "description": "Brief description",
    "tech_stack": ["python", "flask"],
    "entry_point": "main.py",
    "agents": [
        {
            "name": "backend_api",
            "role": "Implement REST API",
            "instructions": "Detailed step-by-step instructions",
            "files_to_generate": ["main.py", "routes.py"]
        }
    ],
    "tests": [
        {
            "test_name": "syntax_check",
            "test_type": "syntax",
            "description": "Verify Python syntax",
            "test_command": "python -m py_compile {file}"
        }
    ],
    "success_criteria": [
        {
            "criteria_name": "runs_without_errors",
            "description": "Application starts successfully",
            "verification_method": "Execute entry point"
        }
    ]
}
```

### 2. Dynamic Worker Agent (`src/core/dynamic_worker.py`)

**Responsibility**: Generates code files based on custom instructions

**Features**:
- Dynamically initialized with architect's instructions
- Generates complete, functional code (no placeholders)
- Returns dictionary mapping file paths to content

### 3. Code Executor (`src/core/code_executor.py`)

**Responsibility**: Safely executes Python code and captures real output

**Features**:
- Subprocess execution with timeout (default 30s)
- Captures stdout, stderr, and exit code
- Syntax checking without execution
- Dependency installation (pip)
- Custom command execution

### 4. Testing Agent (`src/core/testing_agent.py`)

**Responsibility**: Executes tests and validates success criteria

**Test Types**:
- **Syntax**: Python syntax validation (py_compile)
- **Unit**: Unit test execution
- **Integration**: Integration test execution
- **Functional**: Functional/end-to-end testing

**Features**:
- Real code execution (not simulated)
- Multiple test types supported
- Success criteria verification

### 5. Architect Pipeline (`src/core/architect_pipeline.py`)

**Responsibility**: Orchestrates the entire workflow

**Features**:
- Retry logic (configurable, default 5 retries)
- File validation before acceptance
- Automatic standard file generation (README, requirements.txt, .gitignore)
- Progress tracking and reporting

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional - Pipeline Configuration
USE_ARCHITECT_PIPELINE=true  # Set to false to use old pipeline
MAX_AGENT_RETRIES=5          # Maximum retries per agent
```

### Settings (`src/settings.py`)

```python
class Settings(BaseSettings):
    # Pipeline configuration
    USE_ARCHITECT_PIPELINE: bool = True  # Use architect pipeline
    MAX_AGENT_RETRIES: int = 5           # Max retries per agent
```

## Usage

### 1. CLI Testing

Test the new pipeline directly from command line:

```bash
# Interactive mode
python test_cli.py

# Direct prompt
python test_cli.py --prompt "Create a Flask REST API for managing books"

# With verbose output
python test_cli.py --prompt "Build a CLI calculator" --verbose

# Save results to file
python test_cli.py --prompt "Simple todo app" --save-results results.json

# Custom retries
python test_cli.py --prompt "Web scraper" --retries 3
```

### 2. WebSocket API

The pipeline integrates seamlessly with the existing WebSocket API:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Send build request
ws.send(JSON.stringify({
    action: 'build',
    data: {
        prompt: 'Create a Flask REST API for managing todos'
    }
}));

// Receive progress updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'progress') {
        console.log(`Step ${data.step}: ${data.message}`);
    }

    if (data.type === 'complete') {
        console.log('Project generated:', data.data);
        // data.data contains:
        // - project_name
        // - project_path
        // - files_count
        // - tests_passed
        // - tests_total
        // - agents_used
        // - all_criteria_met
    }
};
```

### 3. Programmatic Usage

```python
from src.core.architect_pipeline import ArchitectPipeline

# Initialize pipeline
pipeline = ArchitectPipeline(
    openai_api_key="your-api-key",
    max_retries=5
)

# Run pipeline
result = pipeline.run("Create a Flask REST API for managing books")

# Access results
print(f"Project: {result['plan']['project_name']}")
print(f"Path: {result['project_path']}")
print(f"Success: {result['success']}")
print(f"Tests passed: {result['test_results']['tests_passed']}")
```

## Retry Logic

The pipeline includes sophisticated retry logic:

1. **Agent Execution**:
   - Each worker agent gets up to 5 attempts (configurable)
   - After each attempt, generated files are validated
   - If validation fails, error feedback is provided to agent
   - Agent retries with error context

2. **Validation Checks**:
   - All required files present
   - Files not empty (>10 characters)
   - Sufficient code (>3 code lines for Python files)
   - No placeholder patterns (TODO, NotImplementedError, etc.)

3. **Test Execution**:
   - Tests executed with real output
   - If tests fail, results are captured
   - No automatic retries for test failures (by design)

## Testing

### Test Types

The architect can define various test types:

#### 1. Syntax Check
```python
{
    "test_name": "syntax_check",
    "test_type": "syntax",
    "description": "Verify Python syntax is valid",
    "test_command": "python -m py_compile {file}"
}
```

#### 2. Unit Tests
```python
{
    "test_name": "unit_tests",
    "test_type": "unit",
    "description": "Run unit tests",
    "test_command": "python -m pytest tests/ -v"
}
```

#### 3. Functional Tests
```python
{
    "test_name": "app_runs",
    "test_type": "functional",
    "description": "Verify app starts without errors",
    "test_command": "python {entry_point} --test"
}
```

### Success Criteria

The architect defines success criteria that are verified:

```python
{
    "criteria_name": "all_files_created",
    "description": "All required files exist",
    "verification_method": "Check file existence"
}
```

Common verification methods:
- File existence checks
- Syntax validation
- Execution without errors
- Test passage

## Output Structure

The pipeline returns a comprehensive result dictionary:

```python
{
    "user_prompt": "Original user prompt",

    "plan": {
        "project_name": "my_project",
        "description": "...",
        "tech_stack": [...],
        "entry_point": "main.py",
        "agents": [...],
        "tests": [...],
        "success_criteria": [...]
    },

    "agent_results": [
        {
            "name": "agent_name",
            "success": true,
            "attempts": 2,
            "files_generated": 3
        }
    ],

    "files_generated": 10,
    "project_path": "/path/to/generated_projects/my_project",

    "test_results": {
        "success": true,
        "tests_run": 3,
        "tests_passed": 3,
        "tests_failed": 0,
        "results": [...]
    },

    "criteria_results": {
        "all_criteria_met": true,
        "criteria_results": [
            {
                "criteria_name": "...",
                "description": "...",
                "met": true
            }
        ]
    },

    "success": true  // Overall success status
}
```

## Switching Between Pipelines

You can easily switch between the old and new pipeline:

### Option 1: Environment Variable
```bash
# Use new architect pipeline
export USE_ARCHITECT_PIPELINE=true

# Use old multi-agent pipeline
export USE_ARCHITECT_PIPELINE=false
```

### Option 2: Settings File
```python
# In src/settings.py
class Settings(BaseSettings):
    USE_ARCHITECT_PIPELINE: bool = True  # Change to False for old pipeline
```

## Examples

### Example 1: Simple CLI Tool
```bash
python test_cli.py --prompt "Create a Python CLI calculator that supports basic operations"
```

**Architect Will Define**:
- 2 agents: main_app, tests
- 1 syntax test
- Success criteria: runs without errors

### Example 2: REST API
```bash
python test_cli.py --prompt "Build a Flask REST API for a book library with CRUD operations"
```

**Architect Will Define**:
- 3-4 agents: api_routes, database_models, main_app, tests
- 2-3 tests: syntax, unit tests, API endpoint test
- Success criteria: API starts, endpoints respond

### Example 3: Data Processing
```bash
python test_cli.py --prompt "Create a CSV processor that filters and transforms data"
```

**Architect Will Define**:
- 2-3 agents: processor, cli_interface, tests
- 2 tests: syntax, functional test with sample CSV
- Success criteria: processes sample file successfully

## Troubleshooting

### Issue: "Max retries reached"

**Cause**: Agent couldn't generate valid code after 5 attempts

**Solutions**:
- Increase retries: `--retries 10`
- Simplify prompt
- Check that tech stack is appropriate for task

### Issue: "Tests failed"

**Cause**: Generated code has actual errors

**Solutions**:
- Check test output in verbose mode: `--verbose`
- Examine generated files in project directory
- Review test commands in architect's plan

### Issue: "Python module not found"

**Cause**: Required dependencies not installed

**Solutions**:
- Install dependencies from generated requirements.txt
- Add required libraries to prompt

## Performance

**Typical Generation Times**:
- Simple CLI tool: 30-60 seconds
- REST API: 1-3 minutes
- Complex multi-component app: 3-5 minutes

**Factors Affecting Speed**:
- Number of agents defined by architect
- Retry attempts needed
- Test execution time
- LLM response time

## Best Practices

1. **Clear Prompts**: Be specific about requirements
2. **Specify Tech Stack**: Mention frameworks/libraries if needed
3. **Test Early**: Use CLI for testing before frontend integration
4. **Review Output**: Check generated code and tests
5. **Adjust Retries**: Lower for faster iteration, higher for complex projects

## Future Enhancements

Potential improvements:
- [ ] Parallel agent execution
- [ ] Incremental file generation with streaming
- [ ] Agent collaboration and communication
- [ ] Learn from previous successes
- [ ] Custom agent templates
- [ ] Docker containerization for safer execution
- [ ] More sophisticated test generation

---

**Created**: 2025-11-30
**Last Updated**: 2025-11-30
**Version**: 1.0.0
