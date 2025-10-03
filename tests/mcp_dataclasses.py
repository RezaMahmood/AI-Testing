from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Protocol
from enum import Enum
from abc import ABC, abstractmethod

@dataclass
class McpRequest:
    method: str
    parameters: Dict[str, Any]
    id: str
    jsonrpc: str = "2.0"

@dataclass
class McpResponse:
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    jsonrpc: Optional[str] = None
    

class MCPCapabilityType(Enum):
    TOOLS = "tools"
    RESOURCES = "resources" 
    PROMPTS = "prompts"

@dataclass
class DiscoveredCapability:
    name: str
    type: MCPCapabilityType
    description: str
    schema: Dict[str, Any]
    server_name: str
    metadata: Dict[str, Any]

# NEW: Add base capability interface
class IMCPCapability(Protocol):
    """Protocol defining the interface for MCP capabilities"""
    name: str
    description: str
    schema: Dict[str, Any]
    
    async def execute(self, arguments: Dict[str, Any]) -> Any:
        """Execute this capability with given arguments"""
        ...

# NEW: Add client interface
class IMCPClient(Protocol):
    """Protocol defining the interface for MCP clients"""
    server_name: str
    server_url: str
    
    async def discover_capabilities(self) -> Dict[str, Any]:
        """Discover server capabilities"""
        ...
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool"""
        ...
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get discovered tools"""
        ...

# NEW: Add server configuration with validation
@dataclass
class MCPServerConfig:
    name: str
    url: str
    client_class: str  # Fully qualified class name like "mcp_chromedevtools_client.ChromeDevToolsClient"
    capabilities: Optional[List[MCPCapabilityType]] = None
    authentication: Optional[Dict[str, str]] = None
    timeout: int = 30
    connection_params: Optional[Dict[str, Any]] = None  # Client-specific params

# NEW: Add tool definition contract
@dataclass
class MCPToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None

# NEW: Add server capability manifest
@dataclass
class MCPServerManifest:
    server_name: str
    version: str
    tools: List[MCPToolDefinition]
    resources: Optional[List[Dict[str, Any]]] = None
    prompts: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None