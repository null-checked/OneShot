"""
LangGraph Pipeline - Orchestrates the 9-step workflow
Part of the Multi-Agent Software Factory Generator
"""

from typing import Dict, Any, TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import os

# Import all agent modules
from core.agents import (
    PromptAnalyzerAgent,
    ResearchPlannerAgent,
    MarketResearcherAgent,
    ImplementationPlannerAgent,
    DocumentationResearcherAgent,
    CodeImplementerAgent,
    CodeReviewerAgent,
    CodeTesterAgent,
    DocumentationWriterAgent
)
from core.builder import ProjectBuilder
from core.reviewer import CodeReviewer
from core.tester import CodeTester
from core.doc_writer import DocumentationWriter
from core.filesystem_writer import FilesystemWriter


# Define the state that flows through the graph
class WorkflowState(TypedDict):
    """State object that flows through the entire workflow."""
    user_prompt: str
    requirements: Dict[str, Any]
    research_plan: Dict[str, Any]
    market_research: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    documentation_research: Dict[str, Any]
    code_files: Dict[str, str]
    review_results: Dict[str, Any]
    test_results: Dict[str, Any]
    documentation_files: Dict[str, str]
    project_path: str
    error: str


class MultiAgentPipeline:
    """
    LangGraph-based pipeline orchestrating all 9 agents in sequence.
    
    The workflow:
    1. Prompt Analyzer -> Extract requirements
    2. Research Planner -> Plan research
    3. Market Researcher -> Conduct market research
    4. Implementation Planner -> Plan architecture
    5. Documentation Researcher -> Research tech docs
    6. Code Implementer -> Generate code
    7. Code Reviewer -> Review code
    8. Code Tester -> Generate tests
    9. Documentation Writer -> Write docs
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialize the pipeline with all agents.
        
        Args:
            openai_api_key: OpenAI API key for LLM access
        """
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        
        # Initialize specialized modules
        self.builder = ProjectBuilder(self.llm)
        self.reviewer = CodeReviewer(self.llm)
        self.tester = CodeTester(self.llm)
        self.doc_writer = DocumentationWriter(self.llm)
        self.fs_writer = FilesystemWriter()
        
        # Initialize all 9 agents
        self.prompt_analyzer = PromptAnalyzerAgent(self.llm)
        self.research_planner = ResearchPlannerAgent(self.llm)
        self.market_researcher = MarketResearcherAgent(self.llm)
        self.implementation_planner = ImplementationPlannerAgent(self.llm)
        self.documentation_researcher = DocumentationResearcherAgent(self.llm)
        self.code_implementer = CodeImplementerAgent(self.builder)
        self.code_reviewer = CodeReviewerAgent(self.reviewer)
        self.code_tester = CodeTesterAgent(self.tester)
        self.documentation_writer = DocumentationWriterAgent(self.doc_writer)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create graph
        workflow = StateGraph(WorkflowState)
        
        # Add all nodes (one for each step)
        workflow.add_node("step1_analyze_prompt", self._step1_analyze_prompt)
        workflow.add_node("step2_plan_research", self._step2_plan_research)
        workflow.add_node("step3_market_research", self._step3_market_research)
        workflow.add_node("step4_plan_implementation", self._step4_plan_implementation)
        workflow.add_node("step5_research_documentation", self._step5_research_documentation)
        workflow.add_node("step6_implement_code", self._step6_implement_code)
        workflow.add_node("step7_review_code", self._step7_review_code)
        workflow.add_node("step8_test_code", self._step8_test_code)
        workflow.add_node("step9_write_documentation", self._step9_write_documentation)
        workflow.add_node("step10_write_to_disk", self._step10_write_to_disk)
        
        # Define the flow (sequential execution)
        workflow.set_entry_point("step1_analyze_prompt")
        workflow.add_edge("step1_analyze_prompt", "step2_plan_research")
        workflow.add_edge("step2_plan_research", "step3_market_research")
        workflow.add_edge("step3_market_research", "step4_plan_implementation")
        workflow.add_edge("step4_plan_implementation", "step5_research_documentation")
        workflow.add_edge("step5_research_documentation", "step6_implement_code")
        workflow.add_edge("step6_implement_code", "step7_review_code")
        workflow.add_edge("step7_review_code", "step8_test_code")
        workflow.add_edge("step8_test_code", "step9_write_documentation")
        workflow.add_edge("step9_write_documentation", "step10_write_to_disk")
        workflow.add_edge("step10_write_to_disk", END)
        
        return workflow.compile()
    
    # ========================================================================
    # STEP IMPLEMENTATIONS
    # ========================================================================
    
    def _step1_analyze_prompt(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Analyze user prompt and extract requirements."""
        print("📝 Step 1: Analyzing user prompt...")
        
        try:
            requirements = self.prompt_analyzer.execute(state["user_prompt"])
            state["requirements"] = requirements
            print(f"✓ Requirements extracted for: {requirements.get('project_name', 'Unknown')}")
        except Exception as e:
            state["error"] = f"Step 1 error: {str(e)}"
            print(f"✗ Error in step 1: {e}")
        
        return state
    
    def _step2_plan_research(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Plan research activities."""
        print("🔍 Step 2: Planning research...")
        
        try:
            research_plan = self.research_planner.execute(state["requirements"])
            state["research_plan"] = research_plan
            print("✓ Research plan created")
        except Exception as e:
            state["error"] = f"Step 2 error: {str(e)}"
            print(f"✗ Error in step 2: {e}")
        
        return state
    
    def _step3_market_research(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Conduct market research."""
        print("📊 Step 3: Conducting market research...")
        
        try:
            market_research = self.market_researcher.execute(
                state["research_plan"],
                state["requirements"]
            )
            state["market_research"] = market_research
            print("✓ Market research completed")
        except Exception as e:
            state["error"] = f"Step 3 error: {str(e)}"
            print(f"✗ Error in step 3: {e}")
        
        return state
    
    def _step4_plan_implementation(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Plan implementation architecture."""
        print("🏗️  Step 4: Planning implementation...")
        
        try:
            implementation_plan = self.implementation_planner.execute(
                state["requirements"],
                state["market_research"]
            )
            state["implementation_plan"] = implementation_plan
            print("✓ Implementation plan created")
        except Exception as e:
            state["error"] = f"Step 4 error: {str(e)}"
            print(f"✗ Error in step 4: {e}")
        
        return state
    
    def _step5_research_documentation(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Research technical documentation."""
        print("📚 Step 5: Researching documentation...")
        
        try:
            documentation_research = self.documentation_researcher.execute(
                state["implementation_plan"]
            )
            state["documentation_research"] = documentation_research
            print("✓ Documentation research completed")
        except Exception as e:
            state["error"] = f"Step 5 error: {str(e)}"
            print(f"✗ Error in step 5: {e}")
        
        return state
    
    def _step6_implement_code(self, state: WorkflowState) -> WorkflowState:
        """Step 6: Generate code files."""
        print("💻 Step 6: Implementing code...")
        
        try:
            code_files = self.code_implementer.execute(
                state["implementation_plan"],
                state["requirements"],
                state["documentation_research"]
            )
            state["code_files"] = code_files
            print(f"✓ Generated {len(code_files)} code files")
        except Exception as e:
            state["error"] = f"Step 6 error: {str(e)}"
            print(f"✗ Error in step 6: {e}")
        
        return state
    
    def _step7_review_code(self, state: WorkflowState) -> WorkflowState:
        """Step 7: Review generated code."""
        print("🔎 Step 7: Reviewing code...")
        
        try:
            review_results = self.code_reviewer.execute(
                state["code_files"],
                state["requirements"]
            )
            state["review_results"] = review_results
            print(f"✓ Code review completed (Score: {review_results.get('overall_score', 'N/A')})")
        except Exception as e:
            state["error"] = f"Step 7 error: {str(e)}"
            print(f"✗ Error in step 7: {e}")
        
        return state
    
    def _step8_test_code(self, state: WorkflowState) -> WorkflowState:
        """Step 8: Generate and run tests."""
        print("🧪 Step 8: Testing code...")
        
        try:
            test_results = self.code_tester.execute(
                state["code_files"],
                state["requirements"]
            )
            state["test_results"] = test_results
            
            # Add test files to code files
            test_files = test_results.get("test_files", {})
            state["code_files"].update(test_files)
            
            print(f"✓ Tests generated and executed")
        except Exception as e:
            state["error"] = f"Step 8 error: {str(e)}"
            print(f"✗ Error in step 8: {e}")
        
        return state
    
    def _step9_write_documentation(self, state: WorkflowState) -> WorkflowState:
        """Step 9: Generate documentation."""
        print("📖 Step 9: Writing documentation...")
        
        try:
            documentation_files = self.documentation_writer.execute(
                state["requirements"],
                state["implementation_plan"],
                state["code_files"]
            )
            state["documentation_files"] = documentation_files
            print(f"✓ Generated {len(documentation_files)} documentation files")
        except Exception as e:
            state["error"] = f"Step 9 error: {str(e)}"
            print(f"✗ Error in step 9: {e}")
        
        return state
    
    def _step10_write_to_disk(self, state: WorkflowState) -> WorkflowState:
        """Step 10: Write all files to disk."""
        print("💾 Step 10: Writing files to disk...")
        
        try:
            project_name = state["requirements"].get("project_name", "generated_project")
            project_path = self.fs_writer.create_project_structure(project_name)
            
            # Combine all files
            all_files = {**state["code_files"], **state["documentation_files"]}
            
            # Write files
            self.fs_writer.write_files(project_path, all_files)
            
            state["project_path"] = str(project_path)
            print(f"✓ Project written to: {project_path}")
        except Exception as e:
            state["error"] = f"Step 10 error: {str(e)}"
            print(f"✗ Error in step 10: {e}")
        
        return state
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
    def run(self, user_prompt: str) -> Dict[str, Any]:
        """
        Run the complete 9-step workflow.
        
        Args:
            user_prompt: User's project description
            
        Returns:
            Final state with all results
        """
        print("=" * 70)
        print("🚀 Multi-Agent Software Factory - Starting Pipeline")
        print("=" * 70)
        
        # Initialize state
        initial_state = WorkflowState(
            user_prompt=user_prompt,
            requirements={},
            research_plan={},
            market_research={},
            implementation_plan={},
            documentation_research={},
            code_files={},
            review_results={},
            test_results={},
            documentation_files={},
            project_path="",
            error=""
        )
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        print("=" * 70)
        if final_state.get("error"):
            print(f"⚠️  Pipeline completed with errors: {final_state['error']}")
        else:
            print("✅ Pipeline completed successfully!")
        print("=" * 70)
        
        return final_state
