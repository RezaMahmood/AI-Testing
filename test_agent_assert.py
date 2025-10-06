import pytest
import asyncio
import csv
from dataclasses import dataclass
from typing import List
from agent_assert_mcp import MCPAgentAssert
from assertion_result import AssertionResult


@dataclass
class TestCase:
    """Dataclass to represent a test case"""
    url: str
    instructions: str
    expected_result: str


class TestAgentAssert:
    """Test class for AgentAssert functionality"""

    async def run_test_case(self, agent: MCPAgentAssert, test_case: TestCase) -> AssertionResult:
        """
        Execute a single test case using the provided agent
        
        Args:
            agent: The MCPAgentAssert instance to use for testing
            test_case: The TestCase dataclass containing test parameters
            
        Returns:
            AssertionResult: The result of the test execution
        """
        return await agent.assert_case(
            url=test_case.url,
            testmessage=test_case.instructions,
            expectedresult=test_case.expected_result
        )

    async def test_single_case(self, agent: MCPAgentAssert, test_case: TestCase) -> AssertionResult:
        """
        Test the agent_assert functionality with a single test case
        
        Args:
            agent: The MCPAgentAssert instance to use for testing
            test_case: The TestCase dataclass containing test parameters
            
        Returns:
            AssertionResult: The result of the test execution
        """
        return await self.run_test_case(agent, test_case)

    @pytest.mark.asyncio
    async def test_default_single_case(self):
        """Test with a default single test case - for pytest discovery"""
        
        test_case = TestCase(
            url="https://github.com/RezaMahmood/AI-Testing",
            instructions="Navigate to the file called assertion_result.py.",
            expected_result="Page should load with status 200. The page should take less than 3 seconds to load"
        )
        
        async with MCPAgentAssert() as agent:
            result = await self.test_single_case(agent, test_case)
        
        assert result.TestPassed == True, f"Web test failed: {result.Message}"

    def parse_csv_file(self, csv_file_path: str) -> List[TestCase]:
        """
        Parse a CSV file and return a list of TestCase objects
        
        Args:
            csv_file_path: Path to the CSV file containing test cases
            
        Returns:
            List[TestCase]: List of parsed test cases
        """
        test_cases = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    test_case = TestCase(
                        url=row['url'].strip(),
                        instructions=row['test_instructions'].strip(),
                        expected_result=row['expected_result'].strip()
                    )
                    test_cases.append(test_case)
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{csv_file_path}' not found. Please ensure the file exists in the current directory.")
        except KeyError as e:
            raise ValueError(f"Missing required column in CSV file: {e}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
        
        return test_cases

    @pytest.mark.asyncio
    async def test_csv_file_cases(self, csv_file_path: str = "manual_tests.csv"):
        """
        Test all cases from a CSV file by calling test_single_case for each
        
        Args:
            csv_file_path: Path to the CSV file containing test cases (defaults to manual_tests.csv)
        """
        
        # Parse test cases from CSV file
        test_cases = self.parse_csv_file(csv_file_path)
        
        failed_tests = []
        passed_tests = []
        
        async with MCPAgentAssert() as agent:
            for test_num, test_case in enumerate(test_cases, start=1):
                print(f"\n🧪 Running test {test_num}: {test_case.instructions[:50]}...")
                
                try:
                    # Use test_single_case for each test case
                    result = await self.test_single_case(agent, test_case)
                    
                    if result.TestPassed:
                        passed_tests.append({
                            'test_num': test_num,
                            'test_case': test_case,
                            'message': result.Message
                        })
                        print(f"✅ Test {test_num} PASSED")
                    else:
                        failed_tests.append({
                            'test_num': test_num,
                            'test_case': test_case,
                            'message': result.Message
                        })
                        print(f"❌ Test {test_num} FAILED: {result.Message[:100]}...")
                        
                except Exception as e:
                    failed_tests.append({
                        'test_num': test_num,
                        'test_case': test_case,
                        'message': f"Exception occurred: {str(e)}"
                    })
                    print(f"💥 Test {test_num} ERROR: {str(e)[:100]}...")
        
        # Print summary
        total_tests = len(passed_tests) + len(failed_tests)
        print(f"\n📊 TEST SUMMARY:")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  Test {test['test_num']}: {test['test_case'].instructions[:50]}...")
                print(f"    URL: {test['test_case'].url}")
                print(f"    Reason: {test['message'][:150]}...")
                print()
        
        # Assert that all tests passed
        if failed_tests:
            failure_summary = f"{len(failed_tests)}/{total_tests} tests failed. See details above."
            pytest.fail(failure_summary)


if __name__ == "__main__":
    # Allow running the test directly
    asyncio.run(TestAgentAssert().test_default_single_case())
