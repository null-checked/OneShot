"""
Filesystem Writer Tool - Writes generated files to disk
Part of the Multi-Agent Software Factory Generator
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import shutil


class FilesystemWriter:
    """
    Tool for writing generated project files to disk.
    Creates directory structure and writes files with proper encoding.
    """
    
    def __init__(self, base_output_dir: str = "generated_projects"):
        """
        Initialize the filesystem writer.
        
        Args:
            base_output_dir: Base directory for all generated projects
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True, parents=True)
    
    def create_project_structure(self, project_name: str) -> Path:
        """
        Create a new project directory with a unique name.
        
        Args:
            project_name: Name of the project to create
            
        Returns:
            Path to the created project directory
        """
        # Sanitize project name
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
        project_path = self.base_output_dir / safe_name
        
        # If exists, add counter
        counter = 1
        original_path = project_path
        while project_path.exists():
            project_path = Path(f"{original_path}_{counter}")
            counter += 1
        
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path
    
    def write_file(self, project_path: Path, file_path: str, content: str) -> bool:
        """
        Write a single file to the project directory.
        
        Args:
            project_path: Root path of the project
            file_path: Relative path of the file (e.g., "src/main.py")
            content: Content to write to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Written: {file_path}")
            return True
        except Exception as e:
            print(f"✗ Error writing {file_path}: {str(e)}")
            return False
    
    def write_files(self, project_path: Path, files: Dict[str, str]) -> Dict[str, bool]:
        """
        Write multiple files to the project directory.
        
        Args:
            project_path: Root path of the project
            files: Dictionary mapping file paths to their contents
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        for file_path, content in files.items():
            results[file_path] = self.write_file(project_path, file_path, content)
        return results
    
    def create_zip(self, project_path: Path) -> Optional[Path]:
        """
        Create a zip archive of the generated project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Path to the created zip file, or None if failed
        """
        try:
            zip_path = project_path.parent / f"{project_path.name}.zip"
            shutil.make_archive(
                str(project_path.parent / project_path.name),
                'zip',
                project_path
            )
            print(f"✓ Created zip: {zip_path}")
            return zip_path
        except Exception as e:
            print(f"✗ Error creating zip: {str(e)}")
            return None
    
    def get_project_summary(self, project_path: Path) -> Dict:
        """
        Generate a summary of the created project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dictionary with project statistics
        """
        files = []
        total_size = 0
        
        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(project_path)
                size = file_path.stat().st_size
                files.append({
                    "path": str(relative_path),
                    "size": size
                })
                total_size += size
        
        return {
            "project_name": project_path.name,
            "project_path": str(project_path),
            "total_files": len(files),
            "total_size_bytes": total_size,
            "files": files
        }
