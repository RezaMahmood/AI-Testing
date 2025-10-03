import asyncio
import subprocess
import json
from typing import Any, Dict, List, Optional


class ChromeDevToolsClient:
    """MCP client for Chrome DevTools server using stdio subprocess communication"""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.stdin_writer: Optional[asyncio.StreamWriter] = None
        self.stdout_reader: Optional[asyncio.StreamReader] = None
        self.request_id = 0
        self.pending_requests = {}
        self.available_tools = {}
        self.server_name = "chrome-devtools"
        self._response_task = None
    
    async def start_server(self):
        """Launch the MCP server as subprocess"""
        print(f"� Starting Chrome DevTools MCP server...")
        
        self.process = await asyncio.create_subprocess_exec(
            "npx", "chrome-devtools-mcp@latest",
            "headless", "true",
            "isolated", "true", "y",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.stdin_writer = self.process.stdin
        self.stdout_reader = self.process.stdout
        
        # Start background task to read responses
        self._response_task = asyncio.create_task(self._read_responses())
        
        print(f"✅ Chrome DevTools MCP server started with PID {self.process.pid}")
    
    async def cleanup(self):
        """Clean up resources"""
        print(f"🧹 Cleaning up Chrome DevTools client resources")
        
        if self._response_task:
            self._response_task.cancel()
            try:
                await self._response_task
            except asyncio.CancelledError:
                pass
        
        if self.stdin_writer:
            self.stdin_writer.close()
            await self.stdin_writer.wait_closed()
        
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print(f"🔚 Chrome DevTools MCP server stopped")
    
    async def send_jsonrpc_request(self, method: str, params: dict = None) -> dict:
        """Send JSON-RPC 2.0 request to MCP server"""
        if not self.stdin_writer:
            raise RuntimeError("MCP server not started. Call start_server() first.")
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[self.request_id] = future
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.stdin_writer.write(request_json.encode('utf-8'))
        await self.stdin_writer.drain()
        
        # Wait for response
        return await future

    async def send_jsonrpc_notification(self, method: str, params: dict = None):
        """Send JSON-RPC notification (no response expected)"""
        if not self.stdin_writer:
            raise RuntimeError("MCP server not started. Call start_server() first.")
        
        notification = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if params:
            notification["params"] = params
        
        notification_json = json.dumps(notification) + "\n"
        self.stdin_writer.write(notification_json.encode('utf-8'))
        await self.stdin_writer.drain()

    async def _read_responses(self):
        """Background task to read JSON-RPC responses"""
        try:
            async for line in self.stdout_reader:
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                
                try:
                    response = json.loads(line)
                    request_id = response.get("id")
                    
                    if request_id in self.pending_requests:
                        future = self.pending_requests.pop(request_id)
                        if "error" in response:
                            future.set_exception(Exception(f"MCP Error: {response['error']}"))
                        else:
                            future.set_result(response.get("result"))
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing JSON response: {e}, line: {line}")
                except Exception as e:
                    print(f"❌ Error processing response: {e}")
        except asyncio.CancelledError:
            # Task was cancelled, this is expected during cleanup
            pass
        except Exception as e:
            print(f"❌ Error in response reader: {e}")
    
    async def initialize_mcp_connection(self):
        """Initialize MCP connection with proper handshake"""
        print("🤝 Initializing MCP connection...")
        
        # Send initialize request
        init_response = await self.send_jsonrpc_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "ChromeDevToolsClient",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification
        await self.send_jsonrpc_notification("notifications/initialized")
        
        print("✅ MCP connection initialized")
        return init_response

    async def discover_capabilities(self) -> dict:
        """Discover available tools from MCP server"""
        print("🔍 Discovering Chrome DevTools capabilities...")
        
        # List available tools
        tools_response = await self.send_jsonrpc_request("tools/list")
        
        # Parse and store tools
        if "tools" in tools_response:
            for tool in tools_response["tools"]:
                self.available_tools[tool["name"]] = tool
        
        print(f"✅ Discovered {len(self.available_tools)} tools")
        
        return {
            "tools": self.available_tools,
            "server_name": self.server_name
        }

    async def call_tool(self, tool_name: str, arguments: dict = None) -> any:
        """Call a specific tool using MCP protocol"""
        return await self.send_jsonrpc_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_server()
        await self.initialize_mcp_connection()
        await self.discover_capabilities()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
    
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
            "mcp_chrome-devtools_navigate_page": [
                {"url": "https://example.com", "timeout": 30000}
            ],
            "mcp_chrome-devtools_click": [
                {"uid": "button_submit", "dblClick": False}
            ],
            "mcp_chrome-devtools_fill": [
                {"uid": "input_email", "value": "test@example.com"}
            ],
            "mcp_chrome-devtools_take_screenshot": [
                {"format": "png", "fullPage": True}
            ]
        }
        return examples.get(tool_name, [])
    
    # Chrome DevTools specific helper methods
    async def navigate_and_wait(self, url: str, wait_for_text: str = None, timeout: int = 30000) -> Any:
        """High-level navigation with optional wait"""
        # Navigate first
        nav_result = await self.call_tool("mcp_chrome-devtools_navigate_page", {
            "url": url,
            "timeout": timeout
        })
        
        # Wait for specific text if provided
        if wait_for_text:
            await self.call_tool("mcp_chrome-devtools_wait_for", {
                "text": wait_for_text,
                "timeout": timeout
            })
        
        return nav_result
    
    async def fill_and_submit_form(self, form_data: Dict[str, str], submit_button_uid: str) -> Any:
        """High-level form filling and submission"""
        # Fill form fields
        for uid, value in form_data.items():
            await self.call_tool("mcp_chrome-devtools_fill", {
                "uid": uid,
                "value": value
            })
        
        # Click submit button
        return await self.call_tool("mcp_chrome-devtools_click", {
            "uid": submit_button_uid
        })
    
    def get_chrome_capabilities_summary(self) -> Dict[str, Any]:
        """Get Chrome DevTools specific capabilities summary"""
        tools_by_category = {}
        for tool_name, tool in self.available_tools.items():
            category = self._determine_chrome_tool_category(tool_name)
            if category not in tools_by_category:
                tools_by_category[category] = []
            tools_by_category[category].append({
                "name": tool_name,
                "description": tool.get("description", "")
            })
        
        return {
            "client_type": "Chrome DevTools",
            "server_name": self.server_name,
            "total_tools": len(self.available_tools),
            "categories": tools_by_category,
            "high_level_methods": [
                "navigate_and_wait",
                "fill_and_submit_form"
            ]
        }

