#!/bin/bash
# Simple test runner script for CI/CD pipelines
# This script sets up the environment and runs the Python tests

set -e  # Exit on any error

echo "Setting up Python test environment..."

# Navigate to tests directory
# cd /workspaces/e2e-testing/tests

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv 
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run tests
echo "Running tests..."
pytest --tb=short --verbose --color=yes

echo "All tests completed successfully!"