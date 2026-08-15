import pytest
from agent.tools import registry, browser

@pytest.mark.asyncio
async def test_browser_registered_tools():
    tools = registry.list_tools()
    tool_names = [t["name"] for t in tools]
    
    assert "open_url" in tool_names
    assert "search_web" in tool_names
    assert "click_element" in tool_names
    assert "type_text" in tool_names
    assert "read_page" in tool_names
    assert "extract_data" in tool_names
    assert "download_file" in tool_names
    assert "close_browser" in tool_names

@pytest.mark.asyncio
async def test_browser_tool_executions(tmp_path):
    open_tool = registry.get_tool("open_url")
    res_open = await open_tool.execute(url="https://react.dev")
    assert res_open["success"] is True

    read_tool = registry.get_tool("read_page")
    res_read = await read_tool.execute(max_length=1000)
    assert res_read["success"] is True

    dl_target = tmp_path / "react_docs.pdf"
    dl_tool = registry.get_tool("download_file")
    res_dl = await dl_tool.execute(url="https://example.com/docs.pdf", destination=str(dl_target))
    assert res_dl["success"] is True
    assert dl_target.exists()
