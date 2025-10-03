from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import asyncio
import aiohttp
from mcp_dataclasses import McpRequest, McpResponse, IMCPClient, MCPToolDefinition



class GenericMCPClient(ABC, IMCPClient):
    """Abstract base class for all MCP clients"""
    
    def __init__(self, server_url: str, server_name: str = "mcp-server"):
        self.server_url = server_url
        self.server_name = server_name
        self.session = None
        self.available_tools = {}
        self.server_info = {}
        self._tool_definitions: List[MCPToolDefinition] = []
    
    # Keep existing session management methods as-is
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        await self.initialize_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_client()
        if self.session:
            await self.session.close()
    
    # Abstract methods that subclasses must implement
    @abstractmethod
    async def initialize_client(self):
        """Initialize client-specific setup"""
        pass
    
    @abstractmethod
    async def cleanup_client(self):
        """Cleanup client-specific resources"""
        pass
    
    @abstractmethod
    def get_supported_tool_methods(self) -> List[str]:
        """Return list of tool discovery methods this client supports"""
        pass
    
    @abstractmethod
    def get_supported_call_methods(self) -> List[str]:
        """Return list of tool call methods this client supports"""
        pass
    
    @abstractmethod
    def parse_tool_response(self, response_data: Any) -> List[MCPToolDefinition]:
        """Parse server response into tool definitions"""
        pass
    
    # Concrete methods that can be used by all subclasses
    async def send_mcp_request(self, method: str, parameters: Dict[str, Any] = None) -> McpResponse:
        """Send generic MCP request - implementation stays the same"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": parameters or {},
            "id": str(hash(f"{method}{parameters}"))
        }
        
        try:
            async with self.session.post(
                self.server_url,
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    return McpResponse(error={"message": f"HTTP {response.status}: {response.reason}"})
                
                response_data = await response.json()
                return McpResponse(
                    result=response_data.get("result"),
                    error=response_data.get("error"),
                    id=response_data.get("id"),
                    jsonrpc=response_data.get("jsonrpc")
                )
        except asyncio.TimeoutError:
            return McpResponse(error={"message": "Request timeout"})
        except Exception as e:
            return McpResponse(error={"message": str(e)})
    
    async def discover_capabilities(self) -> Dict[str, Any]:
        """Discover capabilities using client-specific methods"""
        capabilities = {
            "server_name": self.server_name,
            "server_url": self.server_url,
            "tools": {},
            "client_type": self.__class__.__name__
        }
        
        # Use client-specific discovery methods
        await self._discover_tools_with_client_methods(capabilities)
        return capabilities
    
    async def _discover_tools_with_client_methods(self, capabilities: Dict[str, Any]):
        """Discover tools using client-specific methods"""
        supported_methods = self.get_supported_tool_methods()
        
        for method in supported_methods:
            try:
                response = await self.send_mcp_request(method)
                if not response.error and response.result:
                    # Use client-specific parsing
                    tool_definitions = self.parse_tool_response(response.result)
                    
                    for tool_def in tool_definitions:
                        self.available_tools[tool_def.name] = tool_def
                        capabilities["tools"][tool_def.name] = {
                            "name": tool_def.name,
                            "description": tool_def.description,
                            "inputSchema": tool_def.input_schema,
                            "category": tool_def.category
                        }
                    
                    if capabilities["tools"]:
                        break
            except Exception as e:
                continue
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call tool using client-specific methods"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not found in {self.server_name}")
        
        supported_methods = self.get_supported_call_methods()
        
        for method in supported_methods:
            try:
                result = await self._try_call_method(method, tool_name, arguments)
                if result is not None:
                    return result
            except Exception as e:
                continue
        
        raise Exception(f"Failed to call tool '{tool_name}' using any supported method")
    
    async def _try_call_method(self, method: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Try calling tool with specific method"""
        if method == tool_name:
            response = await self.send_mcp_request(method, arguments)
        else:
            response = await self.send_mcp_request(method, {
                "name": tool_name,
                "arguments": arguments
            })
        
        if response.error:
            raise Exception(f"Tool call failed: {response.error}")
        
        return response.result
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get available tools"""
        return {name: {
            "name": tool.name,
            "description": tool.description,
            "schema": tool.input_schema,
            "category": tool.category
        } for name, tool in self.available_tools.items()}