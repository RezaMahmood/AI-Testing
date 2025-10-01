#!/usr/bin/env python3
"""
Test runner script for CI/CD integration.
This script runs the test suite and exits with appropriate codes.
"""

import sys
import subprocess
import os


def run_tests():
    """Run pytest and return the exit code."""
    # Change to the tests directory
    tests_dir = '/workspaces/e2e-testing/tests'
    os.chdir(tests_dir)
    
    try:
        # Activate virtual environment and run pytest
        result = subprocess.run([
            'bash', '-c', 
            'source venv/bin/activate && python -m pytest --tb=short --verbose --color=yes'
        ], cwd=tests_dir)
        
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install requirements first.")
        print("Run: source venv/bin/activate && pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)