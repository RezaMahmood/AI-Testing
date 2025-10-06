import pytest
import asyncio
from agent_assert_mcp import MCPAgentAssert
from assertion_result import AssertionResult


class TestAgentAssert:
    """Test class for AgentAssert functionality"""

    @pytest.mark.asyncio
    async def test_agent_assert_case(self):
        """Test the agent_assert functionality with a sample test case"""

        # Placeholder values for the test case
        test_url = "https://github.com/RezaMahmood/AI-Testing"
        test_message = "Navigate to the file called assertion_result.py."
        expected_result = "Page should load with status 200.  The page should take less than 3 seconds to load"
        # Initialize the MCPAgentAssert instance
        async with MCPAgentAssert() as agent:
            # Execute the test case
            result = await agent.assert_case(
                url=test_url, testmessage=test_message, expectedresult=expected_result
            )

        assert result.TestPassed == True, f"Web test failed: {result.Message}"


if __name__ == "__main__":
    # Allow running the test directly
    asyncio.run(TestAgentAssert().test_agent_assert_case())
