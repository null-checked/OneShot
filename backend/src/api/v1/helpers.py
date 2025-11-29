from pathlib import Path
from src.settings import fs_writer

def create_project_zip(project_path: str):
    """Background task to create project zip file."""
    try:
        fs_writer.create_zip(Path(project_path))
        print(f"✓ Created zip for: {project_path}")
    except Exception as e:
        print(f"✗ Failed to create zip: {e}")
