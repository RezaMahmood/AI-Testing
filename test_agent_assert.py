import csv

import pytest

from agent_assert_mcp import MCPAgentAssert


@pytest.mark.asyncio
async def test_single_case():
    """Test with a single hardcoded test case"""

    # TODO: Replace these placeholders with actual test values
    url = "https://developer.chrome.com/"
    testmessage = "I want to find out what's new in Chrome.  navigate to Explore now."
    expectedresult = "There should be at least 6 documentation updates."

    async with MCPAgentAssert() as agent:
        result = await agent.assert_case(url, testmessage, expectedresult)

    assert result.TestPassed, f"Test failed: {result.Message}"


@pytest.mark.asyncio
async def test_csv_cases():
    """Test all cases from manual_tests.csv file"""

    async with MCPAgentAssert() as agent:
        with open('manual_tests.csv', 'r', newline='',
                  encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row_num, row in enumerate(reader, start=1):
                url = row['url']
                testmessage = row['test_instructions']
                expectedresult = row['expected_result']

                print(f"Running test {row_num}: {testmessage[:50]}...")

                result = await agent.assert_case(url, testmessage,
                                                 expectedresult)

                assert result.TestPassed, (f"Test {row_num} failed: "
                                           f"{result.Message}")
