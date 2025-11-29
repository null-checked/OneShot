"""
This module provides a parser that uses an LLM to convert a natural language
problem description into a structured format.
"""

import json
from typing import TypedDict, List, Any, Dict

from llm_client import BaseLLMClient

# --- Data Structures for a Parsed Problem ---

class TestCase(TypedDict):
    """Represents a single test case with inputs and expected output."""
    input: List[Any]
    expected: Any

class StructuredProblem(TypedDict):
    """A structured representation of a programming problem."""
    title: str
    description: str
    function_signature: str
    function_name: str
    constraints: List[str]
    test_cases: List[TestCase]


# --- Problem Parser Class ---

class ProblemParser:
    """
    Parses a natural language problem description into a structured format using an LLM.
    """
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def _create_prompt(self, problem_description: str) -> str:
        """Creates the prompt for the LLM to parse the problem."""
        return f"""
Analyze the following programming problem description and extract a structured representation of it.

**Problem Description:**
"{problem_description}"

Your response MUST be a JSON object with the following structure:
{{
  "title": "A short, descriptive title for the problem (e.g., 'Two Sum').",
  "description": "A clear and concise restatement of the problem.",
  "function_signature": "The Python function signature required to solve the problem, including type hints (e.g., 'def two_sum(nums: List[int], target: int) -> List[int]:').",
  "function_name": "The name of the function to be called for testing (e.g., 'two_sum').",
  "constraints": [
    "A list of key constraints and edge cases mentioned in the problem (e.g., 'The list will contain at least two numbers.', 'Numbers can be positive, negative, or zero.')."
  ],
  "test_cases": [
    {{
      "input": "[...args]",
      "expected": "result"
    }}
  ]
}}

**Instructions for Test Cases:**
- Generate 5 to 8 diverse test cases.
- Include basic cases that test the primary logic.
- Include edge cases (e.g., empty lists, single-element lists, lists with duplicate values).
- Include tests with larger inputs to check for performance issues.
- The "input" field must be a list of arguments that can be passed directly to the function.

Do not include any extra text or explanation outside of the JSON object.
"""

    def _extract_json(self, response_text: str) -> Dict:
        """
        Robustly extracts a JSON object from a string that might contain extra text.
        """
        try:
            start_index = response_text.find('{')
            end_index = response_text.rfind('}')
            if start_index != -1 and end_index != -1 and start_index < end_index:
                json_str = response_text[start_index:end_index + 1]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON object found in the response.")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to decode JSON from LLM response: {e}\\nResponse: {response_text}") from e
    
    def _get_function_name(self, signature: str) -> str:
        """Extracts the function name from its signature."""
        try:
            return signature.split("def ")[1].split("(")[0].strip()
        except IndexError:
            raise ValueError(f"Could not parse function name from signature: {signature}")

    def parse(self, problem_description: str) -> StructuredProblem:
        """
        Parses the problem description and returns a structured representation.
        """
        prompt = self._create_prompt(problem_description)
        # Use a lower temperature for more predictable, structured output
        raw_response = self.llm_client.generate(prompt, temperature=0.3, system="You are a meticulous software engineer who is an expert at parsing requirements.")
        
        try:
            parsed_json = self._extract_json(raw_response)
            
            # --- Validation ---
            required_keys = {"title", "description", "function_signature", "constraints", "test_cases"}
            if not required_keys.issubset(parsed_json.keys()):
                # Try to get function name from signature if it's missing
                if 'function_name' not in parsed_json and 'function_signature' in parsed_json:
                    parsed_json['function_name'] = self._get_function_name(parsed_json['function_signature'])
                else:
                    raise ValueError(f"LLM response is missing required keys for problem parsing. Missing: {required_keys - set(parsed_json.keys())}")
            
            if not parsed_json.get("function_name"):
                 parsed_json['function_name'] = self._get_function_name(parsed_json['function_signature'])

            if not isinstance(parsed_json["test_cases"], list) or not parsed_json["test_cases"]:
                 raise ValueError("`test_cases` must be a non-empty list.")
            
            for i, case in enumerate(parsed_json["test_cases"]):
                if "input" not in case or "expected" not in case:
                    raise ValueError(f"Test case at index {i} is missing 'input' or 'expected' key.")

            # Type cast to the structured problem format for clarity
            return StructuredProblem(**parsed_json)

        except (ValueError, TypeError) as e:
            # In case of error, we can't proceed, so we raise a higher-level error.
            raise RuntimeError(f"Failed to parse the problem description into a structured format. Error: {e}")
