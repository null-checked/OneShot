"""
Architect Agent - Defines the implementation structure
Analyzes user prompt and determines what agents are needed, tests to perform, and success criteria
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json


class ArchitectAgent:
    """
    The Architect Agent analyzes the user prompt and creates a complete implementation plan.

    It defines:
    - What worker agents are needed (name, role, instructions, files to generate)
    - What tests should be performed
    - Success criteria for the project
    """

    SYSTEM_PROMPT = """You are an expert software architect. Your job is to analyze a user's project request
and create a detailed implementation plan that defines:

1. **Worker Agents Needed**: Break down the project into logical components/modules. For each component,
   define a worker agent with:
   - name: Agent identifier (e.g., "backend_api", "frontend_ui", "database_models")
   - role: What this agent is responsible for
   - instructions: Detailed instructions on what to implement
   - files_to_generate: List of file paths this agent should create

2. **Tests to Perform**: Define specific tests that should be executed to verify the implementation:
   - test_name: Identifier for the test
   - test_type: "unit", "integration", "functional", or "syntax"
   - description: What the test verifies
   - test_command: Command to run the test (e.g., "python -m pytest tests/", "python main.py --test")

3. **Success Criteria**: Define what makes this project successful:
   - criteria_name: Name of the criterion
   - description: What should be achieved
   - verification_method: How to verify this criterion is met

4. **Project Metadata**:
   - project_name: Clean project name (lowercase, underscores)
   - description: Brief project description
   - tech_stack: List of technologies/libraries needed
   - entry_point: Main file to run (e.g., "main.py", "app.py")

**Important Guidelines**:
- Create 2-6 worker agents depending on project complexity
- Each agent should have clear, non-overlapping responsibilities
- Include at least one test (syntax check at minimum)
- Be specific in instructions - agents will follow them literally
- Consider the tech stack and structure carefully

Output **ONLY** valid JSON in this exact format:
{
    "project_name": "my_project",
    "description": "Brief description of the project",
    "tech_stack": ["python", "flask", "sqlite"],
    "entry_point": "main.py",
    "agents": [
        {
            "name": "agent_name",
            "role": "What this agent does",
            "instructions": "Detailed step-by-step instructions for implementation",
            "files_to_generate": ["path/to/file1.py", "path/to/file2.py"]
        }
    ],
    "tests": [
        {
            "test_name": "syntax_check",
            "test_type": "syntax",
            "description": "Verify Python syntax is valid",
            "test_command": "python -m py_compile {file}"
        }
    ],
    "success_criteria": [
        {
            "criteria_name": "runs_without_errors",
            "description": "Application starts and runs without crashing",
            "verification_method": "Execute entry point and check exit code"
        }
    ]
}
"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analyze the user prompt and create an implementation plan.

        Args:
            user_prompt: The user's project request

        Returns:
            Dictionary with project plan including agents, tests, and success criteria
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"User Request:\n{user_prompt}\n\nCreate a detailed implementation plan.")
        ]

        try:
            response = self.llm.invoke(messages)

            # Try to parse JSON from response
            plan = self._parse_json_response(response.content)

            # Validate the plan structure
            plan = self._validate_and_fix_plan(plan, user_prompt)

            return plan

        except Exception as e:
            print(f"Error in ArchitectAgent: {e}")
            # Return a minimal fallback plan
            return self._create_fallback_plan(user_prompt)

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response."""
        # Sometimes LLM wraps JSON in markdown code blocks
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        return json.loads(content)

    def _validate_and_fix_plan(self, plan: Dict[str, Any], user_prompt: str) -> Dict[str, Any]:
        """Validate the plan structure and fix any issues."""
        # Ensure required fields exist
        if "project_name" not in plan:
            plan["project_name"] = "generated_project"

        if "description" not in plan:
            plan["description"] = user_prompt[:200]

        if "tech_stack" not in plan or not isinstance(plan["tech_stack"], list):
            plan["tech_stack"] = ["python"]

        if "entry_point" not in plan:
            plan["entry_point"] = "main.py"

        if "agents" not in plan or not isinstance(plan["agents"], list) or len(plan["agents"]) == 0:
            # Create a default agent
            plan["agents"] = [{
                "name": "main_implementation",
                "role": "Implement the core functionality",
                "instructions": f"Implement the following: {user_prompt}",
                "files_to_generate": ["main.py"]
            }]

        # Validate each agent
        for agent in plan["agents"]:
            if "name" not in agent:
                agent["name"] = "worker_agent"
            if "role" not in agent:
                agent["role"] = "Implementation"
            if "instructions" not in agent:
                agent["instructions"] = "Implement the functionality"
            if "files_to_generate" not in agent or not isinstance(agent["files_to_generate"], list):
                agent["files_to_generate"] = ["code.py"]

        if "tests" not in plan or not isinstance(plan["tests"], list) or len(plan["tests"]) == 0:
            # Add a default syntax check test
            plan["tests"] = [{
                "test_name": "syntax_check",
                "test_type": "syntax",
                "description": "Verify Python syntax is valid",
                "test_command": "python -m py_compile {file}"
            }]

        if "success_criteria" not in plan or not isinstance(plan["success_criteria"], list):
            plan["success_criteria"] = [{
                "criteria_name": "implementation_complete",
                "description": "All required files are generated",
                "verification_method": "Check that all files exist"
            }]

        return plan

    def _create_fallback_plan(self, user_prompt: str) -> Dict[str, Any]:
        """Create a minimal fallback plan when parsing fails."""
        return {
            "project_name": "generated_project",
            "description": user_prompt[:200],
            "tech_stack": ["python"],
            "entry_point": "main.py",
            "agents": [{
                "name": "main_implementation",
                "role": "Implement the core functionality",
                "instructions": f"Implement a Python application based on this request: {user_prompt}",
                "files_to_generate": ["main.py", "README.md"]
            }],
            "tests": [{
                "test_name": "syntax_check",
                "test_type": "syntax",
                "description": "Verify Python syntax is valid",
                "test_command": "python -m py_compile main.py"
            }],
            "success_criteria": [{
                "criteria_name": "files_generated",
                "description": "All required files are created",
                "verification_method": "Check file existence"
            }]
        }
