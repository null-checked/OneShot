"""
Example client for the Multi-Agent Software Factory API
Demonstrates how to use the /build endpoint
"""

import requests
import json
import time
from pathlib import Path


class SoftwareFactoryClient:
    """Client for interacting with the Software Factory API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
    
    def health_check(self) -> dict:
        """Check if the API is healthy."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def build_project(self, prompt: str, openai_api_key: str = None) -> dict:
        """
        Build a software project from a prompt.
        
        Args:
            prompt: Description of the project to build
            openai_api_key: Optional OpenAI API key
            
        Returns:
            Build response with project information
        """
        payload = {"prompt": prompt}
        if openai_api_key:
            payload["openai_api_key"] = openai_api_key
        
        print(f"\n{'='*70}")
        print(f"Building project: {prompt[:60]}...")
        print(f"{'='*70}\n")
        
        response = requests.post(
            f"{self.base_url}/build",
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Build failed: {response.status_code} - {response.text}")
    
    def download_project(self, project_name: str, save_path: str = ".") -> Path:
        """
        Download a generated project.
        
        Args:
            project_name: Name of the project
            save_path: Directory to save the zip file
            
        Returns:
            Path to the downloaded file
        """
        response = requests.get(
            f"{self.base_url}/download/{project_name}",
            stream=True
        )
        
        if response.status_code == 200:
            file_path = Path(save_path) / f"{project_name}.zip"
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Downloaded: {file_path}")
            return file_path
        else:
            raise Exception(f"Download failed: {response.status_code}")
    
    def list_projects(self) -> list:
        """List all generated projects."""
        response = requests.get(f"{self.base_url}/projects")
        return response.json().get("projects", [])


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_1_simple_cli_tool():
    """Example 1: Build a simple CLI tool."""
    
    client = SoftwareFactoryClient()
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Build project
    prompt = """
    Create a command-line calculator tool in Python.
    Features:
    - Basic arithmetic operations (+, -, *, /)
    - Support for parentheses
    - Command history
    - Clear and user-friendly interface
    """
    
    try:
        result = client.build_project(prompt)
        
        print("\n" + "="*70)
        print("BUILD COMPLETED!")
        print("="*70)
        print(f"Project: {result['project_name']}")
        print(f"Path: {result['project_path']}")
        print(f"Files: {result['files_count']}")
        print(f"Review Score: {result.get('review_score', 'N/A')}")
        print(f"Download URL: {result.get('download_url')}")
        
        if result.get('error'):
            print(f"\n⚠️  Errors: {result['error']}")
        
        # Download the project
        client.download_project(result['project_name'])
        
    except Exception as e:
        print(f"Error: {e}")


def example_2_web_api():
    """Example 2: Build a REST API."""
    
    client = SoftwareFactoryClient()
    
    prompt = """
    Create a REST API for a task management system using FastAPI.
    Features:
    - CRUD operations for tasks (create, read, update, delete)
    - User authentication with JWT tokens
    - Task categories and priorities
    - Due dates and reminders
    - SQLite database
    - API documentation with Swagger
    """
    
    try:
        result = client.build_project(prompt)
        
        print("\n" + "="*70)
        print("BUILD COMPLETED!")
        print("="*70)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")


def example_3_data_analysis_tool():
    """Example 3: Build a data analysis tool."""
    
    client = SoftwareFactoryClient()
    
    prompt = """
    Create a data analysis tool for CSV files.
    Features:
    - Load and parse CSV files
    - Statistical analysis (mean, median, mode, std dev)
    - Data visualization with matplotlib
    - Export reports as PDF
    - Support for missing data handling
    - Interactive CLI interface
    """
    
    try:
        result = client.build_project(prompt)
        
        # Show results
        print(f"\n✅ Project: {result['project_name']}")
        print(f"📁 Location: {result['project_path']}")
        print(f"📄 Files: {result['files_count']}")
        
        # List all projects
        projects = client.list_projects()
        print(f"\n📚 Total projects generated: {len(projects)}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_4_custom_api_key():
    """Example 4: Build with custom API key."""
    
    client = SoftwareFactoryClient()
    
    # Read API key from environment or file
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    prompt = "Create a simple web scraper for news articles with BeautifulSoup"
    
    try:
        result = client.build_project(prompt, openai_api_key=api_key)
        print(f"✅ Built: {result['project_name']}")
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """Run example usage."""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     MULTI-AGENT SOFTWARE FACTORY - CLIENT EXAMPLES           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("\nMake sure the API server is running:")
    print("  python main.py\n")
    
    # Wait for user to start server
    input("Press Enter when server is ready...")
    
    # Run example 1
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple CLI Calculator")
    print("="*70)
    example_1_simple_cli_tool()
    
    # Uncomment to run other examples:
    # example_2_web_api()
    # example_3_data_analysis_tool()
    # example_4_custom_api_key()
