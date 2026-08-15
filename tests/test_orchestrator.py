import pytest
import asyncio
from agent.core import orchestrator, TaskState
from agent.database import db

@pytest.mark.asyncio
async def test_orchestrator_execution_flow():
    await db.initialize()
    
    events = []
    def subscriber(evt):
        events.append(evt["state"])

    orchestrator.subscribe(subscriber)
    
    task_id = await orchestrator.run_command("Get system info.")
    assert task_id is not None
    
    # Wait brief moment for async execution loop
    await asyncio.sleep(1.0)
    
    assert TaskState.UNDERSTANDING.value in events
    assert TaskState.PLANNING.value in events
    assert TaskState.EXECUTING.value in events
    assert TaskState.COMPLETED.value in events or orchestrator.current_state == TaskState.IDLE
