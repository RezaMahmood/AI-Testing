from semantic_kernel import kernel
from assertion_result import AssertionResult

class AgentAssert:
    def __init__(self):
        print("Initialising AgentAssert")

    def assert_case(self, url, test_steps, expected_result):
        return AssertionResult(TestPassed=False, Message="Test failed because LLM said so")