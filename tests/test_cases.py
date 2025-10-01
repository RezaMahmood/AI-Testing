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

def test_single_test_case(agent_assertion):
    """Test that verifies a string matches 'Hello World'."""
    test = agent_assertion.assert_case("http://localhost:1234", "these are my steps","this is what i expect")

    assert result.TestPassed == True, result.Message