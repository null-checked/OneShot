"""
This module provides a sandboxed environment for executing and testing code solutions.
"""

import json
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from typing import List, Any, Optional
import os
import psutil
import sys

from problem_parser import TestCase

# --- Data Structures for Execution Results ---

@dataclass
class ExecutionResult:
    """Result of a single test case execution."""
    passed: bool
    actual_output: Any
    expected_output: Any
    execution_time_ms: float
    error: Optional[str] = None

@dataclass
class TestSuiteResult:
    """Result of a full test suite execution for an agent's solution."""
    agent_name: str
    total_tests: int
    passed_tests: int
    results: List[ExecutionResult]
    avg_time_ms: float
    max_memory_kb: int
    has_errors: bool = False
    compilation_error: Optional[str] = None


# --- Test Runner Template ---

# This code will be written to a temporary file and executed in a sandbox.
TEST_RUNNER_TEMPLATE = """
import time
import json
import sys
import traceback
from typing import List, Any

# User's code will be injected here
{user_code}

def run_tests(test_cases: List[dict], function_name: str):
    results = []
    
    try:
        solution_func = globals()[function_name]
    except KeyError:
        print(json.dumps({{"error": f"Function '{function_name}' not found in the provided code."}}))
        return

    for case in test_cases:
        inputs = case['input']
        expected = case['expected']
        start_time = time.perf_counter()
        
        try:
            actual = solution_func(*inputs)
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000
            
            passed = (actual == expected)
            
            results.append({{
                "passed": passed,
                "actual_output": actual,
                "expected_output": expected,
                "execution_time_ms": execution_time_ms,
                "error": None
            }})

        except Exception as e:
            end_time = time.perf_counter()
            execution_time_ms = (end_time - start_time) * 1000
            results.append({{
                "passed": False,
                "actual_output": None,
                "expected_output": expected,
                "execution_time_ms": execution_time_ms,
                "error": f"{{type(e).__name__}}: {{str(e)}}"
            }})
            
    print(json.dumps(results))

if __name__ == "__main__":
    try:
        test_cases_json = sys.stdin.read()
        test_cases_data = json.loads(test_cases_json)
        func_name = sys.argv[1]
        run_tests(test_cases_data, func_name)
    except Exception as e:
        print(json.dumps({{"error": f"Test runner failed: {{type(e).__name__}} {{str(e)}}. Trace: {{traceback.format_exc()}}"}}))
"""

# --- Main Executor Function ---

def execute_in_sandbox(
    agent_name: str,
    code: str,
    function_name: str,
    test_cases: List[TestCase],
    timeout_seconds: float = 7.0
) -> TestSuiteResult:
    
    tmp_filepath = None
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as tmp_file:
        full_code = TEST_RUNNER_TEMPLATE.format(user_code=code)
        tmp_file.write(full_code)
        tmp_filepath = tmp_file.name

    max_mem = 0
    proc = None
    try:
        test_cases_json = json.dumps(test_cases)
        python_executable = sys.executable

        start_time = time.time()
        proc = subprocess.Popen(
            [python_executable, tmp_filepath, function_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        ps_proc = psutil.Process(proc.pid)

        while proc.poll() is None:
            try:
                mem_info = ps_proc.memory_info()
                max_mem = max(max_mem, mem_info.rss)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            
            if time.time() - start_time > timeout_seconds:
                ps_proc.kill()
                raise subprocess.TimeoutExpired(proc.args, timeout_seconds)
            
            time.sleep(0.01)

        stdout, stderr = proc.communicate()

        if proc.returncode != 0 and not stdout:
            return TestSuiteResult(
                agent_name=agent_name, total_tests=len(test_cases), passed_tests=0, results=[],
                avg_time_ms=0, max_memory_kb=int(max_mem / 1024), has_errors=True,
                compilation_error=f"Execution failed with code {proc.returncode}. Stderr: {stderr.strip()}"
            )

        try:
            output_data = json.loads(stdout)
            if isinstance(output_data, dict) and "error" in output_data:
                 return TestSuiteResult(
                    agent_name=agent_name, total_tests=len(test_cases), passed_tests=0, results=[],
                    avg_time_ms=0, max_memory_kb=0, has_errors=True,
                    compilation_error=output_data["error"]
                )
            execution_results_data = output_data
        except json.JSONDecodeError:
            return TestSuiteResult(
                agent_name=agent_name, total_tests=len(test_cases), passed_tests=0, results=[],
                avg_time_ms=0, max_memory_kb=int(max_mem / 1024), has_errors=True,
                compilation_error=f"Failed to parse JSON. Raw output: {stdout[:500]}"
            )

        results = [ExecutionResult(**res) for res in execution_results_data]
        passed_count = sum(1 for r in results if r.passed)
        total_time = sum(r.execution_time_ms for r in results if r.execution_time_ms is not None)
        avg_time = total_time / len(results) if results else 0

        return TestSuiteResult(
            agent_name=agent_name, total_tests=len(test_cases), passed_tests=passed_count,
            results=results, avg_time_ms=avg_time, max_memory_kb=int(max_mem / 1024),
            has_errors=any(r.error for r in results) or passed_count < len(test_cases)
        )

    except subprocess.TimeoutExpired:
        return TestSuiteResult(
            agent_name=agent_name, total_tests=len(test_cases), passed_tests=0, results=[],
            avg_time_ms=0, max_memory_kb=int(max_mem / 1024), has_errors=True,
            compilation_error=f"Execution timed out after {timeout_seconds} seconds."
        )
    
    except Exception as e:
         return TestSuiteResult(
            agent_name=agent_name, total_tests=len(test_cases), passed_tests=0, results=[],
            avg_time_ms=0, max_memory_kb=0, has_errors=True,
            compilation_error=f"An unexpected error occurred in the executor: {type(e).__name__} - {e}"
        )

    finally:
        if tmp_filepath and os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
