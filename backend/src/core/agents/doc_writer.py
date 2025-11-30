"""
Documentation Writer Module - Generates project documentation
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from deepagents import create_deep_agent
import json
from datetime import datetime

from src.core.tools.search_tool import internet_search


class DocumentationWriter:
    """
    Generates comprehensive project documentation including README,
    architecture docs, API docs, and usage guides.
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "DocumentationWriter"

    def generate_documentation(self,
                               requirements: Dict[str, Any],
                               implementation_plan: Dict[str, Any],
                               files: Dict[str, str]) -> Dict[str, str]:
        """
        Generate all documentation files.
        
        Args:
            requirements: Project requirements
            implementation_plan: Architecture plan
            files: Generated code files
            
        Returns:
            Dictionary mapping doc file paths to contents
        """

        docs = {}

        # Generate README.md
        docs['README.md'] = self._generate_readme(
            requirements, implementation_plan)

        # Generate ARCHITECTURE.md
        docs['ARCHITECTURE.md'] = self._generate_architecture_doc(
            implementation_plan)

        # Generate USAGE.md
        docs['USAGE.md'] = self._generate_usage_guide(requirements, files)

        # Generate CONTRIBUTING.md
        docs['CONTRIBUTING.md'] = self._generate_contributing_guide()

        return docs

    def _ensure_json_serializable(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._ensure_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._ensure_json_serializable(elem) for elem in obj]
        elif hasattr(obj, 'content'): # Handle LangChain message objects
            return obj.content
        else:
            try:
                json.dumps(obj)
                return obj
            except TypeError:
                return str(obj) # Fallback to string representation for other non-serializable types

    def _generate_readme(self, requirements: Dict[str, Any],
                         implementation_plan: Dict[str, Any]) -> str:
        """Generate README.md using LLM."""

        system_prompt = """You are a technical writer. Generate a comprehensive README.md
        in Markdown format with:
        
        1. Project title and description
        2. Features list
        3. Installation instructions
        4. Quick start guide
        5. Usage examples
        6. Configuration
        7. Contributing
        8. License
        
        Make it professional and clear.
        """

        # Ensure inputs are JSON-serializable
        serializable_requirements = self._ensure_json_serializable(requirements)
        serializable_implementation_plan = self._ensure_json_serializable(implementation_plan)

        user_prompt = f"""Generate README.md for:

Project: {serializable_requirements.get('project_name', 'Project')}
Description: {serializable_requirements.get('description', '')}
Features: {json.dumps(serializable_requirements.get('features', []), indent=2)}
Tech Stack: {json.dumps(serializable_implementation_plan.get('tech_stack_final', []), indent=2)}
Platform: {serializable_requirements.get('platform', 'general')}
"""

        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt="", name=self.name,debug=True) # System prompt passed in messages
        print("Generating README.md with DocumentationWriter agent.")
        response = deep_agent.invoke(
            {
                "messages" : [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    { 
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
        )
        content = response
        if len(content) < 100:
            return self._generate_fallback_readme(requirements)
        return content

    def _generate_fallback_readme(self, requirements: Dict[str, Any]) -> str:
        """Generate basic README if LLM fails."""

        project_name = requirements.get('project_name', 'Generated Project')
        description = requirements.get(
            'description', 'A generated software project')
        features = requirements.get('features', [])

        readme = f"""# {project_name}

{description}

## Features

{chr(10).join(f'- {feature}' for feature in features) if features else '- Core functionality'}

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name.lower().replace(' ', '-')}

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
# Import the main module
import main

# Run the application
main.main()
```

## Configuration

Copy `.env.example` to `.env` and configure your environment variables.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

---
Generated on {datetime.now().strftime('%Y-%m-%d')} by Multi-Agent Software Factory
"""
        return readme

    def _generate_architecture_doc(self, implementation_plan: Dict[str, Any]) -> str:
        """Generate architecture documentation."""

        architecture = implementation_plan.get(
            'architecture', 'Modular architecture')
        modules = implementation_plan.get('modules', [])

        doc = f"""# Architecture Documentation

## Overview

{architecture}

## System Architecture

### Modules

"""

        for module in modules:
            name = module.get('name', 'Module')
            desc = module.get('description', 'No description')
            deps = module.get('dependencies', [])

            doc += f"""#### {name}

{desc}

Dependencies: {', '.join(deps) if deps else 'None'}

"""

        doc += f"""
## File Structure

```
{self._format_file_structure(implementation_plan.get('file_structure', {}))}
```

## Design Patterns

- Modular design for maintainability
- Separation of concerns
- Clear interface definitions

## Technology Stack

{chr(10).join(f'- {tech}' for tech in implementation_plan.get('tech_stack_final', []))}

---
Generated by Multi-Agent Software Factory
"""

        return doc

    def _format_file_structure(self, file_structure: Dict[str, str]) -> str:
        """Format file structure as tree."""

        if not file_structure:
            return "project/\n  └── main.py"

        lines = ["project/"]
        for path, desc in file_structure.items():
            lines.append(f"  ├── {path}")

        return "\n".join(lines)

    def _generate_usage_guide(self, requirements: Dict[str, Any],
                              files: Dict[str, str]) -> str:
        """Generate usage guide."""

        project_name = requirements.get('project_name', 'Project')

        guide = f"""# Usage Guide - {project_name}

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

```bash
python main.py
```

## Features and Examples

"""

        features = requirements.get('features', [])
        for feature in features:
            guide += f"""### {feature}

Example usage for {feature}:

```python
# TODO: Add specific example
```

"""

        guide += """
## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
2. **Configuration errors**: Check your .env file

## Support

For issues and questions, please check the documentation or open an issue.

---
Generated by Multi-Agent Software Factory
"""

        return guide

    def _generate_contributing_guide(self) -> str:
        """Generate contributing guidelines."""

        return """# Contributing Guidelines

## How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Add docstrings to all functions and classes
- Write unit tests for new features

## Testing

Run tests before submitting:

```bash
pytest tests/
```

## Code Review Process

All submissions require review before merging.

Thank you for contributing!
"""
