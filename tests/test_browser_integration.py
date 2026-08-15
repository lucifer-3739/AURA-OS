import pytest
import asyncio
from agent.database import db
from agent.core import orchestrator, TaskState
from agent.browser import browser_driver

@pytest.mark.asyncio
async def test_end_to_end_browser_automation_flow():
    # 1. Initialize Database
    await db.initialize()

    # 2. Dispatch Multi-Step Browser Automation Command
    task_id = await orchestrator.run_command("Search web for React documentation.")
    assert task_id is not None

    await asyncio.sleep(0.8)

    # 3. Verify Active Browser State
    content = await browser_driver.get_page_content()
    assert content["url"] != "about:blank" or "google" in content["url"] or "react" in content["url"]

    # 4. Execute Click Element
    click_res = await browser_driver.click(text="Installation")
    assert click_res["success"] is True

    # 5. Read Page Text Content
    read_res = await browser_driver.get_page_content(max_length=500)
    assert read_res["url"] is not None
