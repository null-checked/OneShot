#!/usr/bin/env python3
"""
Test CLI for Architect Pipeline
Simple command-line interface to test the new architect-based backend
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.architect_pipeline import ArchitectPipeline
from dotenv import load_dotenv
import json


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Test the Architect-Based Multi-Agent Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_cli.py

  # Direct prompt
  python test_cli.py --prompt "Create a Flask REST API for managing todos"

  # Specify output directory
  python test_cli.py --prompt "Build a CLI calculator" --output ./my_projects

  # Adjust max retries
  python test_cli.py --prompt "Simple web scraper" --retries 3

  # Verbose output
  python test_cli.py --prompt "Basic chatbot" --verbose
        """
    )

    parser.add_argument(
        "--prompt", "-p",
        type=str,
        help="Project description prompt"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="generated_projects",
        help="Output directory for generated projects (default: generated_projects)"
    )

    parser.add_argument(
        "--retries", "-r",
        type=int,
        default=5,
        help="Maximum retries per agent (default: 5)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output with detailed results"
    )

    parser.add_argument(
        "--save-results", "-s",
        type=str,
        help="Save results to JSON file"
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[ERR] Error: OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or export it:")
        print("  export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)

    # Get prompt
    if args.prompt:
        prompt = args.prompt
    else:
        print("\n" + "=" * 70)
        print("[ARCH]  Architect-Based Multi-Agent Pipeline - Test CLI")
        print("=" * 70)
        print("\nEnter your project description (or 'quit' to exit):")
        print("Example: Create a Flask REST API for managing a book library\n")

        prompt = input("Your prompt: ").strip()

        if prompt.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            sys.exit(0)

        if not prompt:
            print("[ERR] Error: Empty prompt")
            sys.exit(1)

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Change to output directory for file generation
    original_cwd = os.getcwd()
    os.chdir(output_dir.parent)

    try:
        # Initialize pipeline
        print(f"\n[START] Initializing pipeline (max retries: {args.retries})...")
        pipeline = ArchitectPipeline(
            openai_api_key=api_key,
            max_retries=args.retries
        )

        # Run pipeline
        print(f"\n[NOTE] Processing prompt: {prompt}\n")
        result = pipeline.run(prompt)

        # Display results
        print("\n" + "=" * 70)
        print("[DATA] RESULTS SUMMARY")
        print("=" * 70)

        print(f"\n[FOLDER] Project: {result['plan']['project_name']}")
        print(f"[LOC] Location: {result['project_path']}")
        print(f"[FILE] Files Generated: {result['files_generated']}")

        print(f"\n[AGENT] Agents Executed: {len(result['agent_results'])}")
        for agent in result['agent_results']:
            status = "[OK]" if agent['success'] else "[WARN]"
            print(f"  {status} {agent['name']}: {agent['files_generated']} files ({agent['attempts']} attempts)")

        print(f"\n[TEST] Tests:")
        print(f"  Total: {result['test_results']['tests_run']}")
        print(f"  Passed: {result['test_results']['tests_passed']}")
        print(f"  Failed: {result['test_results']['tests_failed']}")

        print(f"\n[OK] Success Criteria:")
        for criterion in result['criteria_results']['criteria_results']:
            status = "[OK]" if criterion['met'] else "[ERR]"
            print(f"  {status} {criterion['criteria_name']}")

        print(f"\n[TARGET] Overall Status: {'[OK] SUCCESS' if result['success'] else '[WARN]  COMPLETED WITH ISSUES'}")

        # Verbose output
        if args.verbose:
            print("\n" + "=" * 70)
            print("[LIST] DETAILED RESULTS")
            print("=" * 70)

            print("\n[ARCH]  Implementation Plan:")
            print(f"  Description: {result['plan']['description']}")
            print(f"  Tech Stack: {', '.join(result['plan']['tech_stack'])}")
            print(f"  Entry Point: {result['plan']['entry_point']}")

            print("\n[TOOL] Agents:")
            for agent in result['plan']['agents']:
                print(f"\n  - {agent['name']}")
                print(f"    Role: {agent['role']}")
                print(f"    Files: {', '.join(agent['files_to_generate'])}")

            print("\n[TEST] Test Results:")
            for test in result['test_results']['results']:
                print(f"\n  - {test['test_name']}: {'[OK] PASSED' if test['success'] else '[ERR] FAILED'}")
                print(f"    {test['details']}")
                if test['stderr']:
                    print(f"    Error: {test['stderr'][:200]}")

        # Save results to file if requested
        if args.save_results:
            results_file = Path(args.save_results)
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n[SAVE] Results saved to: {results_file}")

        print("\n" + "=" * 70)
        print(f"[DONE] Done! Your project is ready at: {result['project_path']}")
        print("=" * 70)

        # Return success exit code if successful
        sys.exit(0 if result['success'] else 1)

    except KeyboardInterrupt:
        print("\n\n[WARN]  Interrupted by user")
        sys.exit(130)

    except Exception as e:
        print(f"\n[ERR] Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    finally:
        # Restore original directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
