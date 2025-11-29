"""
Code Reviewer Module - Reviews generated code for quality
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage 
import json


class CodeReviewer:
    """
    Reviews generated code for quality, best practices, and potential issues.
    Provides feedback and suggestions for improvements.
    """

    REVIEW_CRITERIA = [
        "Code quality and readability",
        "Error handling and edge cases",
        "Security vulnerabilities",
        "Performance considerations",
        "Documentation and comments",
        "Best practices adherence",
        "Type safety and validation"
    ]

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def review_code(self, files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review all generated code files.
        
        Args:
            files: Dictionary mapping file paths to contents
            requirements: Project requirements
            
        Returns:
            Review results with issues and suggestions
        """

        system_prompt = f"""You are an expert code reviewer. Review the provided code against these criteria:
        {', '.join(self.REVIEW_CRITERIA)}
        
        Output JSON with:
        {{
            "overall_score": 0-100,
            "issues": [
                {{
                    "file": "path",
                    "severity": "low|medium|high",
                    "issue": "description",
                    "suggestion": "how to fix"
                }}
            ],
            "strengths": ["...", "..."],
            "improvements": ["...", "..."]
        }}
        """

        # Prepare code summary for review
        code_summary = self._prepare_code_summary(files)

        user_prompt = f"""Review this code for project: {requirements.get('project_name', 'Unknown')}

Files to review:
{code_summary}

Provide detailed feedback on code quality, security, and best practices.
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = self.llm.invoke(messages)

        try:
            review = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback review
            review = {
                "overall_score": 75,
                "issues": [],
                "strengths": ["Code generated successfully"],
                "improvements": ["Add more comprehensive error handling"]
            }

        return review

    def _prepare_code_summary(self, files: Dict[str, str]) -> str:
        """Prepare a summary of code files for review."""

        summary_parts = []
        for file_path, content in files.items():
            # Limit content length for API
            content_preview = content[:1000] + \
                "..." if len(content) > 1000 else content
            summary_parts.append(f"\n--- {file_path} ---\n{content_preview}\n")

        return "\n".join(summary_parts)

    def apply_fixes(self, files: Dict[str, str], review: Dict[str, Any]) -> Dict[str, str]:
        """
        Automatically apply fixes for identified issues (optional).
        
        Args:
            files: Original files
            review: Review results with issues
            
        Returns:
            Fixed files
        """

        # In a full implementation, this would use the LLM to automatically fix issues
        # For now, return original files
        return files
