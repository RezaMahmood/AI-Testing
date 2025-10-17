
import logging
import os
from pathlib import Path
from string import Template

import semantic_kernel as sk
from azure.monitor.opentelemetry.exporter import (AzureMonitorLogExporter,
                                                  AzureMonitorMetricExporter,
                                                  AzureMonitorTraceExporter)
from dotenv import load_dotenv
from opentelemetry._logs import set_logger_provider
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (BatchLogRecordProcessor,
                                            ConsoleLogExporter)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (ConsoleMetricExporter,
                                              PeriodicExportingMetricReader)
from opentelemetry.sdk.metrics.view import DropAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import set_tracer_provider
from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion, OpenAIPromptExecutionSettings)
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import \
    AzureChatPromptExecutionSettings
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.functions import KernelArguments

from assertion_result import AssertionResult

# Load environment variables from .env file
load_dotenv()

# Replace the connection string with your Application Insights connection string
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if not connection_string:
    raise ValueError(
        "APPLICATIONINSIGHTS_CONNECTION_STRING environment variable required")

# Create a resource to represent the service/sample
resource = Resource.create(
    {ResourceAttributes.SERVICE_NAME: "telemetry-application-insights-quickstart"})


def set_up_logging():
    exporter = AzureMonitorLogExporter(connection_string=connection_string)

    # Create and set a global logger provider for the application.
    logger_provider = LoggerProvider(resource=resource)
    # Log processors are initialized with an exporter which is responsible
    # for sending the telemetry data to a particular backend.
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    # Sets the global default logger provider
    set_logger_provider(logger_provider)

    # Create a logging handler to write logging records, in OTLP format, to the exporter.
    handler = LoggingHandler()
    # Add filters to the handler to only process records from semantic_kernel.
    handler.addFilter(logging.Filter("semantic_kernel"))
    # Attach the handler to the root logger. `getLogger()` with no arguments returns the root logger.
    # Events from all child loggers will be processed by this handler.
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def set_up_tracing():
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)

    # Initialize a trace provider for the application. This is a factory for creating tracers.
    tracer_provider = TracerProvider(resource=resource)
    # Span processors are initialized with an exporter which is responsible
    # for sending the telemetry data to a particular backend.
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    # Sets the global default tracer provider
    set_tracer_provider(tracer_provider)


def set_up_metrics():
    exporter = AzureMonitorMetricExporter(connection_string=connection_string)

    # Initialize a metric provider for the application. This is a factory for creating meters.
    meter_provider = MeterProvider(
        metric_readers=[PeriodicExportingMetricReader(
            exporter, export_interval_millis=5000)],
        resource=resource,
        views=[
            # Dropping all instrument names except for those starting with "semantic_kernel"
            View(instrument_name="*", aggregation=DropAggregation()),
            View(instrument_name="semantic_kernel*"),
        ],
    )
    # Sets the global default meter provider
    set_meter_provider(meter_provider)


# This must be done before any other telemetry calls
set_up_logging()
set_up_tracing()
set_up_metrics()


def load_prompt_template(template_name: str) -> Template:
    """Load a prompt template from file"""
    template_path = Path("prompts") / f"{template_name}.txt"
    with open(template_path, 'r', encoding='utf-8') as f:
        return Template(f.read())


class MCPAgentAssert:
    def __init__(self):
        # Azure OpenAI configuration from environment
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

        # Validation
        if not self.api_key:
            raise ValueError(
                "AZURE_OPENAI_API_KEY environment variable required")
        if not self.azure_endpoint:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT environment variable required")
        if not self.deployment_name:
            raise ValueError(
                "AZURE_OPENAI_DEPLOYMENT_NAME environment variable required")

        self.kernel = None
        self.chrome_plugin = None

    async def __aenter__(self):
        """Async context manager entry - establish MCP connection"""
        print("🔧 Establishing MCP connection...")

        # Create and enter the MCP plugin context
        self.chrome_plugin = MCPStdioPlugin(
            name="chrome_devtools",
            description="Plugin to interact with Chrome DevTools via MCP",
            command="npx",
            args=["chrome-devtools-mcp@latest", "--isolated",
                  "true", "--headless", "true", "-y"]
        )

        try:
            await self.chrome_plugin.__aenter__()
            print("✅ MCP connection established")

            # Setup kernel with the active plugin
            await self._setup_kernel()
            return self
        except Exception as e:
            print(f"❌ Failed to establish MCP connection: {e}")
            # Cleanup on failure
            if self.chrome_plugin:
                try:
                    await self.chrome_plugin.__aexit__(type(e), e, e.__traceback__)
                except:
                    pass
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup MCP connection"""
        print("🧹 Cleaning up MCP connection...")
        if self.chrome_plugin:
            try:
                await self.chrome_plugin.__aexit__(exc_type, exc_val, exc_tb)
                print("✅ MCP connection cleaned up")
            except Exception as e:
                print(f"⚠️ Warning during MCP cleanup: {e}")
            finally:
                self.chrome_plugin = None
        self.kernel = None

    async def _setup_kernel(self):
        """Setup kernel with already-established MCP plugin"""
        print("🔧 Setting up Semantic Kernel with Azure OpenAI...")

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

        # Add the already-established MCP plugin
        if self.chrome_plugin:
            self.kernel.add_plugin(self.chrome_plugin)
            print("✅ Chrome DevTools plugin added to kernel")

            # NEW: Verify plugin functions are available
            await self._verify_plugin_functions()
        else:
            print("⚠️ Warning: No Chrome DevTools plugin available")

        print("✅ Semantic Kernel setup complete")

    async def _verify_plugin_functions(self):
        """Verify that MCP plugin functions are actually available"""
        print("🔍 Verifying MCP plugin functions...")

        try:
            # Check available plugins
            available_plugins = self.kernel.plugins
            print(f"📋 Total plugins loaded: {len(available_plugins)}")

            chrome_plugin = None
            for plugin_name, plugin in available_plugins.items():
                print(f"🔌 Plugin: {plugin_name}")
                if "chrome" in plugin_name.lower() or "devtools" in plugin_name.lower():
                    chrome_plugin = plugin

                # List all functions in this plugin
                if hasattr(plugin, 'functions') and plugin.functions:
                    print(
                        f"  📚 Functions available ({len(plugin.functions)}):")
                    for func_name in plugin.functions.keys():
                        print(f"    - {func_name}")
                else:
                    print(f"  ⚠️ No functions found in plugin")

            if chrome_plugin and hasattr(chrome_plugin, 'functions') and chrome_plugin.functions:
                print(
                    f"✅ Chrome DevTools plugin verified with {len(chrome_plugin.functions)} functions")
                return True
            else:
                print("❌ Chrome DevTools plugin has no available functions")
                return False

        except Exception as e:
            print(f"❌ Error verifying plugin functions: {e}")
            return False

    async def _test_mcp_connection(self):
        """Test that MCP connection is working by attempting a simple function call"""
        print("🧪 Testing MCP connection...")

        try:
            # Try to get available plugins and their functions
            available_plugins = self.kernel.plugins

            # Look for any Chrome DevTools functions to test
            for plugin_name, plugin in available_plugins.items():
                if hasattr(plugin, 'functions') and plugin.functions:
                    # Try to find a simple function to test (like getting version or status)
                    test_functions = ['version', 'status', 'ping', 'info']

                    for func_name in plugin.functions.keys():
                        if any(test in func_name.lower() for test in test_functions):
                            print(
                                f"🔄 Testing function: {plugin_name}.{func_name}")
                            try:
                                # Attempt to call the function
                                result = await self.kernel.invoke_function(plugin_name, func_name)
                                print(
                                    f"✅ MCP connection test successful: {func_name}")
                                return True
                            except Exception as func_error:
                                print(
                                    f"⚠️ Function {func_name} test failed: {func_error}")
                                continue

            print("⚠️ No testable functions found, but plugin is loaded")
            return True

        except Exception as e:
            print(f"❌ MCP connection test failed: {e}")
            raise RuntimeError(f"MCP connection not working: {e}")

    async def assert_case(self, url: str, testmessage: str, expectedresult: str) -> AssertionResult:
        """Execute test case using Chrome DevTools and AI reasoning"""
        try:
            # Verify kernel is setup (should be done in __aenter__)
            if not self.kernel:
                raise RuntimeError(
                    "Kernel not initialized. Use 'async with MCPAgentAssert() as agent:' pattern.")

            if not self.chrome_plugin:
                raise RuntimeError(
                    "Chrome DevTools plugin not available. Use 'async with MCPAgentAssert() as agent:' pattern.")

            # NEW: Test MCP connection before proceeding
            await self._test_mcp_connection()

            # Load prompt template and substitute variables
            prompt_template = load_prompt_template('web_testing_assistant')

            # Explicitly convert all parameters to strings and validate
            safe_url = str(url) if url is not None else ""
            safe_testmessage = str(
                testmessage) if testmessage is not None else ""
            safe_expectedresult = str(
                expectedresult) if expectedresult is not None else ""

            prompt = prompt_template.substitute(
                url=safe_url,
                testmessage=safe_testmessage,
                expectedresult=safe_expectedresult
            )

            # Execute the prompt using the persistent kernel with MCP plugin
            exec_settings = AzureChatPromptExecutionSettings(
                temperature=0.0,
                top_p=0.0,
                max_tokens=1000,
                frequency_penalty=0.0,
                presence_penalty=0.0,
                seed=12345,
                service_id="azure-openai"
            )
            arguments = KernelArguments(settings=exec_settings)

            result = await self.kernel.invoke_prompt(
                prompt, arguments=arguments)
            # result = await self.kernel.invoke_prompt(prompt)
            result_text = str(result)

            # Analyze the result to determine if test passed or failed
            test_passed = "TEST PASSED" in result_text.upper()

            return AssertionResult(
                TestPassed=test_passed,
                Message=result_text
            )

        except Exception as ex:
            print(
                f"🚨 Exception in assert_case: {type(ex).__name__}: {str(ex)}")

            # Additional debugging for function-related errors
            if "invoking function" in str(ex):
                print(
                    "🔍 Function invocation error detected. Checking available functions...")
                try:
                    available_plugins = self.kernel.plugins
                    for plugin_name, plugin in available_plugins.items():
                        print(f"Debug Plugin: {plugin_name}")
                        if hasattr(plugin, 'functions') and plugin.functions:
                            for func_name, func in plugin.functions.items():
                                print(
                                    f"  Debug Function: {func_name} -> {func}")
                except Exception as debug_ex:
                    print(f"  Debug error: {debug_ex}")

            return AssertionResult(
                TestPassed=False,
                Message=f"Error in assert_case: {str(ex)}"
            )
        # Note: No finally block needed - cleanup handled by __aexit__
