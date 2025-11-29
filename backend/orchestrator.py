"""
This module contains the ArenaOrchestrator, which coordinates the entire multi-agent
competition workflow.
"""

import concurrent.futures
from typing import Callable, Any, Dict, List

from config import Settings, settings
from llm_client import create_llm_client, BaseLLMClient
from problem_parser import ProblemParser, StructuredProblem
from agents import CodingAgent, ALL_AGENTS, AgentSolution
from executor import execute_in_sandbox, TestSuiteResult
from judge import Judge, JudgeScore
from synthesizer import Synthesizer, SynthesizedSolution

class ArenaOrchestrator:
    """
    Manages the full pipeline from problem parsing to final synthesis.
    """
    def __init__(self, config: Settings = settings, event_callback: Callable[[str, Any], None] | None = None):
        self.config = config
        self.event_callback = event_callback or (lambda name, data: None)
        
        self.llm_client: BaseLLMClient = create_llm_client(config)
        self.problem_parser: ProblemParser = ProblemParser(self.llm_client)
        self.agents: List[CodingAgent] = [CodingAgent(p, self.llm_client) for p in ALL_AGENTS]
        self.judge: Judge = Judge()
        self.synthesizer: Synthesizer = Synthesizer(self.llm_client)

    def _send_event(self, name: str, data: Any):
        """Helper to send an event to the registered callback."""
        self.event_callback(name, data)

    def run(self, problem_description: str) -> Dict:
        """
        Executes the entire arena workflow for a given problem description.
        """
        # 1. Parse Problem
        self._send_event("status", {"message": "Parsing problem..."})
        try:
            problem = self.problem_parser.parse(problem_description)
            self._send_event("problem_parsed", problem)
        except Exception as e:
            self._send_event("error", {"message": f"Failed to parse problem: {e}"})
            return {"error": str(e)}

        # 2. Generate Solutions (in parallel)
        self._send_event("status", {"message": "Agents are generating solutions..."})
        solutions: Dict[str, AgentSolution] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            future_to_agent = {}
            for agent in self.agents:
                self._send_event("agent_start", {"agent": agent.personality.name})
                future = executor.submit(agent.generate_solution, problem)
                future_to_agent[future] = agent

            for future in concurrent.futures.as_completed(future_to_agent):
                agent = future_to_agent[future]
                agent_name = agent.personality.name
                try:
                    solution = future.result()
                    solutions[agent_name] = solution
                    self._send_event("agent_complete", {"agent": agent_name, "solution": solution})
                except Exception as e:
                    error_msg = f"Agent {agent_name} failed during generation: {e}"
                    self._send_event("error", {"message": error_msg})
                    solutions[agent_name] = {"code": "", "error": error_msg}

        # 3. Execute Solutions
        self._send_event("status", {"message": "Executing and testing solutions..."})
        test_results: Dict[str, TestSuiteResult] = {}
        for agent_name, solution in solutions.items():
            if solution.get("error") or not solution.get("code"):
                # Create a placeholder result for failed agents
                test_results[agent_name] = TestSuiteResult(
                    agent_name=agent_name, total_tests=len(problem["test_cases"]), passed_tests=0,
                    results=[], avg_time_ms=0, max_memory_kb=0, has_errors=True,
                    compilation_error=solution.get("error", "No code generated.")
                )
                self._send_event("test_results", test_results[agent_name].__dict__)
                continue
            
            result = execute_in_sandbox(
                agent_name=agent_name,
                code=solution["code"],
                function_name=problem["function_name"],
                test_cases=problem["test_cases"]
            )
            test_results[agent_name] = result
            self._send_event("test_results", result.__dict__)

        # 4. Judge Solutions
        self._send_event("status", {"message": "Judging solutions..."})
        scores = self.judge.judge_solutions(solutions, test_results)
        self._send_event("scores", {"rankings": [s.__dict__ for s in scores]})
        
        # 5. Synthesize a final solution
        self._send_event("status", {"message": "Synthesizing final solution..."})
        synthesized_solution = self.synthesizer.synthesize(problem, solutions, scores)
        self._send_event("synthesis_complete", synthesized_solution)

        # 6. Return all results
        final_results = {
            "problem": problem,
            "solutions": solutions,
            "test_results": {name: tr.__dict__ for name, tr in test_results.items()},
            "scores": [s.__dict__ for s in scores],
            "synthesized_solution": synthesized_solution,
        }
        self._send_event("final_results", final_results)
        
        return final_results
