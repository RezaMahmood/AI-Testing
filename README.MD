# AI Testing Framework

A Python-based testing framework that uses AI to perform automated web testing through Chrome DevTools integration via Model Context Protocol (MCP). Features comprehensive telemetry with Azure Application Insights and support for batch test execution.

## Overview

This framework allows you to write natural language test cases that are executed by an AI agent using Chrome browser automation. The agent can navigate websites, interact with elements, and provide detailed analysis of test results.

### Key Features

- 🤖 **AI-Powered Testing**: Natural language test instructions executed by GPT-4
- 🌐 **Browser Automation**: Chrome DevTools integration via MCP for real browser testing
- 📊 **Azure Application Insights**: Comprehensive telemetry, logging, and performance monitoring
- 📋 **Batch Testing**: Execute multiple tests from CSV files with detailed reporting
- 🔄 **Immutable Test Execution**: Each test runs independently without context contamination
- 🚀 **GitHub Actions**: Automated testing workflows with result reporting

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
Create a `.env` file in the root directory with your Azure OpenAI and Application Insights credentials:
```
# Azure OpenAI Configuration (required)
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here

# Application Insights for Telemetry (optional but recommended)
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key;IngestionEndpoint=https://your-region.in.applicationinsights.azure.com/

# Semantic Kernel Telemetry Settings (optional)
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS=true
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS_SENSITIVE=true
```

**Note**: The Application Insights connection string should be in the format:
`InstrumentationKey=<guid>;IngestionEndpoint=<url>;LiveEndpoint=<url>;ApplicationId=<guid>`

## Running Tests

### Single Test Execution
Run a single default test case:
```bash
source venv/bin/activate
python -m pytest test_agent_assert.py::TestAgentAssert::test_default_single_case -v -s
```

### Batch Test Execution from CSV
Execute multiple test cases from the `manual_tests.csv` file:
```bash
source venv/bin/activate
python -m pytest test_agent_assert.py::TestAgentAssert::test_csv_file_cases -v -s
```

### Run All Tests
Execute all available tests:
```bash
source venv/bin/activate
python -m pytest test_agent_assert.py -v -s
```

The `-s` flag shows all output including the AI agent's analysis and telemetry information.

### Test Results and Telemetry

When Application Insights is configured, the framework automatically captures:
- 📈 **Performance Metrics**: Test execution times, API response times
- 📝 **Detailed Logs**: Semantic Kernel operations, MCP interactions
- 🔍 **Traces**: End-to-end test execution flows
- ⚠️ **Error Tracking**: Detailed exception information and stack traces

Access your telemetry data through the Azure Application Insights dashboard.

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

1. **Test Definition**: Write test cases with natural language instructions (single tests or CSV batches)
2. **AI Agent**: The agent uses Chrome DevTools to navigate and interact with web pages
3. **Telemetry Collection**: All interactions are logged to Azure Application Insights
4. **Analysis**: AI compares actual results with expected outcomes
5. **Reporting**: Detailed pass/fail results with explanations and performance metrics

## Test Case Formats

### Single Test Case
```python
test_case = TestCase(
    url="https://example.com",
    instructions="Navigate to the page and click the login button",
    expected_result="Should redirect to login page within 2 seconds"
)
```

### CSV Batch Testing
The framework includes a `manual_tests.csv` file with 10 sample test cases for Microsoft Learn Azure DevOps documentation. You can modify this file or create your own CSV with the following columns:
- `url`: The webpage to test
- `test_instructions`: Natural language testing instructions
- `expected_result`: Expected outcome description

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

- `agent_assert_mcp.py` - Main AI testing agent with telemetry integration
- `test_agent_assert.py` - Test execution framework with single and batch test support
- `assertion_result.py` - Test result data structure
- `manual_tests.csv` - Sample CSV file with 10 web testing scenarios
- `.env` - Environment configuration (create this file)

## Dependencies

- **Semantic Kernel** - AI orchestration framework with telemetry support
- **Chrome DevTools MCP** - Browser automation via Model Context Protocol
- **pytest** - Test framework
- **Azure OpenAI** - AI model for test analysis
- **Azure Monitor OpenTelemetry** - Telemetry collection and Application Insights integration

## GitHub Actions Workflow

The repository includes a GitHub Actions workflow that:
- Sets up the exact same environment as the devcontainer
- Installs all Python dependencies from `requirements.txt`
- Supports both single tests and CSV batch testing
- Captures comprehensive test results with telemetry data
- Uploads test artifacts for later analysis
- Integrates with Application Insights for CI/CD monitoring

The workflow is configured for **manual execution only** to avoid unnecessary runs during development.

## Telemetry and Monitoring

The framework provides comprehensive observability through Azure Application Insights:

### Automatic Data Collection
- **Request Telemetry**: Every test execution is tracked as a request
- **Dependency Telemetry**: Azure OpenAI API calls and response times
- **Custom Events**: Test pass/fail events with detailed context
- **Performance Counters**: System resource usage during testing
- **Exception Tracking**: Detailed error information with stack traces

### Dashboards and Alerts
Configure Azure Application Insights dashboards to monitor:
- Test success/failure rates over time
- Average test execution times
- API response times and availability
- Error trends and patterns
- Resource utilization during test runs

---

**Note**: This framework includes comprehensive telemetry and batch testing capabilities. The included tests may require proper Azure credentials and may fail initially, demonstrating real-world testing scenarios where tests need refinement based on actual website behavior and proper environment configuration. Use the Application Insights dashboard to monitor test performance and identify optimization opportunities.
