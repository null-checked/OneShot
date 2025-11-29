"""
This module contains the Judge, which evaluates and ranks agent solutions.
"""

import ast
from dataclasses import dataclass
from typing import List, Dict

from agents import AgentSolution
from executor import TestSuiteResult

# --- Data Structure for Judging ---

@dataclass
class JudgeScore:
    """Represents the scores and rank of a single agent's solution."""
    agent_name: str
    correctness_score: float
    performance_score: float
    code_quality_score: float
    total_score: float
    rank: int = 0
    analysis: str = ""

# --- Judge Class ---

class Judge:
    """
    Evaluates and ranks agent solutions based on correctness, performance, and code quality.
    """
    CORRECTNESS_WEIGHT = 0.5
    PERFORMANCE_WEIGHT = 0.3
    QUALITY_WEIGHT = 0.2

    def _calculate_correctness_score(self, test_result: TestSuiteResult) -> float:
        """Calculates the correctness score based on passed tests."""
        if test_result.has_errors or test_result.total_tests == 0:
            return 0.0
        return (test_result.passed_tests / test_result.total_tests) * 100

    def _calculate_performance_scores(self, test_results: List[TestSuiteResult]) -> Dict[str, float]:
        """Calculates and normalizes performance scores for all agents."""
        scores = {}
        # Only fully correct solutions are eligible for performance points.
        successful_runs = [r for r in test_results if not r.has_errors and r.passed_tests == r.total_tests]

        if not successful_runs:
            return {r.agent_name: 0.0 for r in test_results}

        agent_times = {r.agent_name: r.avg_time_ms for r in successful_runs}
        
        if len(successful_runs) <= 1:
            for r_name in agent_times:
                scores[r_name] = 100.0
            return scores

        min_time = min(agent_times.values())
        max_time = max(agent_times.values())

        if min_time == max_time:
            for name in agent_times:
                scores[name] = 100.0
        else:
            # Normalize scores: fastest is 100, slowest is 0
            for name, time in agent_times.items():
                scores[name] = max(0, ((max_time - time) / (max_time - min_time)) * 100)

        # Assign 0 to agents who didn't pass all tests
        for r in test_results:
            if r.agent_name not in scores:
                scores[r.agent_name] = 0.0

        return scores

    def _calculate_code_quality_score(self, solution: AgentSolution) -> float:
        """Calculates code quality score using heuristics and AST analysis."""
        code = solution.get("code", "")
        if not code or code.isspace() or solution.get("error"):
            return 0.0

        score = 0
        try:
            tree = ast.parse(code)
            # Check for a function with a docstring
            if tree.body and isinstance(tree.body[0], ast.FunctionDef) and ast.get_docstring(tree.body[0]):
                score += 30
        except SyntaxError:
            return 0.0  # Unparseable code gets 0 quality score.

        # Comment count bonus
        comment_count = code.count('#')
        score += min(comment_count * 4, 30)

        # Line length and count considerations
        lines = code.splitlines()
        total_lines = len(lines)
        long_lines = sum(1 for line in lines if len(line) > 99)
        
        line_score = 40
        # Penalize for overly long code
        if total_lines > 50:
            line_score -= min(20, (total_lines - 50))
        # Penalize long lines
        line_score -= min(20, long_lines * 5)
        
        score += max(0, line_score)
        
        return max(0, min(100, score))

    def judge_solutions(
        self,
        solutions: Dict[str, AgentSolution],
        test_results: Dict[str, TestSuiteResult]
    ) -> List[JudgeScore]:
        """
        Judges all solutions and returns a ranked list of scores.
        """
        scores = []
        
        performance_scores = self._calculate_performance_scores(list(test_results.values()))

        for agent_name, solution in solutions.items():
            test_result = test_results.get(agent_name)
            if not test_result:
                continue

            correctness = self._calculate_correctness_score(test_result)
            performance = performance_scores.get(agent_name, 0.0)
            quality = self._calculate_code_quality_score(solution)

            total = (
                correctness * self.CORRECTNESS_WEIGHT +
                performance * self.PERFORMANCE_WEIGHT +
                quality * self.QUALITY_WEIGHT
            )
            
            scores.append(JudgeScore(
                agent_name=agent_name,
                correctness_score=round(correctness, 2),
                performance_score=round(performance, 2),
                code_quality_score=round(quality, 2),
                total_score=round(total, 2)
            ))

        # Rank scores
        scores.sort(key=lambda s: s.total_score, reverse=True)
        for i, score in enumerate(scores):
            score.rank = i + 1
            score.analysis = self._generate_analysis(score)
            
        return scores

    def _generate_analysis(self, score: JudgeScore) -> str:
        """Generates a brief textual analysis of the agent's performance."""
        if score.correctness_score < 100:
            return f"The solution from {score.agent_name} was not fully correct, failing some test cases."
        
        if score.total_score >= 90:
            return f"An outstanding solution by {score.agent_name} with excellent performance and quality."
        
        analysis_parts = []
        if score.performance_score > 75:
            analysis_parts.append("strong performance")
        elif score.performance_score > 40:
            analysis_parts.append("decent performance")
        else:
            analysis_parts.append("slow performance")

        if score.code_quality_score > 75:
            analysis_parts.append("high code quality")
        elif score.code_quality_score > 40:
            analysis_parts.append("acceptable code quality")
        else:
            analysis_parts.append("low code quality")

        return f"{score.agent_name} provided a correct solution with {', and '.join(analysis_parts)}."
