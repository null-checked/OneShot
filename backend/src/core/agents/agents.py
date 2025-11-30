"""
Agent Modules - All 9 agents for the multi-agent workflow
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any, List, Optional
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage

import json

from src.core.tools.search_tool import internet_search


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
    
    Output ONLY valid JSON with these fields:
    ```json
    {
        "project_name": "...",
        "description": "...",
        "features": ["...", "..."],
        "tech_stack": ["...", "..."],
        "platform": "...",
        "constraints": ["...", "..."]
    }
    ```
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "PromptAnalyzerAgent"

    def execute(self, user_prompt: str) -> Dict[str, Any]:
        """Analyze the user prompt and extract requirements."""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt=self.SYSTEM_PROMPT, name=self.name, debug=True)
        print(f"Analyzing prompt with {self.name}. User prompt: {user_prompt}")
        response = deep_agent.invoke(
            {
                "messages" : [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            }
        )
        
        try:
            result = json.loads(response) if isinstance(response, str) else response
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
    
    Output ONLY valid JSON, wrapped in triple backticks, with:
    ```json
    {
        "market_research_topics": ["...", "..."],
        "competitor_analysis": ["...", "..."],
        "documentation_needed": ["...", "..."],
        "best_practices": ["...", "..."]
    }
    ```
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "ResearchPlannerAgent"

    def execute(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan research based on requirements."""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt=self.SYSTEM_PROMPT, name=self.name, debug=True)
        print(f"Planning research with {self.name}.")
        # Ensure requirements is JSON-serializable
        serializable_requirements = self._ensure_json_serializable(requirements)
        
        user_prompt_content = f"Project requirements: {json.dumps(serializable_requirements, indent=2)}"
        
        response = deep_agent.invoke(
            {
                "messages" : [
                    { 
                        "role": "user",
                        "content": user_prompt_content
                    }
                ]
            }
        )
        
        try:
            result = json.loads(response) if isinstance(response, str) else response
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            result = {
                "market_research_topics": ["Industry best practices", "Similar solutions"],
                "competitor_analysis": [],
                "documentation_needed": requirements.get("tech_stack", []),
                "best_practices": []
            }
        return result
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
    
    Output ONLY valid JSON, wrapped in triple backticks, with:
    ```json
    {
        "market_insights": ["...", "..."],
        "existing_solutions": [{"name": "...", "features": ["...", "..."]}],
        "trends": ["...", "..."],
        "recommendations": ["...", "..."]
    }
    ```
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "MarketResearcherAgent"

    def execute(self, research_plan: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct market research."""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt=self.SYSTEM_PROMPT, name=self.name, debug=True)
        print(f"Conducting market research with {self.name}.")
        # Ensure inputs are JSON-serializable
        serializable_research_plan = self._ensure_json_serializable(research_plan)
        serializable_requirements = self._ensure_json_serializable(requirements)
        
        user_prompt_content = f"Research plan: {json.dumps(serializable_research_plan, indent=2)}\n\n" \
                              f"Requirements: {json.dumps(serializable_requirements, indent=2)}"
        
        response = deep_agent.invoke(
            {
                "messages" : [
                    { 
                        "role": "user",
                        "content": user_prompt_content
                    }
                ]
            }
        )
        
        try:
            result = json.loads(response) if isinstance(response, str) else response
        except json.JSONDecodeError:
            result = {
                "market_insights": ["Standard practices apply"],
                "existing_solutions": [],
                "trends": [],
                "recommendations": ["Follow industry standards"]
            }
        return result
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
    
    Output ONLY valid JSON, wrapped in triple backticks, with:
    ```json
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
    ```
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "ImplementationPlannerAgent"

    def execute(self, requirements: Dict[str, Any], research: Dict[str, Any]) -> Dict[str, Any]:
        """Create implementation plan."""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt=self.SYSTEM_PROMPT, name=self.name,debug=True)
        print(f"Generating implementation plan with {self.name}.")
        # Ensure inputs are JSON-serializable
        serializable_requirements = self._ensure_json_serializable(requirements)
        serializable_research = self._ensure_json_serializable(research)
        
        user_prompt_content = f"Requirements: {json.dumps(serializable_requirements, indent=2)}\n\nResearch: {json.dumps(serializable_research, indent=2)}"
        
        response = deep_agent.invoke(
            {
                "messages" : [
                    { 
                        "role": "user",
                        "content": user_prompt_content
                    }
                ]
            }
        )
        try:
            result = json.loads(response) if isinstance(response, str) else response
        except json.JSONDecodeError:
            result = {
                "architecture": "Modular architecture",
                "file_structure": {},
                "modules": [],
                "tech_stack_final": requirements.get("tech_stack", [])
            }
        return result

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
    
    Output ONLY valid JSON, wrapped in triple backticks, with:
    ```json
    {
        "documentation": {
            "framework_name": {
                "overview": "...",
                "key_concepts": ["...", "..."],
                "code_examples": ["...", "..."]
            }
        }
    }
    ```
    """

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.name = "DocumentationResearcherAgent"

    def execute(self, implementation_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Research documentation."""
        deep_agent = create_deep_agent(self.llm, tools=[internet_search], system_prompt=self.SYSTEM_PROMPT, name=self.name, debug=True)
        print(f"Researching documentation with {self.name}.")
        # Ensure inputs are JSON-serializable
        serializable_implementation_plan = self._ensure_json_serializable(implementation_plan)
        
        user_prompt_content = f"Tech stack: {json.dumps(serializable_implementation_plan.get('tech_stack_final', []), indent=2)}"
        
        response = deep_agent.invoke(
            {
                "messages" : [
                    { 
                        "role": "user",
                        "content": user_prompt_content
                    }
                ]
            }
        )

        try:
            result = json.loads(response) if isinstance(response, str) else response
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
