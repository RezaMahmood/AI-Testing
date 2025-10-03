from dataclasses import dataclass

@dataclass
class AssertionResult:
    TestPassed: bool
    Message: str