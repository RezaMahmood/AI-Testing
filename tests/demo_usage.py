async def demonstrate_auto_discovery():
    """Demonstrate the auto-discovery capabilities"""
    
    # Initialize MCP client
    mcp_client = ChromeDevToolsMCPClient()
    
    try:
        await mcp_client.__aenter__()
        
        # Discover and inspect capabilities
        inspector = MCPToolInspector(mcp_client)
        await inspector.print_capabilities_report()
        
        # Initialize agent with auto-discovery
        api_key = os.getenv("OPENAI_API_KEY")
        agent = EnhancedAgentAssert(api_key)
        await agent.setup_kernel()
        
        print(f"\nDiscovered {len(agent.available_tools)} Chrome DevTools functions")
        print("Available functions:", list(agent.available_tools.keys()))
        
        # Run test with auto-discovered functions
        result = await agent.assert_case(
            url="http://localhost:5125",
            test_steps="Navigate to home page and verify the welcome message",
            expected_result="Home page should display welcome content"
        )
        
        print(f"\nTest Result: {result.TestPassed}")
        print(f"Message: {result.Message}")
        
    finally:
        await mcp_client.__aexit__(None, None, None)

# Run the demonstration
if __name__ == "__main__":
    asyncio.run(demonstrate_auto_discovery())