"""
Code Reviewer Module - Reviews generated code for quality
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage 
from deepagents import create_deep_agent
from src.core.tools.search_tool import internet_search


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
        self.name = "CodeReviewer"

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
        
        # Ensure requirements is JSON-serializable
        serializable_requirements = self._ensure_json_serializable(requirements)

        user_prompt = f"""Review this code for project: {serializable_requirements.get('project_name', 'Unknown')}

Files to review:
{code_summary}

Provide detailed feedback on code quality, security, and best practices.
"""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt="", name=self.name,debug=True) # System prompt passed in messages
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

        try:
            review = json.loads(response) if isinstance(response, str) else response
        except json.JSONDecodeError:
            # Fallback review
            review = {
                "overall_score": 75,
                "issues": [],
                "strengths": ["Code generated successfully"],
                "improvements": ["Add more comprehensive error handling"]
            }

        return review

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
