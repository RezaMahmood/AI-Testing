# AI Testing Framework

A Python-based testing framework that uses AI to perform automated web testing through Chrome DevTools integration via Model Context Protocol (MCP).

## Overview

This framework allows you to write natural language test cases that are executed by an AI agent using Chrome browser automation. The agent can navigate websites, interact with elements, and provide detailed analysis of test results.

## Prerequisites

- Python 3.11+
- Node.js (for Chrome DevTools MCP server)
- Azure OpenAI API access

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd AI-Testing
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory with your Azure OpenAI credentials:
```
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
```

## Running Tests

### Run the sample test locally
```bash
source venv/bin/activate
python -m pytest test_agent_assert.py -v -s
```

The `-s` flag shows all output including the AI agent's analysis.

### GitHub Actions Integration

This repository includes a GitHub Action workflow (`.github/workflows/python-tests.yml`) for automated testing:

- **Manual Trigger**: The workflow runs only when manually triggered from the GitHub Actions tab
- **Environment Setup**: Mirrors the devcontainer environment with Python 3.11, Node.js 20, and Chrome DevTools MCP
- **Test Reporting**: Generates comprehensive test reports using GitHub's native reporting tools
- **Artifact Upload**: Test results are saved as XML artifacts for download and analysis

To run tests via GitHub Actions:
1. Go to the **Actions** tab in your GitHub repository
2. Select **"Python Tests"** workflow
3. Click **"Run workflow"** 
4. Optionally specify a test filter pattern to run specific tests

## How It Works

1. **Test Definition**: Write test cases with natural language instructions
2. **AI Agent**: The agent uses Chrome DevTools to navigate and interact with web pages
3. **Analysis**: AI compares actual results with expected outcomes
4. **Reporting**: Detailed pass/fail results with explanations

## Sample Test Case

The included test (`test_agent_assert.py`) performs the following automated web testing:

1. **Target**: Navigates to `https://developer.chrome.com`
2. **Action**: Clicks the "Explore Now" button in the "What's new in Chrome" section
3. **Performance Assertion**: Validates that the page loads with HTTP status 200 and loads in less than 2 seconds
4. **AI Analysis**: Uses an AI agent to analyze the actual page behavior against expected results

### ⚠️ Expected Test Behavior

**This test will likely fail on first run** for several reasons:
- Requires Azure OpenAI API credentials in `.env` file
- Chrome DevTools MCP server must be properly configured
- Page load times may exceed 2 seconds depending on network conditions
- Website structure may have changed since test creation
- The "Explore Now" button location/text may have been updated

This is intentional to demonstrate realistic testing scenarios where tests need adjustment based on actual website conditions.

## Key Components

- `agent_assert_mcp.py` - Main AI testing agent using MCP
- `test_agent_assert.py` - Sample test case
- `assertion_result.py` - Test result data structure
- `.env` - Environment configuration (create this file)

## Dependencies

- **Semantic Kernel** - AI orchestration framework
- **Chrome DevTools MCP** - Browser automation via Model Context Protocol
- **pytest** - Test framework
- **Azure OpenAI** - AI model for test analysis

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that:
- Sets up the exact same environment as the devcontainer
- Installs all Python dependencies from `requirements.txt`
- Runs all tests in the project
- Captures test results for GitHub's reporting tools
- Uploads test artifacts for later analysis

The workflow is configured for **manual execution only** to avoid unnecessary runs during development.

---

**Note**: This is a first draft framework. The included test is intentionally challenging and may fail initially, demonstrating real-world testing scenarios where tests need refinement based on actual website behavior and proper environment configuration.
