# Quick Start Guide - Architect Pipeline

## Setup (5 minutes)

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the `backend` directory:
```bash
# Required
OPENAI_API_KEY=your-api-key-here

# Optional - use new architect pipeline (default: true)
USE_ARCHITECT_PIPELINE=true
MAX_AGENT_RETRIES=5
```

### 3. Test the CLI
```bash
python test_cli.py --help
```

## Quick Test (2 minutes)

### Test 1: Simple Calculator
```bash
python test_cli.py --prompt "Create a simple CLI calculator in Python"
```

Expected output:
- 2-3 agents created
- 3-5 files generated
- Syntax tests pass
- Project in `generated_projects/`

### Test 2: Flask API (Verbose)
```bash
python test_cli.py --prompt "Build a Flask REST API for managing todos" --verbose
```

Expected output:
- 3-4 agents created
- 6-8 files generated
- Multiple tests run
- Detailed test results shown

## Using with Frontend

### 1. Start the Backend Server
```bash
cd backend
uvicorn src.main:app --reload
```

### 2. Verify WebSocket Connection
```bash
# Test WebSocket endpoint
wscat -c ws://localhost:8000/ws
```

### 3. Send Build Request
```json
{
    "action": "build",
    "data": {
        "prompt": "Create a Flask REST API for managing books"
    }
}
```

### 4. Receive Progress Updates
You'll receive messages like:
```json
{"type": "progress", "step": 1, "message": "📐 Architect Agent - Analyzing..."}
{"type": "progress", "step": 2, "message": "💼 Initializing worker agents..."}
...
{"type": "complete", "data": {"project_name": "...", "files_count": 8, ...}}
```

## CLI Examples

### Basic Usage
```bash
# Interactive mode
python test_cli.py

# Direct prompt
python test_cli.py -p "Your project description"
```

### Advanced Usage
```bash
# Custom output directory
python test_cli.py -p "Simple web scraper" -o ./my_projects

# More retries for complex projects
python test_cli.py -p "Complex multi-service app" -r 10

# Verbose output + save results
python test_cli.py -p "Data processor" -v -s results.json

# Quick test with fewer retries
python test_cli.py -p "Hello world app" -r 2
```

## Understanding Output

### Success Output
```
🏗️  Architect-Based Multi-Agent Pipeline - Starting
===============================================================

📐 Step 1: Architect Agent - Analyzing and Planning...
  Project: my_calculator
  Agents to create: 2
  Tests to perform: 1
  Success criteria: 2
    Agent 1: main_implementation - Core calculator logic
    Agent 2: cli_interface - Command-line interface

💼 Step 2: Initializing 2 Worker Agents...
  Agent 1/2: main_implementation
    ✓ Success after 1 attempt(s)
  Agent 2/2: cli_interface
    ✓ Success after 1 attempt(s)

💾 Step 3: Writing 5 files to disk...
  ✓ Project written to: generated_projects/my_calculator

🧪 Step 4: Running 1 tests...
  ✓ syntax_check PASSED

✅ Step 5: Verifying 2 success criteria...
  ✓ files_generated: All required files created
  ✓ runs_without_errors: Application runs successfully

✅ Pipeline completed successfully!
```

### Failure Output
```
⚠️  Validation failed: File contains placeholder code
    Attempt 2/5...
...
⚠️  Max retries (5) reached
✗ syntax_check FAILED
  Error: SyntaxError: invalid syntax

⚠️  Pipeline completed with some issues
```

## Switching Between Pipelines

### To use NEW architect pipeline:
```bash
# In .env file
USE_ARCHITECT_PIPELINE=true
```

### To use OLD multi-agent pipeline:
```bash
# In .env file
USE_ARCHITECT_PIPELINE=false
```

## Common Issues

### Issue: "OPENAI_API_KEY not found"
**Solution**: Add to `.env` file:
```bash
OPENAI_API_KEY=sk-...
```

### Issue: "Module not found"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Tests failed"
**Solution**: Check verbose output:
```bash
python test_cli.py -p "your prompt" -v
```

### Issue: "Max retries reached"
**Solution**: Increase retries or simplify prompt:
```bash
python test_cli.py -p "simpler prompt" -r 10
```

## What Gets Generated

For each project, you'll get:

### Files
- All code files defined by architect
- `README.md` - Project documentation
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore patterns

### Metadata
- Project path
- File count
- Test results
- Success criteria validation
- Agent execution details

### Example Structure
```
generated_projects/
└── my_calculator/
    ├── main.py
    ├── calculator.py
    ├── cli.py
    ├── tests/
    │   └── test_calculator.py
    ├── README.md
    ├── requirements.txt
    └── .gitignore
```

## Testing Before Frontend Integration

### 1. Run CLI Test
```bash
python test_cli.py -p "Simple test app" -v
```

### 2. Check Generated Files
```bash
cd generated_projects/your_project
ls -la
cat README.md
```

### 3. Verify Code Works
```bash
cd generated_projects/your_project
pip install -r requirements.txt
python main.py
```

### 4. Run Tests (if generated)
```bash
cd generated_projects/your_project
pytest tests/
```

## Next Steps

1. ✅ Test CLI works
2. ✅ Generate sample project
3. ✅ Verify files are correct
4. ✅ Start backend server
5. ✅ Test WebSocket connection
6. ✅ Integrate with frontend

## Resources

- **Full Documentation**: `ARCHITECT_PIPELINE.md`
- **API Docs**: `http://localhost:8000/docs` (when server is running)
- **Example Projects**: `generated_projects/`

## Support

If you encounter issues:
1. Check `ARCHITECT_PIPELINE.md` for detailed information
2. Run with `--verbose` flag for detailed output
3. Verify `.env` configuration
4. Check that all dependencies are installed

---

**Ready to start?** Run:
```bash
python test_cli.py
```
