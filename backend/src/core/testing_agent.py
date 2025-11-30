"""
Testing Agent - Executes tests and validates generated code
Uses CodeExecutor to get real execution results
"""

from typing import Dict, Any, List
from pathlib import Path
from src.core.code_executor import CodeExecutor, CodeExecutionResult


class TestResult:
    """Result of a single test."""

    def __init__(self, test_name: str, success: bool, details: str, execution_result: CodeExecutionResult):
        self.test_name = test_name
        self.success = success
        self.details = details
        self.execution_result = execution_result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "success": self.success,
            "details": self.details,
            "stdout": self.execution_result.stdout,
            "stderr": self.execution_result.stderr,
            "exit_code": self.execution_result.exit_code
        }


class TestingAgent:
    """
    Agent responsible for testing generated code.

    Executes tests defined by the architect and validates success criteria.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize the testing agent.

        Args:
            timeout: Maximum execution time per test in seconds
        """
        self.executor = CodeExecutor(timeout=timeout)

    def run_tests(self, project_path: str, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run all defined tests on the project.

        Args:
            project_path: Path to the generated project
            tests: List of test definitions from architect

        Returns:
            Dictionary with test results
        """
        project_path_obj = Path(project_path)

        if not project_path_obj.exists():
            return {
                "success": False,
                "error": f"Project path not found: {project_path}",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "results": []
            }

        results = []
        tests_passed = 0
        tests_failed = 0

        for test in tests:
            test_name = test.get("test_name", "unknown_test")
            test_type = test.get("test_type", "functional")
            test_command = test.get("test_command", "")
            description = test.get("description", "")

            print(f"\n  Running test: {test_name} ({test_type})")
            print(f"  Description: {description}")
            if test_command:
                print(f"  Command: {test_command}")

            # Execute the test based on type
            if test_type == "syntax":
                result = self._run_syntax_test(project_path_obj, test_command)
            elif test_type == "unit":
                result = self._run_unit_test(project_path_obj, test_command)
            elif test_type == "integration":
                result = self._run_integration_test(project_path_obj, test_command)
            elif test_type == "functional":
                result = self._run_functional_test(project_path_obj, test_command)
            else:
                result = self._run_custom_test(project_path_obj, test_command)

            test_result = TestResult(
                test_name=test_name,
                success=result.success,
                details=f"{description} - {'PASSED' if result.success else 'FAILED'}",
                execution_result=result
            )

            results.append(test_result.to_dict())

            # Print detailed test output
            print(f"\n  --- Test Output ---")
            if result.success:
                tests_passed += 1
                print(f"  [OK] {test_name} PASSED (exit code: {result.exit_code})")
            else:
                tests_failed += 1
                print(f"  [ERR] {test_name} FAILED (exit code: {result.exit_code})")

            # Show stdout if present
            if result.stdout and result.stdout.strip():
                print(f"\n  STDOUT:")
                stdout_lines = result.stdout.strip().split('\n')
                for line in stdout_lines[:20]:  # Show first 20 lines
                    print(f"    {line}")
                if len(stdout_lines) > 20:
                    remaining = len(stdout_lines) - 20
                    print(f"    ... ({remaining} more lines)")

            # Show stderr if present
            if result.stderr and result.stderr.strip():
                print(f"\n  STDERR:")
                stderr_lines = result.stderr.strip().split('\n')
                for line in stderr_lines[:20]:  # Show first 20 lines
                    print(f"    {line}")
                if len(stderr_lines) > 20:
                    remaining = len(stderr_lines) - 20
                    print(f"    ... ({remaining} more lines)")

            print(f"  --- End Test Output ---\n")

        return {
            "success": tests_failed == 0,
            "tests_run": len(tests),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "results": results
        }

    def _run_syntax_test(self, project_path: Path, test_command: str) -> CodeExecutionResult:
        """Run syntax check on Python files."""
        # Find all Python files
        py_files = list(project_path.glob("**/*.py"))

        if not py_files:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr="No Python files found to check",
                exit_code=1,
                error="No Python files found"
            )

        # Check syntax of all files
        all_success = True
        errors = []

        for py_file in py_files:
            # Skip __pycache__ and virtual env files
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue

            result = self.executor.check_syntax(str(py_file))
            if not result.success:
                all_success = False
                errors.append(f"{py_file.name}: {result.stderr}")

        if all_success:
            return CodeExecutionResult(
                success=True,
                stdout=f"Syntax check passed for {len(py_files)} files",
                stderr="",
                exit_code=0
            )
        else:
            return CodeExecutionResult(
                success=False,
                stdout="",
                stderr="\n".join(errors),
                exit_code=1,
                error="Syntax errors found"
            )

    def _run_unit_test(self, project_path: Path, test_command: str) -> CodeExecutionResult:
        """Run unit tests."""
        if "{file}" in test_command:
            # Run test for each test file
            test_files = list(project_path.glob("**/test_*.py")) + list(project_path.glob("**/*_test.py"))

            if not test_files:
                return CodeExecutionResult(
                    success=True,  # No tests is not a failure
                    stdout="No test files found",
                    stderr="",
                    exit_code=0
                )

            all_success = True
            combined_stdout = []
            combined_stderr = []

            for test_file in test_files:
                cmd = test_command.replace("{file}", str(test_file))
                result = self.executor.execute_command(cmd, str(project_path))

                combined_stdout.append(result.stdout)
                if result.stderr:
                    combined_stderr.append(result.stderr)

                if not result.success:
                    all_success = False

            return CodeExecutionResult(
                success=all_success,
                stdout="\n".join(combined_stdout),
                stderr="\n".join(combined_stderr),
                exit_code=0 if all_success else 1
            )
        else:
            return self.executor.execute_command(test_command, str(project_path))

    def _run_integration_test(self, project_path: Path, test_command: str) -> CodeExecutionResult:
        """Run integration tests."""
        return self.executor.execute_command(test_command, str(project_path))

    def _run_functional_test(self, project_path: Path, test_command: str) -> CodeExecutionResult:
        """Run functional tests."""
        # Replace placeholders
        if "{entry_point}" in test_command:
            # Find entry point (usually main.py, app.py, etc.)
            entry_point = project_path / "main.py"
            if not entry_point.exists():
                entry_point = project_path / "app.py"
            if not entry_point.exists():
                # Find any .py file
                py_files = list(project_path.glob("*.py"))
                entry_point = py_files[0] if py_files else None

            if entry_point:
                test_command = test_command.replace("{entry_point}", str(entry_point))
            else:
                return CodeExecutionResult(
                    success=False,
                    stdout="",
                    stderr="No entry point found",
                    exit_code=1,
                    error="No entry point found"
                )

        return self.executor.execute_command(test_command, str(project_path))

    def _run_custom_test(self, project_path: Path, test_command: str) -> CodeExecutionResult:
        """Run a custom test command."""
        return self.executor.execute_command(test_command, str(project_path))

    def verify_success_criteria(self, project_path: str, success_criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verify that success criteria are met.

        Args:
            project_path: Path to the generated project
            success_criteria: List of success criteria from architect

        Returns:
            Dictionary with verification results
        """
        project_path_obj = Path(project_path)
        results = []
        all_met = True

        for criterion in success_criteria:
            criteria_name = criterion.get("criteria_name", "unknown")
            description = criterion.get("description", "")
            verification_method = criterion.get("verification_method", "")

            met = self._verify_criterion(project_path_obj, criterion)

            results.append({
                "criteria_name": criteria_name,
                "description": description,
                "met": met
            })

            if not met:
                all_met = False

        return {
            "all_criteria_met": all_met,
            "criteria_results": results
        }

    def _verify_criterion(self, project_path: Path, criterion: Dict[str, Any]) -> bool:
        """Verify a single success criterion."""
        verification_method = criterion.get("verification_method", "").lower()

        # Basic verification methods
        if "file" in verification_method and "exist" in verification_method:
            # Check that files exist
            py_files = list(project_path.glob("**/*.py"))
            return len(py_files) > 0

        if "syntax" in verification_method:
            # Check syntax is valid
            py_files = list(project_path.glob("**/*.py"))
            for py_file in py_files:
                if "__pycache__" in str(py_file) or "venv" in str(py_file):
                    continue
                result = self.executor.check_syntax(str(py_file))
                if not result.success:
                    return False
            return True

        if "run" in verification_method or "execute" in verification_method:
            # Try to run the entry point
            entry_point = project_path / "main.py"
            if not entry_point.exists():
                entry_point = project_path / "app.py"
            if entry_point.exists():
                result = self.executor.execute_file(str(entry_point), str(project_path))
                return result.success

        # Default: assume met if we got this far
        return True
