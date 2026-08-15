import pytest
import os
from pathlib import Path
from agent.tools import registry, filesystem

@pytest.mark.asyncio
async def test_tool_registration():
    tools = registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "create_file" in tool_names
    assert "read_file" in tool_names
    assert "open_application" in tool_names
    assert "system_information" in tool_names

@pytest.mark.asyncio
async def test_create_and_read_file(tmp_path):
    test_file = tmp_path / "test_aura.txt"
    
    # 1. Create file
    create_tool = registry.get_tool("create_file")
    res_create = await create_tool.execute(path=str(test_file), content="Hello AURA OS")
    assert res_create["success"] is True
    assert test_file.exists()
    
    # Verify method
    verified = await create_tool.verify(res_create, path=str(test_file))
    assert verified is True

    # 2. Read file
    read_tool = registry.get_tool("read_file")
    res_read = await read_tool.execute(path=str(test_file))
    assert res_read["success"] is True
    assert res_read["content"] == "Hello AURA OS"
