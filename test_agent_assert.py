import pytest
import asyncio
from agent_assert import AgentAssert
from assertion_result import AssertionResult


class TestAgentAssert:
    """Test class for AgentAssert functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_assert_case(self):
        """Test the agent_assert functionality with a sample test case"""
        
        # Initialize the AgentAssert instance
        agent = AgentAssert()
        
        # Placeholder values for the test case
        test_url = "https://developer.chrome.com"
        test_message = "Navigate using the button called 'Explore Now' in the section on 'What''s new in Chrome'"
        expected_result = "Page should load with status 200 and display the main heading"
        
        # Execute the test case
        result = await agent.assert_case(
            url=test_url,
            testmessage=test_message,
            expectedresult=expected_result
        )
        
        # Verify that we get an AssertionResult instance
        assert isinstance(result, AssertionResult), "Result should be an AssertionResult instance"
        
        # Verify that the result has the required properties
        assert hasattr(result, 'TestPassed'), "Result should have TestPassed property"
        assert hasattr(result, 'Message'), "Result should have Message property"
        
        # Verify the types of the properties
        assert isinstance(result.TestPassed, bool), "TestPassed should be a boolean"
        assert isinstance(result.Message, str), "Message should be a string"
        
        # Verify that we got a meaningful message (not empty)
        assert len(result.Message.strip()) > 0, "Message should not be empty"
        
        # Print the result for debugging purposes
        print(f"\nTest Result:")
        print(f"  Test Passed: {result.TestPassed}")
        print(f"  Message: {result.Message}")
        
        # The test passes regardless of the actual assertion result,
        # as we're testing the functionality of the agent_assert method itself
        assert True, "Test completed successfully"


if __name__ == "__main__":
    # Allow running the test directly
    asyncio.run(TestAgentAssert().test_agent_assert_case())