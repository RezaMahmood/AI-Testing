import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from assertion_result import AssertionResult
from mcp_dataclasses import IMCPClient
from mcp_chromedevtools_client import ChromeDevToolsClient

# Load environment variables from .env file
load_dotenv()

class AgentAssert:
    def __init__(self, 
                 api_key: str = None, 
                 mcp_client: Optional[IMCPClient] = None,
                 azure_endpoint: str = None,
                 deployment_name: str = None):
        # Azure OpenAI configuration (required)
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        self.kernel = None
        self.mcp_client = mcp_client  # Accept specific client
        self.available_tools = {}
        
        # Validation
        if not self.api_key:
            raise ValueError("Azure OpenAI API key required")
        
        if not self.azure_endpoint:
            raise ValueError("Azure OpenAI endpoint required")
        
        if not self.deployment_name:
            raise ValueError("Azure OpenAI deployment name required")
    
    async def setup_kernel(self):
        """Initialize SK with Azure OpenAI and MCP client"""
        # Create kernel
        self.kernel = sk.Kernel()
        
        # Add Azure OpenAI service
        service_id = "azure-openai"
        self.kernel.add_service(AzureChatCompletion(
            service_id=service_id,
            api_key=self.api_key,
            endpoint=self.azure_endpoint,
            deployment_name=self.deployment_name,
            api_version="2024-02-01"
        ))
        
        # Use provided client or create default Chrome DevTools client
        if self.mcp_client is None:
            self.mcp_client = ChromeDevToolsClient()
        
        # Initialize client and discover capabilities
        async with self.mcp_client:
            capabilities = await self.mcp_client.discover_capabilities()
            self.available_tools = capabilities.get("tools", {})
            
            # Add tools to kernel
            await self._register_mcp_tools()
    
    async def _register_mcp_tools(self):
        """Register discovered MCP tools with Semantic Kernel"""
        for tool_name, tool_info in self.available_tools.items():
            # Create kernel function for each tool
            kernel_func = self._create_kernel_function(tool_name, tool_info)
            self.kernel.add_function(
                plugin_name=f"{self.mcp_client.server_name}_tools",
                function=kernel_func
            )
    
    def _create_kernel_function(self, tool_name: str, tool_info: Dict[str, Any]):
        """Create SK function from MCP tool definition"""
        async def dynamic_tool_function(**kwargs) -> str:
            try:
                result = await self.mcp_client.call_tool(tool_name, kwargs)
                return f"Tool '{tool_name}' executed: {result}"
            except Exception as e:
                return f"Error executing '{tool_name}': {str(e)}"
        
        # Set metadata
        dynamic_tool_function.__name__ = tool_name
        dynamic_tool_function.__doc__ = tool_info.get("description", "")
        
        return sk.KernelFunction.from_method(
            method=dynamic_tool_function,
            plugin_name=f"{self.mcp_client.server_name}_tools"
        )
    
    def _generate_tools_description(self) -> str:
        """Generate a description of all available tools for AI prompts"""
        if not self.available_tools:
            return "No Chrome DevTools functions available."
        
        descriptions = []
        for tool_name, tool_info in self.available_tools.items():
            desc = tool_info.get("description", "No description")
            
            # Include parameter info
            input_schema = tool_info.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])
            
            param_info = []
            for param_name, param_details in properties.items():
                param_type = param_details.get("type", "string")
                param_desc = param_details.get("description", "")
                is_required = " (required)" if param_name in required else " (optional)"
                param_info.append(f"  - {param_name} ({param_type}){is_required}: {param_desc}")
            
            tool_desc = f"- {tool_name}: {desc}"
            if param_info:
                tool_desc += "\n" + "\n".join(param_info)
            
            descriptions.append(tool_desc)
        
        return "\n\n".join(descriptions)
    
    async def assert_case(self, url: str, test_steps: str, expected_result: str) -> AssertionResult:
        """Execute test case using the configured MCP client"""
        try:
            if not self.kernel:
                await self.setup_kernel()
            
            # Generate client-specific tools description
            tools_description = self._generate_tools_description()
            
            # Create AI prompt with discovered tools
            prompt = f"""
You are an expert web testing agent with access to Chrome DevTools functions through an MCP server.

Available Chrome DevTools Functions:
{tools_description}

Current Test Details:
- URL: {url}
- Test Steps: {test_steps}  
- Expected Result: {expected_result}

Instructions:
1. First, navigate to the specified URL using the appropriate function
2. Take a page snapshot to understand the current state
3. Execute the test steps using the available Chrome DevTools functions
4. Verify the expected result is achieved
5. Take a screenshot as evidence
6. Provide a clear PASS/FAIL result with detailed reasoning

Execute the test systematically and return the final assessment.
"""
            
            # Execute the prompt with auto-discovered functions
            result = await self.kernel.invoke_prompt(
                prompt,
                plugin_name="ChromeDevTools"
            )
            
            # Analyze result for pass/fail
            analysis_prompt = f"""
Based on this test execution result:
{result}

Expected result was: {expected_result}

Determine if the test PASSED or FAILED. Return your decision in this format:
RESULT: [PASSED/FAILED]
REASON: [Brief explanation]
"""
            
            analysis = await self.kernel.invoke_prompt(analysis_prompt)
            analysis_text = str(analysis).strip()
            
            test_passed = "PASSED" in analysis_text.upper()
            
            return AssertionResult(
                TestPassed=test_passed,
                Message=analysis_text
            )
            
        except Exception as ex:
            return AssertionResult(
                TestPassed=False,
                Message=f"Test execution failed: {str(ex)}"
            )