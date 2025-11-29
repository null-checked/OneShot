from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
from pathlib import Path

from src.core.pipeline import MultiAgentPipeline
from src.models.build import BuildRequest, BuildResponse
from src.settings import get_pipeline_agent, fs_writer
from src.api.v1.helpers import create_project_zip

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/build", response_model=BuildResponse)
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
    # Get API key from request or environment
    pipeline = get_pipeline_agent()

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
                    tests_passed = test_info.get(
                        "passed", test_info.get("total_tests"))

            # Prepare response with simplified data
            response = BuildResponse(
                status="success" if not error else "completed_with_errors",
                project_name=project_name,
                project_path=project_path,
                files_count=files_count,
                download_url=f"/download/{project_name}",
                review_score=review_results.get(
                    "overall_score") if review_results else None,
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


@router.get("/download/{project_name}")
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
                raise HTTPException(
                    status_code=500, detail="Failed to create zip file")
        else:
            raise HTTPException(status_code=404, detail="Project not found")

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename=f"{project_name}.zip"
    )


@router.get("/list")
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


@router.get("/{project_name}/details")
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
