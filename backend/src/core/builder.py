"""
Code Builder Module - Generates actual project files
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
import json


class ProjectBuilder:
    """
    Generates actual code files based on implementation plan.
    Uses LLM to generate production-ready code.
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def generate_project_files(self,
                               implementation_plan: Dict[str, Any],
                               requirements: Dict[str, Any],
                               documentation: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all project files based on the implementation plan.
        
        Args:
            implementation_plan: Architecture and file structure
            requirements: Project requirements
            documentation: Tech stack documentation
            
        Returns:
            Dictionary mapping file paths to file contents
        """
        files = {}

        # Generate main application files
        files.update(self._generate_main_files(
            requirements, implementation_plan))

        # Generate requirements.txt
        files['requirements.txt'] = self._generate_requirements(
            implementation_plan)

        # Generate configuration files
        files.update(self._generate_config_files(requirements))

        # Generate .gitignore
        files['.gitignore'] = self._generate_gitignore()

        return files

    def _generate_main_files(self, requirements: Dict[str, Any],
                             implementation_plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate main application code files."""

        platform = requirements.get('platform', 'web')
        project_name = requirements.get('project_name', 'app')
        description = requirements.get('description', '')
        features = requirements.get('features', [])

        system_prompt = f"""You are an expert software developer. Generate production-ready code
        for a {platform} application.
        
        Project: {project_name}
        Description: {description}
        Features: {', '.join(features)}
        
        Generate complete, runnable code with:
        - Proper imports and error handling
        - Type hints and docstrings
        - Clean, maintainable structure
        - Comments explaining key logic
        
        Return ONLY valid JSON in this format:
        {{
            "file_path": "complete file content",
            ...
        }}
        """

        user_prompt = f"""Generate files for this architecture:
        {json.dumps(implementation_plan, indent=2)}
        
        Include:
        1. Main entry point
        2. Core modules for each feature
        3. Data models if needed
        4. Utility functions
        5. Configuration handling
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        try:
            files = json.loads(response.content)
            return files
        except json.JSONDecodeError:
            # Fallback: generate basic files
            return self._generate_fallback_files(requirements)

    def _generate_fallback_files(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate basic fallback files if LLM fails."""

        project_name = requirements.get('project_name', 'app')
        description = requirements.get('description', 'Generated project')

        main_py = f'''"""
{project_name} - Main Application
{description}
"""

def main():
    """Main entry point."""
    print("Welcome to {project_name}!")
    print("{description}")
    
    # TODO: Implement main application logic
    pass

if __name__ == "__main__":
    main()
'''

        return {
            "main.py": main_py,
            "config.py": '"""Configuration module."""\n\nCONFIG = {}\n',
            "utils.py": '"""Utility functions."""\n\ndef helper():\n    pass\n'
        }

    def _generate_requirements(self, implementation_plan: Dict[str, Any]) -> str:
        """Generate requirements.txt based on tech stack."""

        tech_stack = implementation_plan.get('tech_stack_final', [])

        # Map common frameworks to pip packages
        package_map = {
            'fastapi': 'fastapi>=0.109.0\nuvicorn[standard]>=0.27.0',
            'flask': 'flask>=3.0.0',
            'django': 'django>=5.0.0',
            'requests': 'requests>=2.31.0',
            'pandas': 'pandas>=2.0.0',
            'numpy': 'numpy>=1.24.0',
            'pytest': 'pytest>=7.4.0',
        }

        packages = []
        for tech in tech_stack:
            tech_lower = tech.lower()
            for key, value in package_map.items():
                if key in tech_lower:
                    packages.append(value)

        if not packages:
            packages = ['# Add your dependencies here']

        return '\n'.join(packages) + '\n'

    def _generate_config_files(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate configuration files."""

        env_example = '''# Environment variables
# Copy this to .env and fill in your values

API_KEY=your_api_key_here
DEBUG=true
'''

        return {
            '.env.example': env_example
        }

    def _generate_gitignore(self) -> str:
        """Generate .gitignore file."""

        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
generated_projects/
*.log
'''
