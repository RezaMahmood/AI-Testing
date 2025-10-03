# AI Testing Framework

A Python-based testing framework that uses AI agents to perform automated web testing through Chrome DevTools integration via Model Context Protocol (MCP).

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

### Run the sample test
```bash
source venv/bin/activate
python -m pytest test_agent_assert.py -v -s
```

The `-s` flag shows all output including the AI agent's analysis.

## How It Works

1. **Test Definition**: Write test cases with natural language instructions
2. **AI Agent**: The agent uses Chrome DevTools to navigate and interact with web pages
3. **Analysis**: AI compares actual results with expected outcomes
4. **Reporting**: Detailed pass/fail results with explanations

## Sample Test Case

The included test navigates to `https://developer.chrome.com`, clicks an "Explore Now" button, and validates the page response.

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

---

**Note**: This is a first draft. The framework is designed for automated web testing using AI agents and requires proper Azure OpenAI configuration to function.
