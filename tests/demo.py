"""
Demo script to show test framework working with both passing and failing tests.
This script temporarily modifies a test to demonstrate failure detection.
"""

import subprocess
import os
import sys


def run_demo():
    """Run demonstration of the test framework."""
    tests_dir = '/workspaces/e2e-testing/tests'
    os.chdir(tests_dir)
    
    print("=== Python Test Framework Demo ===\n")
    
    # First, run the normal tests (should pass)
    print("1. Running normal tests (should all pass):")
    print("-" * 50)
    result1 = subprocess.run([
        'bash', '-c', 
        'source venv/bin/activate && python -m pytest test_hello_world.py -v'
    ], capture_output=False)
    
    print(f"\nTest result: {'PASSED' if result1.returncode == 0 else 'FAILED'}")
    print(f"Exit code: {result1.returncode}\n")
    
    # Create a temporary failing test
    print("2. Creating a temporary failing test:")
    print("-" * 50)
    
    failing_test = '''
def test_intentional_failure():
    """This test is designed to fail for demonstration purposes."""
    test_string = "Hello World"
    expected_string = "Goodbye World"  # Intentionally wrong
    
    assert test_string == expected_string, f"Expected '{expected_string}', but got '{test_string}'"
'''
    
    # Append the failing test to the test file
    with open('test_hello_world.py', 'a') as f:
        f.write(failing_test)
    
    print("Added intentional failing test...")
    
    # Run tests again (should fail now)
    print("\n3. Running tests with failing test (should fail):")
    print("-" * 50)
    result2 = subprocess.run([
        'bash', '-c', 
        'source venv/bin/activate && python -m pytest test_hello_world.py -v'
    ], capture_output=False)
    
    print(f"\nTest result: {'PASSED' if result2.returncode == 0 else 'FAILED'}")
    print(f"Exit code: {result2.returncode}")
    
    # Restore the original test file
    print("\n4. Restoring original test file...")
    subprocess.run([
        'bash', '-c', 
        'cd /workspaces/e2e-testing/tests && git checkout test_hello_world.py 2>/dev/null || echo "File restored manually"'
    ])
    
    # Remove the failing test manually
    with open('test_hello_world.py', 'r') as f:
        content = f.read()
    
    # Remove the failing test section
    content = content.split('def test_intentional_failure')[0].rstrip()
    
    with open('test_hello_world.py', 'w') as f:
        f.write(content)
    
    print("Removed failing test, restored to original state.")
    
    print("\n=== Demo Complete ===")
    print("The test framework correctly:")
    print("✓ Passes when tests are correct")  
    print("✓ Fails when tests fail")
    print("✓ Provides clear error messages")
    print("✓ Returns appropriate exit codes for CI/CD")


if __name__ == "__main__":
    run_demo()