"""
Simple test framework for basic string validation.
This test checks if a given string matches "Hello World".
"""

import pytest
from agent_assert import AgentAssert
from assertion_result import AssertionResult



@pytest.fixture
def agent_assertion():
    """Fixture that provides an instance of AgentAssert."""
    return AgentAssert()

@pytest.mark.asyncio
async def test_single_test_case(agent_assertion):
    """Test that verifies a string matches 'Hello World'."""
    result = await agent_assertion.assert_case("http://developer.chrome.com", "load the page and navigate to the announcement regarding Builtin AI Challenge 2025.  ","Verify that the page loads in less than 1 second")

    assert result.TestPassed == True, result.Message