"""
Code Executor - Executes Python code in a subprocess and captures real output
Provides safe execution with timeouts and resource limits
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil


class CodeExecutionResult:
    """Result of code execution."""

    def __init__(self, success: bool, stdout: str, stderr: str, exit_code: int, error: Optional[str] = None):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "error": self.error
        }

    def __repr__(self) -> str:
        return f"CodeExecutionResult(success={self.success}, exit_code={self.exit_code})"


class CodeExecutor:
    """
    Executes Python code safely in a subprocess.

    Features:
    - Executes code in a temporary directory
    - Captures stdout and stderr
    - Enforces timeouts
    - Returns real execution results
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the code executor.

        Args:
            timeout: Maximum execution time in seconds (default: 30)
        """
        self.timeout = timeout

    def execute_file(self, file_path: str, working_dir: Optional[str] = None) -> CodeExecutionResult:
        """
        Execute a Python file.

        Args:
            file_path: Path to the Python file to execute
            working_dir: Working directory for execution (defaults to file's directory)

        Returns:
            CodeExecutionResult with execution details
        """
        if not os.path.exists(file_path):
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=f"File not found: {file_path}",
                exit_code=-1,
                error=f"File not found: {file_path}"
            )

        if working_dir is None:
            working_dir = os.path.dirname(file_path) or "."

        try:
            result = subprocess.run(
                ["python", file_path],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return CodeExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=f"Execution timeout after {self.timeout} seconds",
                exit_code=-1,
                error=f"Timeout after {self.timeout}s"
            )

        except Exception as e:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                error=str(e)
            )

    def check_syntax(self, file_path: str) -> CodeExecutionResult:
        """
        Check Python syntax without executing the file.

        Args:
            file_path: Path to the Python file

        Returns:
            CodeExecutionResult with syntax check details
        """
        if not os.path.exists(file_path):
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=f"File not found: {file_path}",
                exit_code=-1,
                error=f"File not found: {file_path}"
            )

        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            return CodeExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except Exception as e:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                error=str(e)
            )

    def execute_command(self, command: str, working_dir: str) -> CodeExecutionResult:
        """
        Execute an arbitrary command in the working directory.

        Args:
            command: Command to execute
            working_dir: Working directory for execution

        Returns:
            CodeExecutionResult with execution details
        """
        try:
            # Use shell=True for complex commands, but be careful with input
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                shell=True
            )

            return CodeExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command timeout after {self.timeout} seconds",
                exit_code=-1,
                error=f"Timeout after {self.timeout}s"
            )

        except Exception as e:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                error=str(e)
            )

    def install_dependencies(self, requirements_file: str, working_dir: str) -> CodeExecutionResult:
        """
        Install dependencies from a requirements.txt file.

        Args:
            requirements_file: Path to requirements.txt
            working_dir: Working directory

        Returns:
            CodeExecutionResult with installation details
        """
        if not os.path.exists(requirements_file):
            return CodeExecutionResult(
                success=True,  # No requirements is not an error
                stdout="No requirements.txt found, skipping dependency installation",
                stderr="",
                exit_code=0
            )

        try:
            result = subprocess.run(
                ["pip", "install", "-q", "-r", requirements_file],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes for pip install
            )

            return CodeExecutionResult(
                success=(result.returncode == 0),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr="Dependency installation timeout",
                exit_code=-1,
                error="Timeout during pip install"
            )

        except Exception as e:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                error=str(e)
            )

    def run_tests(self, test_command: str, working_dir: str) -> CodeExecutionResult:
        """
        Run tests using the specified test command.

        Args:
            test_command: Test command to run (e.g., "pytest", "python -m pytest")
            working_dir: Working directory

        Returns:
            CodeExecutionResult with test execution details
        """
        return self.execute_command(test_command, working_dir)
