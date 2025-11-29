from pydantic import BaseModel, Field

class BuildRequest(BaseModel):
    """Request model for /build endpoint."""

    prompt: str = Field(
        description="User prompt describing the project to build",
        examples=["Create a REST API for a todo list with FastAPI and SQLite"]
    )


class BuildResponse(BaseModel):
    """Response model for /build endpoint."""

    status: str = Field(description="Status of the build process")
    project_name: str = Field(description="Name of the generated project")
    project_path: str = Field(description="Path to the generated project")
    files_count: int = Field(description="Number of files generated")
    download_url: str | None = Field(
        None, description="URL to download project zip")
    review_score: float | None = Field(
        None, description="Code review score")
    tests_passed: int | None = Field(
        None, description="Number of tests passed")
    error: str | None = Field(None, description="Error message if any")

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
