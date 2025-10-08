# AI Testing Application - C4 Component Diagram

## Component Level Architecture

```mermaid
C4Component
    title Component Diagram for AI Testing Application

    Container_Boundary(pytest_container, "Test Execution Container") {
        Component(test_runner, "Test Runner", "pytest", "Discovers and executes test cases")
        Component(test_cases, "Test Case Components", "Python Classes", "Individual test implementations:<br/>- test_default_single_case<br/>- test_single_case_cache<br/>- test_csv_file_cases")
        Component(csv_parser, "CSV Parser", "Python", "Parses manual_tests.csv for batch testing")
    }

    Container_Boundary(agent_container, "AI Agent Container") {
        Component(mcp_agent, "MCP Agent Assert", "Python/Async", "Core testing agent with context management")
        Component(assertion_result, "Assertion Result", "Dataclass", "Test result data structure:<br/>- TestPassed: bool<br/>- Message: string")
    }

    Container_Boundary(semantic_kernel_container, "Semantic Kernel Container") {
        Component(kernel, "Semantic Kernel", "Microsoft SK", "AI orchestration framework")
        Component(azure_openai, "Azure OpenAI Service", "GPT Model", "AI analysis and decision making")
        Component(mcp_plugin, "MCP Chrome Plugin", "Plugin", "Browser automation capabilities")
    }

    Container_Boundary(mcp_container, "Model Context Protocol Container") {
        Component(mcp_stdio, "MCP Stdio Plugin", "Node.js", "Chrome DevTools communication bridge")
        Component(chrome_devtools, "Chrome DevTools", "Browser API", "Browser automation engine:<br/>- DOM manipulation<br/>- Performance monitoring<br/>- Screenshot capture<br/>- Network analysis")
    }

    Container_Boundary(telemetry_container, "Telemetry Container") {
        Component(app_insights, "Application Insights", "Azure Monitor", "Telemetry collection:<br/>- Logs<br/>- Traces<br/>- Metrics")
    }

    Container_Boundary(external_container, "External Systems") {
        Component(target_web, "Target Web Application", "Web App", "Application under test")
        Component(env_config, "Environment Config", "Config", "Azure OpenAI credentials<br/>and connection strings")
    }

    Rel(test_runner, test_cases, "Discovers & Executes")
    Rel(test_cases, csv_parser, "Uses", "For batch tests")
    Rel(test_cases, mcp_agent, "Initializes", "async context")
    
    Rel(mcp_agent, kernel, "Creates & Configures")
    Rel(mcp_agent, assertion_result, "Returns")
    
    Rel(kernel, azure_openai, "Uses", "AI analysis")
    Rel(kernel, mcp_plugin, "Loads", "Browser capabilities")
    
    Rel(mcp_plugin, mcp_stdio, "Communicates via", "stdio protocol")
    Rel(mcp_stdio, chrome_devtools, "Controls", "Browser automation")
    
    Rel(chrome_devtools, target_web, "Tests", "HTTP/WebSocket")
    
    Rel(azure_openai, app_insights, "Sends telemetry")
    Rel(kernel, app_insights, "Sends telemetry")
    
    Rel(mcp_agent, env_config, "Reads", "Configuration")
    Rel(azure_openai, env_config, "Authenticates")

    UpdateElementStyle(mcp_agent, $bgColor="#fff9c4", $borderColor="#f57f17")
    UpdateElementStyle(azure_openai, $bgColor="#e3f2fd", $borderColor="#1976d2")
    UpdateElementStyle(chrome_devtools, $bgColor="#e8f5e8", $borderColor="#388e3c")
    UpdateElementStyle(app_insights, $bgColor="#f1f8e9", $borderColor="#689f38")
```

## Component Responsibilities

### Test Execution Container
- **Test Runner**: pytest framework orchestrating test discovery and execution
- **Test Case Components**: Individual test implementations with different strategies
- **CSV Parser**: Batch test data processing from external CSV files

### AI Agent Container  
- **MCP Agent Assert**: Central orchestrator with async context management, MCP connection lifecycle
- **Assertion Result**: Standardized result format for test outcomes and AI analysis

### Semantic Kernel Container
- **Semantic Kernel**: Microsoft's AI orchestration framework managing plugins and services
- **Azure OpenAI Service**: GPT model providing intelligent test analysis and decision making
- **MCP Chrome Plugin**: Browser automation capabilities injected as kernel plugin

### Model Context Protocol Container
- **MCP Stdio Plugin**: Node.js bridge implementing MCP protocol for Chrome DevTools
- **Chrome DevTools**: Browser engine providing DOM manipulation, performance monitoring, and network analysis

### Telemetry Container
- **Application Insights**: Azure Monitor collecting logs, traces, and metrics from AI operations

### External Systems
- **Target Web Application**: System under test receiving automated interactions
- **Environment Config**: External configuration providing credentials and connection strings

## Key Interactions

1. **Test Discovery**: pytest discovers test methods and creates test case objects
2. **Agent Initialization**: Test cases initialize MCP Agent with async context management  
3. **Kernel Setup**: Agent configures Semantic Kernel with Azure OpenAI service and MCP plugin
4. **AI Analysis**: Kernel orchestrates AI analysis using GPT model and browser automation
5. **Browser Control**: MCP plugin communicates with Chrome DevTools via stdio protocol
6. **Result Processing**: AI analysis produces structured AssertionResult for pytest validation
7. **Telemetry**: AI operations send telemetry data to Application Insights for monitoring

## C4 Model Compliance

- **Components**: Individual software components with clear responsibilities
- **Containers**: Logical groupings of related components  
- **Relationships**: Explicit communication paths with interaction types
- **External Dependencies**: Clear boundary between internal and external systems
- **Technology Stack**: Specified implementation technologies for each component