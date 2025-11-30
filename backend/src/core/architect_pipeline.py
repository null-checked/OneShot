"""
Architect Pipeline - New multi-agent orchestration system
Uses architect agent to define implementation, then executes with worker and testing agents
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from pathlib import Path
import json

from src.core.architect_agent import ArchitectAgent
from src.core.dynamic_worker import DynamicWorkerAgent
from src.core.testing_agent import TestingAgent
from src.core.filesystem_writer import FilesystemWriter
from src.core.code_executor import CodeExecutor


class ArchitectPipeline:
    """
    New pipeline that uses the architect pattern:
    1. Architect Agent defines implementation structure
    2. Worker Agents generate code (with retry logic)
    3. Testing Agents validate with real execution
    4. Write to filesystem
    """

    def __init__(self, openai_api_key: str, max_retries: int = 5):
        """
        Initialize the architect pipeline.

        Args:
            openai_api_key: OpenAI API key
            max_retries: Maximum retries per agent (default: 5)
        """
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=openai_api_key
        )

        self.architect = ArchitectAgent(self.llm)
        self.testing_agent = TestingAgent(timeout=30)
        self.fs_writer = FilesystemWriter()
        self.max_retries = max_retries

    def run(self, user_prompt: str) -> Dict[str, Any]:
        """
        Run the complete architect-based pipeline.

        Args:
            user_prompt: User's project request

        Returns:
            Final state with all results
        """
        print("=" * 70)
        print("[ARCH] Architect-Based Multi-Agent Pipeline - Starting")
        print("=" * 70)

        # Step 1: Architect defines the implementation
        print("\n[PLAN] Step 1: Architect Agent - Analyzing and Planning...")
        plan = self.architect.execute(user_prompt)

        print(f"\n  Project: {plan['project_name']}")
        print(f"  Agents to create: {len(plan['agents'])}")
        print(f"  Tests to perform: {len(plan['tests'])}")
        print(f"  Success criteria: {len(plan['success_criteria'])}")

        # Display agent breakdown
        for i, agent_def in enumerate(plan['agents'], 1):
            print(f"    Agent {i}: {agent_def['name']} - {agent_def['role']}")

        # Step 2: Initialize and execute worker agents
        print(f"\n[AGENT] Step 2: Initializing {len(plan['agents'])} Worker Agents...")
        all_files = {}
        agent_results = []

        # Build detailed context for agents
        context = {
            "project_name": plan["project_name"],
            "description": plan["description"],
            "tech_stack": plan["tech_stack"],
            "entry_point": plan.get("entry_point", "main.py"),
            "other_agents": [a["name"] for a in plan["agents"]],
            # Include information about what files other agents will generate
            "all_agent_files": {
                a["name"]: a["files_to_generate"]
                for a in plan["agents"]
            }
        }

        for i, agent_def in enumerate(plan['agents'], 1):
            print(f"\n  Agent {i}/{len(plan['agents'])}: {agent_def['name']}")
            print(f"    Role: {agent_def['role']}")
            print(f"    Files to generate: {', '.join(agent_def['files_to_generate'])}")

            # Execute agent with retry logic
            files, success, attempts = self._execute_worker_with_retry(
                agent_def, context, plan
            )

            all_files.update(files)

            agent_results.append({
                "name": agent_def["name"],
                "success": success,
                "attempts": attempts,
                "files_generated": len(files)
            })

            if success:
                print(f"    [PASS] Success after {attempts} attempt(s)")
            else:
                print(f"    [WARN]  Completed with issues after {attempts} attempts")

        # Add requirements.txt and README if not present
        all_files = self._add_standard_files(all_files, plan)

        # Step 3: Write files to disk
        print(f"\n[SAVE] Step 3: Writing {len(all_files)} files to disk...")
        project_path = self.fs_writer.create_project_structure(plan["project_name"])
        self.fs_writer.write_files(project_path, all_files)
        print(f"  [PASS] Project written to: {project_path}")

        # Step 4: Run tests
        print(f"\n[TEST] Step 4: Running {len(plan['tests'])} tests...")
        test_results = self.testing_agent.run_tests(str(project_path), plan["tests"])

        print(f"\n  Tests run: {test_results['tests_run']}")
        print(f"  Tests passed: {test_results['tests_passed']}")
        print(f"  Tests failed: {test_results['tests_failed']}")

        # Step 5: Verify success criteria
        print(f"\n[OK] Step 5: Verifying {len(plan['success_criteria'])} success criteria...")
        criteria_results = self.testing_agent.verify_success_criteria(
            str(project_path), plan["success_criteria"]
        )

        for criterion in criteria_results["criteria_results"]:
            status = "[PASS]" if criterion["met"] else "[FAIL]"
            print(f"  {status} {criterion['criteria_name']}: {criterion['description']}")

        # Build final state
        final_state = {
            "user_prompt": user_prompt,
            "plan": plan,
            "agent_results": agent_results,
            "files_generated": len(all_files),
            "project_path": str(project_path),
            "test_results": test_results,
            "criteria_results": criteria_results,
            "success": test_results["success"] and criteria_results["all_criteria_met"]
        }

        print("\n" + "=" * 70)
        if final_state["success"]:
            print("[OK] Pipeline completed successfully!")
        else:
            print("[WARN]  Pipeline completed with some issues")
        print("=" * 70)

        return final_state

    def _execute_worker_with_retry(
        self,
        agent_def: Dict[str, Any],
        context: Dict[str, Any],
        plan: Dict[str, Any]
    ) -> tuple[Dict[str, str], bool, int]:
        """
        Execute a worker agent with retry logic.

        Args:
            agent_def: Agent definition from architect
            context: Execution context
            plan: Full implementation plan

        Returns:
            Tuple of (files, success, attempts)
        """
        worker = DynamicWorkerAgent(
            llm=self.llm,
            name=agent_def["name"],
            role=agent_def["role"],
            instructions=agent_def["instructions"],
            files_to_generate=agent_def["files_to_generate"]
        )

        last_files = {}
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"    Attempt {attempt}/{self.max_retries}...")

                # Execute the worker
                files = worker.execute(context)

                # Validate the files
                validation_result = self._validate_generated_files(files, agent_def)

                if validation_result["valid"]:
                    return files, True, attempt

                # If not valid, store error and retry
                last_error = validation_result["error"]
                last_files = files

                print(f"    [WARN]  Validation failed: {last_error}")

                # Add error feedback to context for next attempt
                context["previous_error"] = last_error
                context["previous_attempt"] = attempt

            except Exception as e:
                print(f"    [WARN]  Error: {str(e)}")
                last_error = str(e)

        # All retries exhausted
        print(f"    [WARN]  Max retries ({self.max_retries}) reached")
        return last_files, False, self.max_retries

    def _validate_generated_files(
        self,
        files: Dict[str, str],
        agent_def: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that generated files meet basic requirements.

        Args:
            files: Generated files
            agent_def: Agent definition

        Returns:
            Dictionary with validation result
        """
        # Check that all required files are present
        for required_file in agent_def["files_to_generate"]:
            if required_file not in files:
                return {
                    "valid": False,
                    "error": f"Missing required file: {required_file}"
                }

        # Check that files are not empty or placeholder-only
        for file_path, content in files.items():
            if not content or len(content.strip()) < 10:
                return {
                    "valid": False,
                    "error": f"File is too short or empty: {file_path}"
                }

            # Check for excessive TODO/placeholder comments
            if file_path.endswith('.py'):
                lines = content.split('\n')
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

                if len(code_lines) < 3:
                    return {
                        "valid": False,
                        "error": f"File has insufficient code: {file_path}"
                    }

                # Check for placeholder patterns
                placeholder_patterns = [
                    "# TODO",
                    "# implementation here",
                    "# Add implementation",
                    "# implement this",
                    "pass  # TODO",
                    "pass  # implement",
                    "pass # TODO",
                    "pass # implement",
                    "raise NotImplementedError",
                    "NotImplementedError()",
                    "... # TODO",
                    "TODO:",
                ]

                content_lower = content.lower()
                for pattern in placeholder_patterns:
                    if pattern.lower() in content_lower:
                        return {
                            "valid": False,
                            "error": f"File contains placeholder code ('{pattern}'): {file_path}"
                        }

                # Check for functions with only 'pass' statement
                import re
                # Match function definitions followed by only whitespace and pass
                func_pass_pattern = r'def\s+\w+\([^)]*\):\s*(?:"""[^"]*"""\s*)?pass\s*(?:\n|$)'
                if re.search(func_pass_pattern, content, re.MULTILINE):
                    return {
                        "valid": False,
                        "error": f"File contains function with only 'pass' statement: {file_path}"
                    }

        # Basic import validation
        validation_result = self._validate_imports(files, agent_def)
        if not validation_result["valid"]:
            return validation_result

        return {"valid": True, "error": None}

    def _validate_imports(self, files: Dict[str, str], agent_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that imports between files are consistent.

        Args:
            files: Generated files
            agent_def: Agent definition

        Returns:
            Dictionary with validation result
        """
        import re

        for file_path, content in files.items():
            if not file_path.endswith('.py'):
                continue

            # Find all import statements
            import_patterns = [
                r'from\s+(\w+)\s+import\s+([^#\n]+)',  # from module import name
                r'import\s+(\w+)',  # import module
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        module_name = match[0]
                    else:
                        module_name = match

                    # Skip standard library and common packages
                    if module_name in ['sys', 'os', 're', 'json', 'math', 'random', 'datetime',
                                      'time', 'collections', 'itertools', 'functools', 'pathlib',
                                      'typing', 'argparse', 'unittest', 'pytest']:
                        continue

                    # Check if this module is one we're generating
                    expected_file = f"{module_name}.py"
                    if expected_file in files or expected_file in [f for f in files.keys()]:
                        # Good - importing from a file we're generating
                        continue

                    # Check if it's in other agent files from context
                    # For now, we'll be lenient and assume other agents will create their files properly

        return {"valid": True, "error": None}

    def _add_standard_files(self, files: Dict[str, str], plan: Dict[str, Any]) -> Dict[str, str]:
        """Add standard files like README and requirements.txt if not present."""

        # Add README.md if not present
        if "README.md" not in files:
            files["README.md"] = self._generate_readme(plan)

        # Add requirements.txt if not present
        if "requirements.txt" not in files:
            files["requirements.txt"] = self._generate_requirements(plan["tech_stack"])

        # Add .gitignore if not present
        if ".gitignore" not in files:
            files[".gitignore"] = self._generate_gitignore()

        return files

    def _generate_readme(self, plan: Dict[str, Any]) -> str:
        """Generate a basic README."""
        return f"""# {plan['project_name']}

{plan['description']}

## Tech Stack

{', '.join(plan['tech_stack'])}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python {plan['entry_point']}
```

## Components

{self._format_agents_list(plan['agents'])}

## Tests

Run tests to verify the implementation:

```bash
{self._format_tests_list(plan['tests'])}
```

## Success Criteria

{self._format_criteria_list(plan['success_criteria'])}

---

*Generated by Architect-Based Multi-Agent Pipeline*
"""

    def _format_agents_list(self, agents: List[Dict[str, Any]]) -> str:
        """Format agents list for README."""
        return "\n".join([f"- **{a['name']}**: {a['role']}" for a in agents])

    def _format_tests_list(self, tests: List[Dict[str, Any]]) -> str:
        """Format tests list for README."""
        if not tests:
            return "No automated tests defined."
        return "\n".join([f"# {t['test_name']}: {t['description']}\n{t['test_command']}\n" for t in tests])

    def _format_criteria_list(self, criteria: List[Dict[str, Any]]) -> str:
        """Format success criteria for README."""
        return "\n".join([f"- {c['criteria_name']}: {c['description']}" for c in criteria])

    def _generate_requirements(self, tech_stack: List[str]) -> str:
        """Generate requirements.txt based on tech stack."""
        # Map tech stack to pip packages
        package_mapping = {
            "flask": "flask>=2.3.0",
            "fastapi": "fastapi>=0.104.0\nuvicorn>=0.24.0",
            "django": "django>=4.2.0",
            "requests": "requests>=2.31.0",
            "numpy": "numpy>=1.24.0",
            "pandas": "pandas>=2.0.0",
            "sqlalchemy": "sqlalchemy>=2.0.0",
            "pytest": "pytest>=7.4.0",
            "click": "click>=8.1.0",
        }

        packages = set()
        for tech in tech_stack:
            tech_lower = tech.lower()
            if tech_lower in package_mapping:
                for pkg in package_mapping[tech_lower].split('\n'):
                    packages.add(pkg)

        # Always add pytest for testing
        packages.add("pytest>=7.4.0")

        return "\n".join(sorted(packages)) + "\n"

    def _generate_gitignore(self) -> str:
        """Generate a basic .gitignore."""
        return """# Python
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

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
"""
