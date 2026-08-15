import pytest
import asyncio
from agent.voice.pipeline import voice_pipeline
from agent.voice.audio import playback_controller
from agent.core import orchestrator, TaskState
from agent.database import db

@pytest.mark.asyncio
async def test_fast_path_stop_talking():
    playback_controller.is_speaking = True
    handled = await voice_pipeline._handle_fast_path_command("stop talking")
    assert handled is True
    assert playback_controller.is_speaking is False

@pytest.mark.asyncio
async def test_fast_path_cancel_task():
    await db.initialize()
    orchestrator.current_task_id = "test-cancel-id"
    handled = await voice_pipeline._handle_fast_path_command("cancel task")
    assert handled is True
    assert orchestrator.current_state == TaskState.CANCELLED or orchestrator.current_state == TaskState.IDLE

@pytest.mark.asyncio
async def test_voice_permission_confirmation():
    await db.initialize()
    orchestrator.current_state = TaskState.WAITING_FOR_PERMISSION
    orchestrator.pending_step = {"tool_name": "delete_file", "arguments": {"path": "Projects_Test"}}
    
    handled = await voice_pipeline._handle_fast_path_command("yes")
    assert handled is True
