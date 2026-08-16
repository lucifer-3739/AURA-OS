import pytest
import os
from pathlib import Path
from agent.tools import registry, filesystem, computer, system

@pytest.mark.asyncio
async def test_tool_registration():
    tools = registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "create_file" in tool_names
    assert "read_file" in tool_names
    assert "open_application" in tool_names
    assert "system_information" in tool_names
    assert "organize_folder" in tool_names
    assert "capture_camera" in tool_names

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

@pytest.mark.asyncio
async def test_organize_folder(tmp_path):
    img_file = tmp_path / "photo.png"
    doc_file = tmp_path / "report.pdf"
    img_file.write_text("dummy image data")
    doc_file.write_text("dummy pdf data")

    organize_tool = registry.get_tool("organize_folder")
    res = await organize_tool.execute(folder_path=str(tmp_path))
    assert res["success"] is True
    assert (tmp_path / "Images" / "photo.png").exists()
    assert (tmp_path / "Documents" / "report.pdf").exists()

@pytest.mark.asyncio
async def test_capture_camera(tmp_path):
    cam_file = tmp_path / "camera_test.jpg"
    cam_tool = registry.get_tool("capture_camera")
    res = await cam_tool.execute(camera_index=0, save_path=str(cam_file))
    assert res["success"] is True
    assert cam_file.exists()
