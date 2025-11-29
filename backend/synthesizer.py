"""
This module defines the Synthesizer, which creates a hybrid solution from multiple
agent outputs.
"""
import json
from typing import List, Dict, TypedDict

from llm_client import BaseLLMClient
from agents import AgentSolution
from judge import JudgeScore
from problem_parser import StructuredProblem

# --- Data Structure for Synthesized Solution ---

class SynthesizedSolution(TypedDict):
    """Represents the final, synthesized solution."""
    synthesis_reasoning: str
    improvements: List[str]
    approach: str
    time_complexity: str
    space_complexity: str
    code: str

# --- Synthesizer Class ---

class Synthesizer:
    """
    Uses an LLM to analyze multiple solutions and create a superior, hybrid solution.
    """
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def _create_prompt(
        self,
        problem: StructuredProblem,
        solutions: Dict[str, AgentSolution],
        scores: List[JudgeScore]
    ) -> str | None:
        """Creates the detailed prompt for the synthesizer LLM."""
        
        # Only consider solutions that were fully correct
        successful_agents = {s.agent_name for s in scores if s.correctness_score == 100}
        if not successful_agents:
            return None

        prompt = f"""
You are an expert software architect. Your task is to analyze multiple solutions to a programming problem, identify the best parts of each, and synthesize a new, superior solution.

**Problem Statement:**
- **Title:** {problem['title']}
- **Description:** {problem['description']}
- **Function Signature:** `{problem['function_signature']}`

Here are the successful solutions from different agents, ranked by their scores:
"""
        
        # Add details of successful solutions to the prompt
        sorted_successful_scores = sorted([s for s in scores if s.agent_name in successful_agents], key=lambda s: s.rank)

        for score in sorted_successful_scores:
            agent_name = score.agent_name
            solution = solutions[agent_name]
            prompt += f"""
---
**Agent: {agent_name} (Rank: {score.rank}, Score: {score.total_score:.2f})**
- **Approach:** {solution['approach_name']}
- **Complexity:** Time: {solution['time_complexity']}, Space: {solution['space_complexity']}
- **Judge's Analysis:** {score.analysis}
- **Code:**
```python
{solution['code']}
```
---
"""

        prompt += """
**Your Task:**
Based on the analysis, create a new, hybrid solution that combines the best ideas from the provided solutions. The new solution should aim to be more efficient, readable, and robust than any single solution.

Your response MUST be a JSON object with the following structure:
{
  "synthesis_reasoning": "Explain your thought process. What are the strengths and weaknesses of each solution? What did you take from each agent to create the final version?",
  "improvements": [
    "A list of specific improvements you made over the original solutions (e.g., 'Used a single pass approach from GreedyGus but with the data structure from DataStructDave')."
  ],
  "approach": "A concise name for your final approach.",
  "time_complexity": "The Big O time complexity of your new solution.",
  "space_complexity": "The Big O space complexity of your new solution.",
  "code": "The complete, correct, and runnable Python code for the new, synthesized solution."
}

Do not include any extra text or explanation outside of this JSON object.
"""
        return prompt

    def _extract_json(self, response_text: str) -> Dict:
        """Robustly extracts a JSON object from a string."""
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

    def synthesize(
        self,
        problem: StructuredProblem,
        solutions: Dict[str, AgentSolution],
        scores: List[JudgeScore]
    ) -> SynthesizedSolution:
        """
        Generates the synthesized solution.
        """
        prompt = self._create_prompt(problem, solutions, scores)
        if not prompt:
            return {
                "synthesis_reasoning": "No fully correct solutions were provided, so a hybrid solution could not be created.",
                "improvements": [],
                "approach": "N/A",
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "code": "# No solution could be synthesized."
            }
            
        system_prompt = "You are a world-class principal engineer with a talent for synthesizing optimal solutions from multiple proposals."
        raw_response = self.llm_client.generate(prompt, system=system_prompt, temperature=0.4)
        
        try:
            parsed_json = self._extract_json(raw_response)
            
            required_keys = {"synthesis_reasoning", "improvements", "approach", "time_complexity", "space_complexity", "code"}
            if not required_keys.issubset(parsed_json.keys()):
                raise ValueError(f"Synthesizer LLM response is missing required keys. Missing: {required_keys - set(parsed_json.keys())}")
            
            return SynthesizedSolution(**parsed_json)
            
        except ValueError as e:
            return {
                "synthesis_reasoning": f"Failed to synthesize a new solution due to an error: {e}",
                "improvements": [],
                "approach": "Error",
                "time_complexity": "N/A",
                "space_complexity": "N/A",
                "code": f"# Synthesis failed.\\n# Raw response from LLM:\\n# {raw_response}"
            }
