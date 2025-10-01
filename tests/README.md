# Python Test Framework

A simple Python testing framework using pytest for basic validation tests. This framework provides a minimal setup for running string validation tests that can be easily integrated into CI/CD pipelines.

## Features

- Simple "Hello World" string matching tests
- Virtual environment setup for isolated dependencies
- CI/CD ready with multiple runner scripts
- GitHub Actions workflow example
- Pytest configuration for consistent test execution

## Setup

### Method 1: Using the shell script (Recommended for CI/CD)
```bash
./run_tests.sh
```

### Method 2: Manual setup
1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

### Using the test runners:
```bash
# Shell script (handles environment setup)
./run_tests.sh

# Python script
python3 run_tests.py
```

### Using pytest directly:
```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest test_hello_world.py

# CI/CD friendly output
pytest --tb=short --verbose --color=yes
```

## Test Structure

- `test_hello_world.py`: Basic string matching tests including:
  - `test_hello_world_match()`: Tests exact string matching
  - `test_hello_world_case_sensitive()`: Verifies case sensitivity
  - `test_hello_world_exact_match()`: Tests string trimming functionality
- Tests follow pytest naming conventions (functions starting with `test_`)
- Each test includes descriptive docstrings and assertion messages

## CI/CD Integration

### GitHub Actions
A complete GitHub Actions workflow is provided in `.github/workflows/python-tests.yml` that:
- Sets up Python 3.11
- Creates virtual environment
- Installs dependencies
- Runs tests with XML output
- Uploads test results as artifacts

### Other CI/CD Systems
Use the provided scripts:
- `run_tests.sh`: Bash script for Unix-based systems
- `run_tests.py`: Python script for cross-platform compatibility

### Exit Codes
- `0`: All tests passed
- `1`: Test failures or setup errors

## Files Structure
```
tests/
├── venv/                       # Virtual environment (auto-created)
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Pytest configuration
├── test_hello_world.py        # Main test file
├── run_tests.sh               # Shell script runner
├── run_tests.py               # Python script runner
└── README.md                  # This file
```

## Extending the Framework

To add new tests:
1. Create new test files following the `test_*.py` naming pattern
2. Define test functions starting with `test_`
3. Use descriptive assertions with error messages
4. Run the test suite to verify everything works