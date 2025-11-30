"""
Dynamic Worker Agent - Generates code based on custom instructions
Can be initialized with any role and instructions defined by the Architect
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json


class DynamicWorkerAgent:
    """
    A worker agent that can be dynamically configured with custom instructions.

    Each worker agent is responsible for generating specific files according to
    the architect's plan.
    """

    def __init__(self, llm: ChatOpenAI, name: str, role: str, instructions: str, files_to_generate: List[str]):
        """
        Initialize a dynamic worker agent.

        Args:
            llm: Language model instance
            name: Agent identifier
            role: What this agent is responsible for
            instructions: Detailed instructions on what to implement
            files_to_generate: List of file paths this agent should create
        """
        self.llm = llm
        self.name = name
        self.role = role
        self.instructions = instructions
        self.files_to_generate = files_to_generate

    def execute(self, context: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Execute the agent's task and generate code files.

        Args:
            context: Optional context including project metadata, tech stack, etc.

        Returns:
            Dictionary mapping file paths to their content
        """
        if context is None:
            context = {}

        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(context)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            response = self.llm.invoke(messages)

            # Parse the response as JSON
            files = self._parse_files_response(response.content)

            # Validate that all required files are present
            files = self._ensure_all_files(files)

            return files

        except Exception as e:
            print(f"Error in worker agent '{self.name}': {e}")
            # Return fallback files
            return self._create_fallback_files()

    def _create_system_prompt(self) -> str:
        """Create the system prompt for this worker agent."""
        return f"""You are a specialized software development agent.

**Your Role**: {self.role}

**Your Responsibility**: Generate complete, working, production-quality code files.

**Instructions**:
{self.instructions}

**Files You Must Generate**: {', '.join(self.files_to_generate)}

**Output Format**:
Return ONLY valid JSON mapping file paths to their complete content:
{{
    "path/to/file.py": "complete file content here...",
    "path/to/another.py": "complete file content here..."
}}

**CRITICAL REQUIREMENTS - READ THIS CAREFULLY**:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!! ABSOLUTELY NO PLACEHOLDERS OR TODOS ALLOWED WHATSOEVER    !!
!! YOUR CODE WILL BE REJECTED IF IT CONTAINS ANY OF THESE    !!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

- Generate COMPLETE, FUNCTIONAL code with FULL implementation
- Write ACTUAL working logic, not just function signatures or stubs
- Every function MUST have real code inside, not just "pass" or comments
- NEVER EVER use: "TODO", "pass", "NotImplementedError", "# implementation here"
- If you don't know exactly what to implement, make a reasonable working implementation
- Include all necessary imports at the top
- Add proper error handling where needed
- Follow Python best practices (PEP 8)
- Include docstrings for functions and classes
- The code must be IMMEDIATELY executable without modifications

**IMPORT HANDLING RULES** (CRITICAL - FAILURES OFTEN DUE TO IMPORT ERRORS):
- ONLY import from modules that are explicitly shown in the context below
- ONLY import classes/functions that are EXPLICITLY listed as existing in other modules
- If you see "Class: SomeClass" in the context, import with: from module_name import SomeClass
- If you see "Standalone Functions: func1, func2" in the context, import with: from module_name import func1, func2
- DO NOT guess or assume what exists - if it's not shown in the context, DON'T import it
- DO NOT create your own imports unless explicitly instructed
- When your instructions say "IMPORT: from X import Y", use EXACTLY that import statement
- Match class names and function names EXACTLY (case-sensitive)
- If importing from a class, you must instantiate it: obj = SomeClass(args)
- If importing standalone functions, call them directly: result = some_function(args)

**ABSOLUTELY FORBIDDEN PATTERNS** (will cause IMMEDIATE REJECTION):
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DO NOT USE ANY OF THESE - YOUR CODE WILL BE REJECTED:
- "# TODO"
- "# implementation here"
- "# Add implementation"
- "# implement this"
- "pass  # TODO"
- "pass  # implement"
- "pass # TODO"
- "raise NotImplementedError"
- Functions with only "pass" in the body
- Empty function bodies
- Any variation of TODO or placeholder comments
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

**WRONG - This will be REJECTED**:
```python
def calculate_derivative(coefficients):
    # TODO: Implement polynomial derivative calculation
    pass

def process_data(data):
    # implementation here
    return None
```

**CORRECT - This will be ACCEPTED**:
```python
def calculate_derivative(coefficients):
    '''Calculate derivative of polynomial with given coefficients.'''
    if not coefficients or len(coefficients) == 0:
        return []
    # Derivative of ax^n is n*ax^(n-1)
    result = []
    for i in range(1, len(coefficients)):
        result.append(i * coefficients[i])
    return result

def process_data(data):
    '''Process input data and return cleaned results.'''
    if not data:
        return []
    return [item.strip().lower() for item in data if item]
```

Notice: Every function has REAL, WORKING code that actually does something!
"""

    def _create_user_prompt(self, context: Dict[str, Any]) -> str:
        """Create the user prompt with context."""
        prompt_parts = [f"Generate the files for the '{self.name}' component."]

        if "project_name" in context:
            prompt_parts.append(f"\nProject Name: {context['project_name']}")

        if "description" in context:
            prompt_parts.append(f"\nProject Description: {context['description']}")

        if "tech_stack" in context:
            prompt_parts.append(f"\nTech Stack: {', '.join(context['tech_stack'])}")

        if "other_agents" in context:
            prompt_parts.append(f"\nOther Components: {', '.join(context['other_agents'])}")
            prompt_parts.append("\nEnsure your code integrates well with these other components.")

            # Show what files other agents are generating
            if "all_agent_files" in context:
                prompt_parts.append("\n**Integration Information:**")
                prompt_parts.append("Other agents' files:")
                for agent_name, files in context["all_agent_files"].items():
                    if agent_name != self.name:  # Don't show own files
                        prompt_parts.append(f"  - {agent_name}: {', '.join(files)}")

                prompt_parts.append("\n**IMPORTANT for imports**:")
                prompt_parts.append("- Use the EXACT file names listed above (without .py)")
                prompt_parts.append("- Only import what you actually need")
                prompt_parts.append("- Assume other files will define their functions/classes properly")
                prompt_parts.append("- If you're creating the main/entry point, import from the correct module names")
                prompt_parts.append("- Example: if 'calculator.py' exists, use 'from calculator import Calculator'")

                # If this is likely an entry point or main file
                if any(main_name in f.lower() for f in self.files_to_generate for main_name in ['main', 'cli', 'app', 'run']):
                    prompt_parts.append("\n**You are creating an entry point/main file**:")
                    prompt_parts.append("- Import the necessary classes/functions from other modules")
                    prompt_parts.append("- Make sure to use standard, predictable class names (e.g., Calculator, Parser, etc.)")
                    prompt_parts.append("- When instantiating classes, check their __init__ signatures above and provide required arguments")
                    prompt_parts.append("- Example: If SomeClass.__init__(self, arg1: str), create it as: SomeClass('value')")
                    prompt_parts.append("- Example: If AnotherClass.__init__(self, obj: SomeClass), create it as: AnotherClass(some_instance)")
                    prompt_parts.append("- The code must work when run with: python <your_file>")

                # If this is a library/module file
                else:
                    prompt_parts.append("\n**You are creating a library/module file**:")
                    prompt_parts.append("- Define clear, well-named classes and functions")
                    prompt_parts.append("- Use standard naming: Calculator, Parser, Handler, Manager, etc.")
                    prompt_parts.append("- Other files may import from you, so use predictable names")

        # Show actual code generated by previous agents (if any)
        # This allows agents to see what classes/functions exist for importing
        if "generated_code_files" in context and context["generated_code_files"]:
            is_test_writer = 'test' in self.name.lower() or 'test' in self.role.lower()

            # Header differs for test writers vs regular agents
            if is_test_writer:
                prompt_parts.append("\n**CODE TO TEST** (already generated by other agents):")
            else:
                prompt_parts.append("\n**EXISTING CODE** (from previous agents - available for import):")

            # Parse and display structure of all generated files
            for file_path, content in context["generated_code_files"].items():
                if file_path.endswith('.py') and not file_path.startswith('test'):
                    # Parse code structure more intelligently
                    structure = self._parse_code_structure(content)

                    if structure["classes"] or structure["standalone_functions"]:
                        module_name = file_path.replace('.py', '')
                        prompt_parts.append(f"\n{file_path} (import as: {module_name}):")

                        # Show classes with their method signatures
                        for class_info in structure["classes"]:
                            prompt_parts.append(f"  Class: {class_info['name']}")
                            if class_info["methods"]:
                                prompt_parts.append(f"    Methods:")
                                for method in class_info["methods"]:
                                    if isinstance(method, dict):
                                        prompt_parts.append(f"      - {method['signature']}")
                                    else:
                                        # Fallback for old format
                                        prompt_parts.append(f"      - {method}(self, ...)")
                            prompt_parts.append(f"    Import: from {module_name} import {class_info['name']}")
                            if class_info["methods"]:
                                prompt_parts.append(f"    Usage: obj = {class_info['name']}(...); obj.method_name(...)")

                        # Show standalone functions with signatures
                        if structure["standalone_functions"]:
                            prompt_parts.append(f"  Standalone Functions:")
                            for func in structure["standalone_functions"]:
                                if isinstance(func, dict):
                                    prompt_parts.append(f"    - {func['signature']}")
                                else:
                                    # Fallback for old format
                                    prompt_parts.append(f"    - {func}(...)")

                            # Create import statement
                            func_names = [f['name'] if isinstance(f, dict) else f for f in structure['standalone_functions']]
                            prompt_parts.append(f"    Import: from {module_name} import {', '.join(func_names)}")

            # Different rules for test writers vs regular agents
            if is_test_writer:
                prompt_parts.append("\n**TEST GENERATION RULES (CRITICAL - READ CAREFULLY)**:")
                prompt_parts.append("- ONLY test functions/classes that actually exist (listed above)")
                prompt_parts.append("- Use the EXACT import statements shown above - DO NOT modify them")
                prompt_parts.append("- Match the EXACT API shown above:")
                prompt_parts.append("  * If method signature is load_data(self), call it as: obj.load_data()")
                prompt_parts.append("  * If method signature is save_data(self, data: dict), call it as: obj.save_data(data)")
                prompt_parts.append("  * If it's a standalone function func(arg1, arg2), call it as: func(arg1, arg2)")
                prompt_parts.append("- For class methods, import the class and create an instance in setUp()")
                prompt_parts.append("- For standalone functions, import them directly and call them")
                prompt_parts.append("- Test the ACTUAL implementation, not what you think it should be")
                prompt_parts.append("- Create comprehensive test cases covering normal and edge cases")
            else:
                prompt_parts.append("\n**IMPORT RULES (CRITICAL - MOST ERRORS COME FROM WRONG IMPORTS)**:")
                prompt_parts.append("- Use ONLY the EXACT import statements shown above")
                prompt_parts.append("- DO NOT import anything that isn't explicitly listed above")
                prompt_parts.append("- DO NOT assume what exists - only use what's shown")
                prompt_parts.append("- For classes:")
                prompt_parts.append("  * Import: from module import ClassName")
                prompt_parts.append("  * Usage: obj = ClassName(args); obj.method()")
                prompt_parts.append("- For standalone functions:")
                prompt_parts.append("  * Import: from module import function_name")
                prompt_parts.append("  * Usage: result = function_name(args)")
                prompt_parts.append("- If your instructions specify an import, use EXACTLY that import")
                prompt_parts.append("- If no existing code is shown above, implement everything from scratch")

        # IMPORTANT: Include error feedback from previous attempts
        if "previous_error" in context:
            attempt_num = context.get("previous_attempt", 1)
            prompt_parts.append("\n" + "=" * 80)
            prompt_parts.append(f"!!! PREVIOUS ATTEMPT {attempt_num} WAS REJECTED !!!")
            prompt_parts.append("=" * 80)
            prompt_parts.append(f"\nREJECTION REASON:\n{context['previous_error']}")
            prompt_parts.append("\n" + "=" * 80)
            prompt_parts.append("!!! YOU MUST FIX THIS ERROR NOW !!!")
            prompt_parts.append("=" * 80)
            prompt_parts.append("\nREQUIREMENTS FOR THIS ATTEMPT:")
            prompt_parts.append("1. Read the error above CAREFULLY")
            prompt_parts.append("2. Identify the EXACT problematic code shown")
            prompt_parts.append("3. Replace ALL placeholders with REAL, WORKING implementations")
            prompt_parts.append("4. EVERY function must have actual logic, not just 'pass' or comments")
            prompt_parts.append("5. If you see 'TODO' or 'pass' ANYWHERE, replace it with working code")
            prompt_parts.append("6. Test your logic mentally - would this code actually run and work?")
            prompt_parts.append("\nDO NOT REPEAT THE SAME MISTAKE!")
            prompt_parts.append("Generate COMPLETE, WORKING code with REAL implementations.")

        prompt_parts.append(f"\nFiles to generate: {', '.join(self.files_to_generate)}")

        return "\n".join(prompt_parts)

    def _parse_code_structure(self, content: str) -> Dict[str, Any]:
        """
        Parse Python code to extract classes, methods with signatures, and standalone functions.

        Args:
            content: Python source code

        Returns:
            Dictionary with:
            - classes: List of {name, methods: [{name, signature}]}
            - standalone_functions: List of {name, signature}
        """
        import re

        structure = {
            "classes": [],
            "standalone_functions": []
        }

        lines = content.split('\n')
        current_class = None
        current_indent = 0

        for line in lines:
            stripped = line.lstrip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue

            # Calculate indentation
            indent = len(line) - len(stripped)

            # Check for class definition
            class_match = re.match(r'class\s+(\w+)', stripped)
            if class_match:
                current_class = {
                    "name": class_match.group(1),
                    "methods": []
                }
                structure["classes"].append(current_class)
                current_indent = indent
                continue

            # Check for function/method definition with full signature
            func_match = re.match(r'def\s+(\w+)\s*\(([^)]*)\)', stripped)
            if func_match:
                func_name = func_match.group(1)
                func_params = func_match.group(2).strip()

                # Skip private/magic methods EXCEPT __init__ (we need that for instantiation)
                if func_name.startswith('_') and func_name != '__init__':
                    continue

                # Create function info with signature
                func_info = {
                    "name": func_name,
                    "signature": f"{func_name}({func_params})"
                }

                # If we're inside a class, it's a method
                if current_class is not None and indent > current_indent:
                    current_class["methods"].append(func_info)
                else:
                    # Standalone function
                    structure["standalone_functions"].append(func_info)
                    current_class = None  # Reset class context

        return structure

    def _parse_files_response(self, content: str) -> Dict[str, str]:
        """Parse the LLM response to extract file contents."""
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        files = json.loads(content)

        # Ensure it's a dictionary
        if not isinstance(files, dict):
            raise ValueError("Response is not a dictionary")

        return files

    def _ensure_all_files(self, files: Dict[str, str]) -> Dict[str, str]:
        """Ensure all required files are present, create placeholders if missing."""
        for file_path in self.files_to_generate:
            if file_path not in files:
                # Create a minimal placeholder
                files[file_path] = self._create_placeholder_content(file_path)

        return files

    def _create_placeholder_content(self, file_path: str) -> str:
        """Create placeholder content for a missing file."""
        if file_path.endswith('.py'):
            return f'''"""
{file_path} - Generated by {self.name}
{self.role}
"""

# TODO: Implementation needed
pass
'''
        elif file_path.endswith('.md'):
            return f"# {file_path}\n\nGenerated by {self.name}\n"
        else:
            return f"# Generated by {self.name}\n"

    def _create_fallback_files(self) -> Dict[str, str]:
        """Create fallback files when execution fails."""
        files = {}
        for file_path in self.files_to_generate:
            files[file_path] = self._create_placeholder_content(file_path)
        return files

    def __repr__(self) -> str:
        return f"DynamicWorkerAgent(name='{self.name}', role='{self.role}', files={self.files_to_generate})"
