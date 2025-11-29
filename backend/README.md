# Multi-Agent Software Factory Generator

🤖 An AI-powered software project generator using **LangChain**, **LangGraph**, and multi-agent architecture.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green)
![LangChain](https://img.shields.io/badge/LangChain-0.1.6-orange)

## 🌟 Overview

The Multi-Agent Software Factory is a sophisticated system that generates complete, production-ready software projects from natural language descriptions. It orchestrates 9 specialized AI agents that work together to analyze requirements, conduct research, write code, review quality, generate tests, and create comprehensive documentation.

## 🏗️ Architecture

### 9-Step Workflow

The system follows a sequential pipeline of 9 agents:

1. **Prompt Analyzer Agent** - Extracts structured requirements from user input
2. **Research Planner Agent** - Plans what research needs to be conducted
3. **Market Researcher Agent** - Analyzes existing solutions and best practices
4. **Implementation Planner Agent** - Creates detailed architecture and file structure
5. **Documentation Researcher Agent** - Gathers technical documentation for chosen stack
6. **Code Implementer Agent** - Generates actual project files and code
7. **Code Reviewer Agent** - Reviews code quality, security, and best practices
8. **Code Tester Agent** - Generates and executes unit/integration tests
9. **Documentation Writer Agent** - Creates README, architecture docs, and guides

### Technology Stack

- **Backend**: FastAPI (async REST API)
- **AI Framework**: LangChain + LangGraph
- **LLM**: OpenAI GPT-4
- **Orchestration**: LangGraph StateGraph
- **File Generation**: Custom Filesystem Writer

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd multi-agent-python
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Usage

### Endpoint: POST /build

Generate a complete software project from a prompt.

**Request:**
```json
{
  "prompt": "Create a REST API for a todo list with FastAPI and SQLite",
  "openai_api_key": "sk-..." // optional if set in .env
}
```

**Response:**
```json
{
  "status": "success",
  "project_name": "todo_api",
  "project_path": "generated_projects/todo_api",
  "files_count": 12,
  "download_url": "/download/todo_api",
  "requirements": {
    "project_name": "todo_api",
    "description": "REST API for todo list management",
    "features": ["CRUD operations", "SQLite database", "API documentation"],
    "tech_stack": ["fastapi", "sqlalchemy", "sqlite"]
  },
  "review_score": 87.5,
  "test_summary": {
    "total_tests": 15,
    "passed": 15,
    "failed": 0
  }
}
```

### Other Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /projects` - List all generated projects
- `GET /download/{project_name}` - Download project as zip

## 💻 Example Usage

### Using the Python Client

```python
from example_client import SoftwareFactoryClient

client = SoftwareFactoryClient("http://localhost:8000")

# Build a project
result = client.build_project(
    prompt="Create a CLI calculator with history support"
)

print(f"Project generated: {result['project_name']}")
print(f"Location: {result['project_path']}")

# Download the project
client.download_project(result['project_name'])
```

### Using curl

```bash
curl -X POST "http://localhost:8000/build" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a web scraper for news articles"
  }'
```

### Using Python requests

```python
import requests

response = requests.post(
    "http://localhost:8000/build",
    json={
        "prompt": "Create a data analysis tool for CSV files with pandas"
    }
)

result = response.json()
print(f"Generated: {result['project_name']}")
```

## 📁 Project Structure

```
multi-agent-python/
├── main.py                    # FastAPI server entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── example_client.py         # Example API client
│
├── core/                     # Core modules
│   ├── __init__.py
│   ├── agents.py            # All 9 agent classes
│   ├── pipeline.py          # LangGraph orchestration
│   ├── builder.py           # Code generation agent
│   ├── reviewer.py          # Code review agent
│   ├── tester.py            # Test generation agent
│   ├── doc_writer.py        # Documentation agent
│   └── filesystem_writer.py # File I/O operations
│
└── generated_projects/       # Output directory (created on first run)
    ├── project1/
    ├── project2/
    └── project1.zip
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4              # Optional, defaults to gpt-4
OPENAI_TEMPERATURE=0.7          # Optional, defaults to 0.7
```

### Customization

You can customize the agents by modifying their system prompts in `core/agents.py`:

```python
class PromptAnalyzerAgent:
    SYSTEM_PROMPT = """Your custom prompt here..."""
```

## 📊 Generated Project Contents

Each generated project includes:

- **Source Code**: Complete, runnable Python code with proper structure
- **Tests**: Unit and integration tests using pytest
- **Documentation**:
  - `README.md` - Project overview and usage
  - `ARCHITECTURE.md` - System design and structure
  - `USAGE.md` - Detailed usage guide
  - `CONTRIBUTING.md` - Contribution guidelines
- **Configuration**:
  - `requirements.txt` - Python dependencies
  - `.env.example` - Environment template
  - `.gitignore` - Git exclusions

## 🧪 Testing

The system includes automated testing at multiple levels:

1. **Unit Tests**: Each module is tested independently
2. **Integration Tests**: Full pipeline execution tests
3. **Generated Project Tests**: Tests for the generated code itself

Run tests:
```bash
pytest tests/
```

## 🎯 Use Cases

### 1. Rapid Prototyping
Quickly generate functional prototypes from high-level descriptions.

### 2. Learning & Exploration
Generate example projects to learn new frameworks and patterns.

### 3. Boilerplate Generation
Create starter projects with best practices built-in.

### 4. Code Examples
Generate working code examples for documentation.

## 🔍 How It Works

### Pipeline Flow

```
User Prompt
    ↓
[1] Prompt Analyzer → Requirements JSON
    ↓
[2] Research Planner → Research Plan
    ↓
[3] Market Researcher → Market Insights
    ↓
[4] Implementation Planner → Architecture Plan
    ↓
[5] Documentation Researcher → Tech Docs
    ↓
[6] Code Implementer → Source Files
    ↓
[7] Code Reviewer → Review Report
    ↓
[8] Code Tester → Test Files + Results
    ↓
[9] Documentation Writer → Documentation Files
    ↓
[10] Filesystem Writer → Disk Output
    ↓
Generated Project (zip available)
```

### State Management

The pipeline uses a `WorkflowState` object that flows through all agents:

```python
class WorkflowState(TypedDict):
    user_prompt: str
    requirements: Dict[str, Any]
    research_plan: Dict[str, Any]
    market_research: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    documentation_research: Dict[str, Any]
    code_files: Dict[str, str]
    review_results: Dict[str, Any]
    test_results: Dict[str, Any]
    documentation_files: Dict[str, str]
    project_path: str
    error: str
```

## 🛠️ Development

### Adding a New Agent

1. Define agent class in `core/agents.py`
2. Add system prompt as class constant
3. Implement `execute()` method
4. Add node to pipeline in `core/pipeline.py`
5. Connect to graph with edges

### Extending Functionality

- **Custom LLMs**: Modify `ChatOpenAI` initialization in `pipeline.py`
- **Additional Steps**: Add new nodes to the LangGraph workflow
- **Custom Tools**: Extend `FilesystemWriter` or create new tool modules

## 📝 Examples

### Example 1: CLI Tool
```python
prompt = "Create a command-line password generator with customizable length and character sets"
```

### Example 2: Web API
```python
prompt = "Create a REST API for a blog with posts, comments, and user authentication using FastAPI and PostgreSQL"
```

### Example 3: Data Processing
```python
prompt = "Create a data pipeline that reads CSV files, cleans data, performs analysis, and exports visualizations"
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com)
- Orchestrated with [LangGraph](https://langchain-ai.github.io/langgraph/)
- Powered by [OpenAI GPT-4](https://openai.com)

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check the `/docs` endpoint for API documentation
- Review the generated project files for examples

---

**Generated with ❤️ by the Multi-Agent Software Factory**

*Transforming ideas into code, one agent at a time.*
