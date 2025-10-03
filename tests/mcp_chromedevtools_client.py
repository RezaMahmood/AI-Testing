import asyncio
from typing import Any, Dict, List
from mcp_client import GenericMCPClient
from mcp_dataclasses import MCPToolDefinition, MCPCapabilityType


class ChromeDevToolsClient(GenericMCPClient):
    """Specific MCP client for Chrome DevTools server"""
    
    def __init__(self, server_url: str = "http://localhost:3000/mcp"):
        super().__init__(server_url, "chrome-devtools")
        self.browser_session = None
    
    async def initialize_client(self):
        """Initialize Chrome DevTools specific setup"""
        print(f"🔧 Initializing Chrome DevTools MCP client for {self.server_url}")
        # Could add Chrome-specific initialization here
        # e.g., verify browser connection, set default timeouts, etc.
    
    async def cleanup_client(self):
        """Cleanup Chrome DevTools specific resources"""
        print(f"🧹 Cleaning up Chrome DevTools client resources")
        # Could add Chrome-specific cleanup here
    
    def get_supported_tool_methods(self) -> List[str]:
        """Chrome DevTools specific tool discovery methods"""
        return [
            "tools/list",
            "list_tools",
            "mcp_chrome-devtools_list_tools"  # Chrome DevTools specific
        ]
    
    def get_supported_call_methods(self) -> List[str]:
        """Chrome DevTools specific tool call methods"""
        return [
            "tools/call",
            "call_tool",
            # Chrome DevTools allows direct method calls
            "mcp_chrome-devtoo_navigate_page",
            "mcp_chrome-devtoo_take_screenshot",
            "mcp_chrome-devtoo_click",
            "mcp_chrome-devtoo_fill",
            "mcp_chrome-devtoo_take_snapshot"
        ]
    
    def parse_tool_response(self, response_data: Any) -> List[MCPToolDefinition]:
        """Parse Chrome DevTools server response into tool definitions"""
        tools = []
        
        # Handle Chrome DevTools specific response format
        if isinstance(response_data, dict):
            tools_list = response_data.get("tools", [response_data])
        else:
            tools_list = response_data if isinstance(response_data, list) else []
        
        for tool_data in tools_list:
            if isinstance(tool_data, dict) and "name" in tool_data:
                tool_def = MCPToolDefinition(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {}),
                    category=self._determine_chrome_tool_category(tool_data["name"]),
                    examples=self._get_chrome_tool_examples(tool_data["name"])
                )
                tools.append(tool_def)
        
        return tools
    
    def _determine_chrome_tool_category(self, tool_name: str) -> str:
        """Categorize Chrome DevTools based on name"""
        name_lower = tool_name.lower()
        
        if any(x in name_lower for x in ["navigate", "page"]):
            return "navigation"
        elif any(x in name_lower for x in ["click", "fill", "hover", "drag"]):
            return "interaction"
        elif any(x in name_lower for x in ["snapshot", "screenshot"]):
            return "inspection"
        elif any(x in name_lower for x in ["performance", "emulate"]):
            return "performance"
        elif any(x in name_lower for x in ["network", "console"]):
            return "debugging"
        else:
            return "other"
    
    def _get_chrome_tool_examples(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get usage examples for Chrome DevTools"""
        examples = {
            "mcp_chrome-devtoo_navigate_page": [
                {"url": "https://example.com", "timeout": 30000}
            ],
            "mcp_chrome-devtoo_click": [
                {"uid": "button_submit", "dblClick": False}
            ],
            "mcp_chrome-devtoo_fill": [
                {"uid": "input_email", "value": "test@example.com"}
            ],
            "mcp_chrome-devtoo_take_screenshot": [
                {"format": "png", "fullPage": True}
            ]
        }
        return examples.get(tool_name, [])
    
    # Chrome DevTools specific helper methods
    async def navigate_and_wait(self, url: str, wait_for_text: str = None, timeout: int = 30000) -> Any:
        """High-level navigation with optional wait"""
        # Navigate first
        nav_result = await self.call_tool("mcp_chrome-devtoo_navigate_page", {
            "url": url,
            "timeout": timeout
        })
        
        # Wait for specific text if provided
        if wait_for_text:
            await self.call_tool("mcp_chrome-devtoo_wait_for", {
                "text": wait_for_text,
                "timeout": timeout
            })
        
        return nav_result
    
    async def fill_and_submit_form(self, form_data: Dict[str, str], submit_button_uid: str) -> Any:
        """High-level form filling and submission"""
        # Fill form fields
        for uid, value in form_data.items():
            await self.call_tool("mcp_chrome-devtoo_fill", {
                "uid": uid,
                "value": value
            })
        
        # Click submit button
        return await self.call_tool("mcp_chrome-devtoo_click", {
            "uid": submit_button_uid
        })
    
    def get_chrome_capabilities_summary(self) -> Dict[str, Any]:
        """Get Chrome DevTools specific capabilities summary"""
        tools_by_category = {}
        for tool_name, tool in self.available_tools.items():
            category = tool.category or "other"
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append({
                "name": tool.name,
                "description": tool.description
            })
        
        return {
            "client_type": "Chrome DevTools",
            "server_url": self.server_url,
            "total_tools": len(self.available_tools),
            "categories": tools_by_category,
            "high_level_methods": [
                "navigate_and_wait",
                "fill_and_submit_form"
            ]
        }

