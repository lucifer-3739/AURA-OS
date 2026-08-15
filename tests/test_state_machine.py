from agent.core import TaskState

def test_task_states_completeness():
    states = [s.value for s in TaskState]
    expected = [
        "IDLE", "LISTENING", "UNDERSTANDING", "PLANNING", 
        "WAITING_FOR_PERMISSION", "EXECUTING", "OBSERVING", 
        "VERIFYING", "RECOVERING", "COMPLETED", "FAILED", "CANCELLED"
    ]
    for e in expected:
        assert e in states
