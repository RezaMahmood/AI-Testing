import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import os
from dotenv import load_dotenv
from mcp_chromedevtools_client import ChromeDevToolsClient
from assertion_result import AssertionResult

# Load environment variables from .env file
load_dotenv()

class AgentAssert:
    def __init__(self):
        # Azure OpenAI configuration from environment
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Validation
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable required")
        if not self.azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable required")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME environment variable required")
            
        self.kernel = None
        self.mcp_client = None
    
    async def _setup_kernel(self):
        """Initialize Semantic Kernel with Azure OpenAI and Chrome DevTools MCP client"""
        print("🔧 Setting up Semantic Kernel with Azure OpenAI and Chrome DevTools...")
        
        # Create kernel
        self.kernel = sk.Kernel()
        
        # Add Azure OpenAI service
        self.kernel.add_service(AzureChatCompletion(
            service_id="azure-openai",
            api_key=self.api_key,
            endpoint=self.azure_endpoint,
            deployment_name=self.deployment_name,
            api_version="2024-02-01"
        ))
        
        # Initialize Chrome DevTools MCP client
        self.mcp_client = ChromeDevToolsClient()
        await self.mcp_client.start_server()
        await self.mcp_client.initialize_mcp_connection()
        await self.mcp_client.discover_capabilities()
        
        # Register MCP tools as Semantic Kernel functions
        await self._register_mcp_tools()
        
        print("✅ Semantic Kernel setup complete")
    
    async def _register_mcp_tools(self):
        """Register discovered MCP tools as Semantic Kernel functions"""
        if not self.mcp_client or not self.mcp_client.available_tools:
            print("⚠️ No MCP tools available to register")
            return
            
        print(f"🔧 Registering {len(self.mcp_client.available_tools)} MCP tools as Semantic Kernel functions...")
        
        for tool_name, tool_info in self.mcp_client.available_tools.items():
            # Create a wrapper function for each MCP tool
            def create_tool_function(name, info):
                async def tool_function(**kwargs) -> str:
                    try:
                        result = await self.mcp_client.call_tool(name, kwargs)
                        return str(result)
                    except Exception as e:
                        return f"Error executing {name}: {str(e)}"
                
                # Set function metadata
                tool_function.__name__ = name.replace("-", "_")  # SK function names can't have hyphens
                tool_function.__doc__ = info.get("description", f"MCP tool: {name}")
                return tool_function
            
            # Create and register the function
            sk_function = sk.KernelFunction.from_method(
                method=create_tool_function(tool_name, tool_info),
                plugin_name="chrome_devtools"
            )
            
            # Add function to kernel
            self.kernel.add_function(
                plugin_name="chrome_devtools",
                function=sk_function
            )
        
        print(f"✅ Registered {len(self.mcp_client.available_tools)} Chrome DevTools functions")
    
    async def assert_case(self, url: str, testmessage: str, expectedresult: str) -> AssertionResult:
        """Execute test case using Chrome DevTools and AI reasoning"""
        try:
            # Setup kernel if not already done
            if not self.kernel:
                await self._setup_kernel()
            
            # Create a prompt that includes information about available tools
            available_tools = list(self.mcp_client.available_tools.keys()) if self.mcp_client else []
            tools_info = "\n".join([f"- {tool}" for tool in available_tools[:10]])  # Show first 10 tools
            
            prompt = f"""
You are a web testing agent with access to Chrome DevTools functions.

Available Chrome DevTools functions:
{tools_info}
{'...' if len(available_tools) > 10 else ''}

You need to test the following:
URL: {url}
Test Message: {testmessage}
Expected Result: {expectedresult}

Instructions:
1. Use the available Chrome DevTools functions to navigate to the URL and perform the test
3. Compare the actual results with the expected results
5. If the test fails, provide:
   - Clear explanation of what was found vs what was expected
   - Specific reasons why the test failed
   - Actionable suggestions for fixing the issue

Format your response as:
ACTUAL RESULT: [What you actually found]
ANALYSIS: [Detailed comparison with expected result]
REASON FOR FAILURE: [If failed, specific reasons why]
SUGGESTIONS: [If failed, specific suggestions to fix the issue]
CONCLUSION: TEST PASSED or TEST FAILED

IMPORTANT: Always end with "TEST PASSED" or "TEST FAILED" so I can determine the result.
"""
            
            # Execute the prompt
            result = await self.kernel.invoke_prompt(prompt)
            result_text = str(result)
            
            # Analyze the result to determine if test passed or failed
            test_passed = "TEST PASSED" in result_text.upper()
            
            return AssertionResult(
                TestPassed=test_passed,
                Message=result_text
            )
            
        except Exception as ex:
            return AssertionResult(
                TestPassed=False,
                Message=f"Error in assert_case: {str(ex)}"
            )
        finally:
            # Cleanup MCP client
            if self.mcp_client:
                await self.mcp_client.cleanup()
                self.mcp_client = None
