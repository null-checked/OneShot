"""
Multi-Agent Software Factory - FastAPI Backend
Main entry point with /build endpoint
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

from core.pipeline import MultiAgentPipeline
from core.filesystem_writer import FilesystemWriter

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Software Factory",
    description="AI-powered software project generator using multi-agent workflow",
    version="1.0.0"
)

# Global pipeline instance (initialized on startup)
pipeline: Optional[MultiAgentPipeline] = None
fs_writer = FilesystemWriter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class BuildRequest(BaseModel):
    """Request model for /build endpoint."""
    
    prompt: str = Field(
        ...,
        description="User prompt describing the project to build",
        example="Create a REST API for a todo list with FastAPI and SQLite"
    )
    openai_api_key: Optional[str] = Field(
        None,
        description="OpenAI API key (if not set in environment)"
    )


class BuildResponse(BaseModel):
    """Response model for /build endpoint."""
    
    status: str = Field(description="Status of the build process")
    project_name: str = Field(description="Name of the generated project")
    project_path: str = Field(description="Path to the generated project")
    files_count: int = Field(description="Number of files generated")
    download_url: Optional[str] = Field(None, description="URL to download project zip")
    review_score: Optional[float] = Field(None, description="Code review score")
    tests_passed: Optional[int] = Field(None, description="Number of tests passed")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "project_name": "my_project",
                "project_path": "generated_projects/my_project",
                "files_count": 12,
                "download_url": "/download/my_project",
                "review_score": 85.5,
                "tests_passed": 15,
                "error": None
            }
        }


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup."""
    global pipeline
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set in environment")
        print("   API key must be provided in each request")
    else:
        print("✓ OpenAI API key loaded from environment")
        pipeline = MultiAgentPipeline(openai_api_key)
        print("✓ Pipeline initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down Multi-Agent Software Factory...")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Multi-Agent Software Factory",
        "version": "1.0.0",
        "description": "AI-powered software project generator",
        "endpoints": {
            "/build": "POST - Generate a software project from a prompt",
            "/download/{project_name}": "GET - Download generated project as zip",
            "/projects": "GET - List all generated projects",
            "/project/{project_name}/details": "GET - Get detailed project information",
            "/health": "GET - Health check"
        },
        "workflow_steps": [
            "1. Analyze user prompt",
            "2. Plan research",
            "3. Conduct market research",
            "4. Plan implementation",
            "5. Research documentation",
            "6. Implement code",
            "7. Review code",
            "8. Test code",
            "9. Write documentation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "pipeline_initialized": pipeline is not None
    }


@app.post("/build", response_model=BuildResponse)
async def build_project(request: BuildRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint: Generate a complete software project from a user prompt.
    
    This endpoint orchestrates the full 9-step workflow:
    1. Analyze user prompt
    2. Plan research
    3. Conduct market research
    4. Plan implementation
    5. Research documentation
    6. Implement code
    7. Review code
    8. Test code
    9. Write documentation
    
    Returns the generated project path and metadata.
    """
    global pipeline
    
    # Get API key from request or environment
    api_key = request.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="OpenAI API key required. Set OPENAI_API_KEY environment variable or provide in request."
        )
    
    # Initialize pipeline if needed
    if pipeline is None:
        try:
            pipeline = MultiAgentPipeline(api_key)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize pipeline: {str(e)}"
            )
    
    # Run the pipeline
    try:
        print(f"\n{'='*70}")
        print(f"New build request: {request.prompt[:100]}...")
        print(f"{'='*70}\n")
        
        final_state = pipeline.run(request.prompt)
        
        # Extract results
        project_path = final_state.get("project_path", "")
        requirements = final_state.get("requirements", {})
        review_results = final_state.get("review_results", {})
        test_results = final_state.get("test_results", {})
        error = final_state.get("error", "")
        
        # Get project summary
        if project_path and Path(project_path).exists():
            summary = fs_writer.get_project_summary(Path(project_path))
            files_count = summary["total_files"]
            project_name = summary["project_name"]
            
            # Create zip in background
            background_tasks.add_task(create_project_zip, project_path)
            
            # Extract simple metrics
            tests_passed = None
            if test_results and "test_results" in test_results:
                test_info = test_results["test_results"]
                if isinstance(test_info, dict):
                    tests_passed = test_info.get("passed", test_info.get("total_tests"))
            
            # Prepare response with simplified data
            response = BuildResponse(
                status="success" if not error else "completed_with_errors",
                project_name=project_name,
                project_path=project_path,
                files_count=files_count,
                download_url=f"/download/{project_name}",
                review_score=review_results.get("overall_score") if review_results else None,
                tests_passed=tests_passed,
                error=error if error else None
            )
            
            return response
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Project generation failed: {error or 'Unknown error'}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Build failed: {str(e)}"
        )


@app.get("/download/{project_name}")
async def download_project(project_name: str):
    """
    Download a generated project as a zip file.
    
    Args:
        project_name: Name of the project to download
    """
    zip_path = Path("generated_projects") / f"{project_name}.zip"
    
    if not zip_path.exists():
        # Try to create it
        project_path = Path("generated_projects") / project_name
        if project_path.exists():
            created_zip = fs_writer.create_zip(project_path)
            if created_zip:
                zip_path = created_zip
            else:
                raise HTTPException(status_code=500, detail="Failed to create zip file")
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    
    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"{project_name}.zip"
    )


@app.get("/projects")
async def list_projects():
    """List all generated projects."""
    projects_dir = Path("generated_projects")
    
    if not projects_dir.exists():
        return {"projects": []}
    
    projects = []
    for item in projects_dir.iterdir():
        if item.is_dir():
            summary = fs_writer.get_project_summary(item)
            projects.append({
                "name": item.name,
                "path": str(item),
                "files_count": summary["total_files"],
                "size_bytes": summary["total_size_bytes"]
            })
    
    return {"projects": projects}


@app.get("/project/{project_name}/details")
async def get_project_details(project_name: str):
    """Get detailed information about a generated project."""
    project_path = Path("generated_projects") / project_name
    
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project not found")
    
    summary = fs_writer.get_project_summary(project_path)
    
    # Read README if it exists
    readme_content = None
    readme_path = project_path / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        except Exception:
            pass
    
    return {
        "project_name": summary["project_name"],
        "project_path": summary["project_path"],
        "total_files": summary["total_files"],
        "total_size_bytes": summary["total_size_bytes"],
        "files": summary["files"],
        "readme": readme_content
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_project_zip(project_path: str):
    """Background task to create project zip file."""
    try:
        fs_writer.create_zip(Path(project_path))
        print(f"✓ Created zip for: {project_path}")
    except Exception as e:
        print(f"✗ Failed to create zip: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """Run the FastAPI server."""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         MULTI-AGENT SOFTWARE FACTORY                         ║
    ║                                                              ║
    ║  AI-powered software project generator                       ║
    ║  Using LangChain, LangGraph, and Deep Agents                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment")
        print("   Please set it in .env file or environment variables")
        print("   Or provide it in each API request\n")
    
    # Run server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
