# AI Testing Application - ArchiMate Diagram

## Application Layer Architecture

```mermaid
graph TD
    %% Application Components
    subgraph "Test Execution Layer"
        A1[Test Runner<br/>Application Component<br/>pytest framework]
        A2[Test Case Manager<br/>Application Component<br/>Python test implementations]
        A3[CSV Data Parser<br/>Application Component<br/>Batch test data processor]
    end

    subgraph "AI Agent Layer"
        B1[MCP Agent Assert<br/>Application Component<br/>Core testing orchestrator]
        B2[Assertion Result Handler<br/>Application Component<br/>Test result processor]
    end

    subgraph "AI Processing Layer"
        C1[Semantic Kernel<br/>Application Component<br/>AI orchestration framework]
        C2[Azure OpenAI Service<br/>Application Service<br/>GPT analysis engine]
        C3[MCP Chrome Plugin<br/>Application Component<br/>Browser automation interface]
    end

    subgraph "Browser Automation Layer"
        D1[MCP Stdio Bridge<br/>Application Component<br/>Protocol communication]
        D2[Chrome DevTools Engine<br/>Application Component<br/>Browser control interface]
    end

    subgraph "Infrastructure Layer"
        E1[Application Insights<br/>Technology Service<br/>Telemetry collection]
        E2[Environment Configuration<br/>Data Object<br/>Credentials & settings]
    end

    subgraph "External Systems"
        F1[Target Web Application<br/>Application Component<br/>System under test]
    end

    %% Application Interfaces
    I1[Test Execution Interface]
    I2[AI Analysis Interface]
    I3[Browser Control Interface]
    I4[Telemetry Interface]
    I5[Configuration Interface]

    %% Data Objects
    DO1[Test Cases Data<br/>Data Object]
    DO2[Test Results Data<br/>Data Object]
    DO3[Browser Metrics Data<br/>Data Object]
    DO4[Telemetry Data<br/>Data Object]

    %% Application Functions
    AF1[Test Discovery Function<br/>Application Function]
    AF2[AI Decision Making Function<br/>Application Function]
    AF3[Browser Automation Function<br/>Application Function]
    AF4[Result Validation Function<br/>Application Function]

    %% Relationships - Serving
    A1 -->|serves| I1
    C1 -->|serves| I2
    D2 -->|serves| I3
    E1 -->|serves| I4
    E2 -->|serves| I5

    %% Relationships - Used By
    A1 -->|uses| AF1
    C2 -->|uses| AF2
    D2 -->|uses| AF3
    B2 -->|uses| AF4

    %% Relationships - Flow
    A1 -->|triggers| A2
    A2 -->|uses| A3
    A2 -->|initializes| B1
    B1 -->|configures| C1
    C1 -->|uses| C2
    C1 -->|loads| C3
    C3 -->|communicates via| D1
    D1 -->|controls| D2
    D2 -->|tests| F1

    %% Data Flow
    A3 -->|accesses| DO1
    B2 -->|produces| DO2
    D2 -->|captures| DO3
    C2 -->|generates| DO4

    %% Infrastructure Usage
    C2 -->|sends to| E1
    C1 -->|sends to| E1
    B1 -->|reads from| E2
    C2 -->|authenticates via| E2

    %% Styling for ArchiMate element types
    classDef applicationComponent fill:#b3d9ff,stroke:#0066cc,stroke-width:2px
    classDef applicationService fill:#ffcc99,stroke:#cc6600,stroke-width:2px
    classDef technologyService fill:#ccffcc,stroke:#009900,stroke-width:2px
    classDef dataObject fill:#ffffcc,stroke:#cccc00,stroke-width:2px
    classDef applicationFunction fill:#ffccff,stroke:#cc00cc,stroke-width:2px
    classDef applicationInterface fill:#ccccff,stroke:#6666cc,stroke-width:2px

    class A1,A2,A3,B1,B2,C1,C3,D1,D2,F1 applicationComponent
    class C2 applicationService
    class E1 technologyService
    class DO1,DO2,DO3,DO4,E2 dataObject
    class AF1,AF2,AF3,AF4 applicationFunction
    class I1,I2,I3,I4,I5 applicationInterface
```

## ArchiMate Element Mapping

### Application Components
| Component | ArchiMate Type | Description |
|-----------|----------------|-------------|
| Test Runner | Application Component | Encapsulates pytest framework functionality |
| Test Case Manager | Application Component | Manages individual test implementations |
| CSV Data Parser | Application Component | Processes batch test data from CSV files |
| MCP Agent Assert | Application Component | Core testing orchestrator with lifecycle management |
| Assertion Result Handler | Application Component | Processes and formats test outcomes |
| Semantic Kernel | Application Component | AI orchestration framework container |
| MCP Chrome Plugin | Application Component | Browser automation interface component |
| MCP Stdio Bridge | Application Component | Protocol communication bridge |
| Chrome DevTools Engine | Application Component | Browser control and automation |

### Application Services
| Service | ArchiMate Type | Description |
|---------|----------------|-------------|
| Azure OpenAI Service | Application Service | External GPT model providing AI analysis |

### Technology Services
| Service | ArchiMate Type | Description |
|---------|----------------|-------------|
| Application Insights | Technology Service | Azure Monitor telemetry infrastructure |

### Data Objects
| Data Object | ArchiMate Type | Description |
|-------------|----------------|-------------|
| Test Cases Data | Data Object | Structured test case information |
| Test Results Data | Data Object | Formatted test outcomes and analysis |
| Browser Metrics Data | Data Object | Performance and interaction measurements |
| Telemetry Data | Data Object | Operational monitoring information |
| Environment Configuration | Data Object | Credentials and connection settings |

### Application Functions
| Function | ArchiMate Type | Description |
|----------|----------------|-------------|
| Test Discovery Function | Application Function | Automated test case identification |
| AI Decision Making Function | Application Function | Intelligent pass/fail determination |
| Browser Automation Function | Application Function | Web interaction and data extraction |
| Result Validation Function | Application Function | Test outcome verification |

### Application Interfaces
| Interface | ArchiMate Type | Description |
|-----------|----------------|-------------|
| Test Execution Interface | Application Interface | pytest framework API |
| AI Analysis Interface | Application Interface | Semantic Kernel orchestration API |
| Browser Control Interface | Application Interface | Chrome DevTools Protocol API |
| Telemetry Interface | Application Interface | Application Insights logging API |
| Configuration Interface | Application Interface | Environment settings access API |

## ArchiMate Architectural Viewpoints

### Application Cooperation Viewpoint
Shows how application components collaborate to deliver the AI testing capability:
- **Test Runner** orchestrates the entire testing process
- **MCP Agent Assert** serves as the central coordinator
- **Semantic Kernel** manages AI processing workflows
- **Chrome DevTools Engine** provides browser automation

### Application Usage Viewpoint
Demonstrates how the system serves its primary function:
- **External Test Target** ← **Browser Automation** ← **AI Analysis** ← **Test Execution**

### Information Structure Viewpoint
Shows data flow and information dependencies:
- **Test Cases Data** → **Test Results Data** → **Telemetry Data**
- **Browser Metrics Data** → **AI Analysis** → **Decision Output**

### Technology Usage Viewpoint
Illustrates infrastructure dependencies:
- **Application Components** rely on **Azure OpenAI Service**
- **Telemetry** flows to **Application Insights Technology Service**
- **Configuration Data** supports **Authentication** and **Service Setup**

## Key ArchiMate Principles Applied

1. **Layered Architecture**: Clear separation between application and technology layers
2. **Service Orientation**: External services (Azure OpenAI) properly classified
3. **Data Flow**: Explicit data objects showing information lifecycle
4. **Interface Definition**: Clear APIs between major components
5. **Function Decomposition**: Business functions separated from structural elements
6. **Technology Dependencies**: Infrastructure services clearly identified

This ArchiMate representation provides an enterprise architecture view of the AI testing system, suitable for architectural governance and system understanding at the organizational level.