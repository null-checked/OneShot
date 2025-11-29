"""
Agent Modules - All 9 agents for the multi-agent workflow
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage

import json


# ============================================================================
# AGENT 1: Prompt Analyzer Agent
# ============================================================================

class PromptAnalyzerAgent:
    """
    Step 1: Analyzes user prompt and extracts key requirements.
    Outputs structured JSON with project requirements.
    """

    SYSTEM_PROMPT = """You are a requirements analyst. Your task is to analyze user prompts 
    and extract structured requirements for a software project.
    
    Extract:
    - Project name and description
    - Core features and functionality
    - Technology stack preferences
    - Target platform (web, mobile, desktop, CLI)
    - Any specific requirements or constraints
    
    Output valid JSON with these fields:
    {
        "project_name": "...",
        "description": "...",
        "features": ["...", "..."],
        "tech_stack": ["...", "..."],
        "platform": "...",
        "constraints": ["...", "..."]
    }
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze the user prompt and extract requirements."""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"User prompt: {user_prompt}")
        ]

        response = self.llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            result = {
                "project_name": "generated_project",
                "description": user_prompt,
                "features": [],
                "tech_stack": [],
                "platform": "web",
                "constraints": []
            }

        return result


# ============================================================================
# AGENT 2: Research Planner Agent
# ============================================================================

class ResearchPlannerAgent:
    """
    Step 2: Plans what research needs to be done based on requirements.
    Outputs a structured research plan.
    """

    SYSTEM_PROMPT = """You are a research planner. Based on project requirements,
    create a research plan to gather necessary information.
    
    Output JSON with:
    {
        "market_research_topics": ["...", "..."],
        "competitor_analysis": ["...", "..."],
        "documentation_needed": ["...", "..."],
        "best_practices": ["...", "..."]
    }
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan research based on requirements."""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=f"Project requirements: {json.dumps(requirements, indent=2)}")
        ]

        response = self.llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = {
                "market_research_topics": ["Industry best practices", "Similar solutions"],
                "competitor_analysis": [],
                "documentation_needed": requirements.get("tech_stack", []),
                "best_practices": []
            }

        return result


# ============================================================================
# AGENT 3: Market Researcher Agent
# ============================================================================

class MarketResearcherAgent:
    """
    Step 3: Conducts market research based on the research plan.
    In a real implementation, this would query APIs, search engines, etc.
    """

    SYSTEM_PROMPT = """You are a market researcher. Based on the research plan,
    provide insights about existing solutions, market trends, and best practices.
    
    Output JSON with:
    {
        "market_insights": ["...", "..."],
        "existing_solutions": [{"name": "...", "features": ["...", "..."]}],
        "trends": ["...", "..."],
        "recommendations": ["...", "..."]
    }
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, research_plan: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct market research."""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Research plan: {json.dumps(research_plan, indent=2)}\n\n"
                         f"Requirements: {json.dumps(requirements, indent=2)}")
        ]

        response = self.llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = {
                "market_insights": ["Standard practices apply"],
                "existing_solutions": [],
                "trends": [],
                "recommendations": ["Follow industry standards"]
            }

        return result


# ============================================================================
# AGENT 4: Implementation Planner Agent
# ============================================================================

class ImplementationPlannerAgent:
    """
    Step 4: Creates detailed implementation plan based on requirements and research.
    Outputs architecture, file structure, and module specifications.
    """

    SYSTEM_PROMPT = """You are a software architect. Create a detailed implementation plan
    including file structure, modules, and architecture.
    
    Output JSON with:
    {
        "architecture": "description of architecture pattern",
        "file_structure": {
            "src/main.py": "entry point",
            "src/models/": "data models",
            ...
        },
        "modules": [
            {
                "name": "...",
                "description": "...",
                "dependencies": ["...", "..."]
            }
        ],
        "tech_stack_final": ["...", "..."]
    }
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, requirements: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation plan."""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Requirements: {json.dumps(requirements, indent=2)}\n\n"
                         f"Research: {json.dumps(research, indent=2)}")
        ]

        response = self.llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = {
                "architecture": "Modular architecture",
                "file_structure": {},
                "modules": [],
                "tech_stack_final": requirements.get("tech_stack", [])
            }

        return result


# ============================================================================
# AGENT 5: Documentation Researcher Agent
# ============================================================================

class DocumentationResearcherAgent:
    """
    Step 5: Researches documentation for the chosen tech stack.
    Provides code examples and API references.
    """

    SYSTEM_PROMPT = """You are a documentation researcher. Provide relevant documentation
    excerpts, code examples, and API references for the tech stack.
    
    Output JSON with:
    {
        "documentation": {
            "framework_name": {
                "overview": "...",
                "key_concepts": ["...", "..."],
                "code_examples": ["...", "..."]
            }
        }
    }
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def execute(self, implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Research documentation."""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=f"Tech stack: {json.dumps(implementation_plan.get('tech_stack_final', []))}")
        ]

        response = self.llm.invoke(messages)

        try:
            result = json.loads(response.content)
        except json.JSONDecodeError:
            result = {"documentation": {}}

        return result


# ============================================================================
# AGENT 6: Code Implementer Agent
# ============================================================================

class CodeImplementerAgent:
    """
    Step 6: Generates actual code files based on the implementation plan.
    This is handled by builder.py module.
    """

    def __init__(self, builder_module):
        self.builder = builder_module

    def execute(self, implementation_plan: Dict[str, Any],
                requirements: Dict[str, Any],
                documentation: Dict[str, Any]) -> Dict[str, str]:
        """Generate code files."""
        return self.builder.generate_project_files(
            implementation_plan,
            requirements,
            documentation
        )


# ============================================================================
# AGENT 7: Code Reviewer Agent
# ============================================================================

class CodeReviewerAgent:
    """
    Step 7: Reviews generated code for quality, best practices, and issues.
    This is handled by reviewer.py module.
    """

    def __init__(self, reviewer_module):
        self.reviewer = reviewer_module

    def execute(self, files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Review generated code."""
        return self.reviewer.review_code(files, requirements)


# ============================================================================
# AGENT 8: Code Tester Agent
# ============================================================================

class CodeTesterAgent:
    """
    Step 8: Generates and runs tests for the code.
    This is handled by tester.py module.
    """

    def __init__(self, tester_module):
        self.tester = tester_module

    def execute(self, files: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and run tests."""
        return self.tester.generate_and_test(files, requirements)


# ============================================================================
# AGENT 9: Documentation Writer Agent
# ============================================================================

class DocumentationWriterAgent:
    """
    Step 9: Writes project documentation (README, architecture docs, etc.)
    This is handled by doc_writer.py module.
    """

    def __init__(self, doc_writer_module):
        self.doc_writer = doc_writer_module

    def execute(self, requirements: Dict[str, Any],
                implementation_plan: Dict[str, Any],
                files: Dict[str, str]) -> Dict[str, str]:
        """Generate documentation files."""
        return self.doc_writer.generate_documentation(
            requirements,
            implementation_plan,
            files
        )
