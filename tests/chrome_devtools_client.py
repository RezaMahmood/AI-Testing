import asyncio
import aiohttp
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass


class ChromeDevToolsMCPClient:
    def __init__(self, server_url: str = "http://localhost:3000/mcp"):
        self.server_url = server_url
        self.session = None
        self.available_tools = {}
        self.tool_schemas = {}
    
    async def discover_tools(self) -> Dict[str, Any]:
        """Discover all available tools from the MCP server"""
        response = await self.send_mcp_request("tools/list", {})
        
        if response.error:
            raise Exception(f"Failed to discover tools: {response.error}")
        
        # Parse tools and their schemas
        tools = response.result.get("tools", [])
        for tool in tools:
            tool_name = tool["name"]
            self.available_tools[tool_name] = tool
            self.tool_schemas[tool_name] = tool.get("inputSchema", {})
        
        return self.available_tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a discovered tool dynamically"""
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.available_tools.keys())}")
        
        response = await self.send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
        if response.error:
            raise Exception(f"Tool call failed: {response.error}")
        
        return response.result
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get the input schema for a specific tool"""
        return self.tool_schemas.get(tool_name, {})
    
    def list_available_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.available_tools.keys())