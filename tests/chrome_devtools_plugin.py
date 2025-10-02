import semantic_kernel as sk
from semantic_kernel.functions import KernelFunction
from typing import Any, Dict, List, Callable
import inspect

class DynamicChromeDevToolsPlugin:
    def __init__(self, mcp_client: ChromeDevToolsMCPClient):
        self.mcp_client = mcp_client
        self.kernel_functions = {}
    
    async def initialize_and_discover(self):
        """Initialize the client and discover all available tools"""
        await self.mcp_client.discover_tools()
        self._generate_kernel_functions()
    
    def _generate_kernel_functions(self):
        """Generate Semantic Kernel functions from discovered MCP tools"""
        for tool_name, tool_info in self.mcp_client.available_tools.items():
            # Create a dynamic function for each tool
            kernel_func = self._create_kernel_function(tool_name, tool_info)
            self.kernel_functions[tool_name] = kernel_func
    
    def _create_kernel_function(self, tool_name: str, tool_info: Dict[str, Any]) -> KernelFunction:
        """Create a Semantic Kernel function from MCP tool info"""
        
        # Extract tool metadata
        description = tool_info.get("description", f"Execute {tool_name}")
        input_schema = tool_info.get("inputSchema", {})
        properties = input_schema.get("properties", {})
        required = input_schema.get("required", [])
        
        # Create the async function dynamically
        async def dynamic_tool_function(**kwargs) -> str:
            try:
                # Validate required parameters
                for req_param in required:
                    if req_param not in kwargs:
                        return f"Error: Required parameter '{req_param}' missing"
                
                # Call the MCP tool
                result = await self.mcp_client.call_tool(tool_name, kwargs)
                
                # Return formatted result
                if isinstance(result, dict):
                    return f"Tool '{tool_name}' executed successfully: {result}"
                else:
                    return str(result)
                    
            except Exception as e:
                return f"Error executing '{tool_name}': {str(e)}"
        
        # Set function metadata for Semantic Kernel
        dynamic_tool_function.__name__ = tool_name
        dynamic_tool_function.__doc__ = description
        
        # Add parameter annotations dynamically
        annotations = {}
        for param_name, param_info in properties.items():
            param_type = self._map_json_type_to_python(param_info.get("type", "string"))
            param_desc = param_info.get("description", f"Parameter {param_name}")
            annotations[param_name] = param_type
        
        dynamic_tool_function.__annotations__ = annotations
        
        # Create and return KernelFunction
        return KernelFunction.from_method(
            method=dynamic_tool_function,
            plugin_name="ChromeDevTools"
        )
    
    def _map_json_type_to_python(self, json_type: str) -> type:
        """Map JSON schema types to Python types"""
        type_mapping = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        return type_mapping.get(json_type, str)
    
    def get_all_functions(self) -> Dict[str, KernelFunction]:
        """Get all dynamically generated kernel functions"""
        return self.kernel_functions