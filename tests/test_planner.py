import pytest
from agent.core.planner import MockAIProvider

@pytest.mark.asyncio
async def test_mock_planner_open_vscode():
    planner = MockAIProvider()
    plan = await planner.generate_plan("Open VS Code.", {})
    assert len(plan) == 1
    assert plan[0]["tool_name"] == "open_application"
    assert plan[0]["arguments"]["application"] == "code"

@pytest.mark.asyncio
async def test_mock_planner_create_folder():
    planner = MockAIProvider()
    plan = await planner.generate_plan("Create a folder called Projects", {})
    assert len(plan) == 1
    assert plan[0]["tool_name"] == "create_folder"
    assert plan[0]["arguments"]["path"] == "Projects"
