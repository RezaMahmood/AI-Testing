
from assertion_result import AssertionResult

class AgentAssert:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.kernel = None
        self.chrome_plugin = None
        self.mcp_client = None
        self.available_tools = {}
    
    async def setup_kernel(self):
        """Initialize the Semantic Kernel with auto-discovered Chrome DevTools functions"""
        # Create kernel
        self.kernel = sk.Kernel()
        
        # Add OpenAI chat completion service
        service_id = "chat-gpt"
        self.kernel.add_service(OpenAIChatCompletion(
            service_id=service_id,
            api_key=self.api_key,
            ai_model_id=self.model
        ))
        
        # Setup Chrome DevTools MCP client
        self.mcp_client = ChromeDevToolsMCPClient()
        await self.mcp_client.__aenter__()
        
        # Create dynamic plugin with auto-discovery
        self.chrome_plugin = DynamicChromeDevToolsPlugin(self.mcp_client)
        await self.chrome_plugin.initialize_and_discover()
        
        # Add all discovered functions to the kernel
        for func_name, kernel_func in self.chrome_plugin.get_all_functions().items():
            self.kernel.add_function(
                plugin_name="ChromeDevTools",
                function=kernel_func
            )
        
        # Store available tools for prompt generation
        self.available_tools = self.mcp_client.available_tools
    
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
        """Execute test case using auto-discovered Chrome DevTools functions"""
        try:
            if not self.kernel:
                await self.setup_kernel()
            
            # Generate dynamic tools description
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