import sys
import asyncio
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from tests.test_tools import test_tool_registration, test_create_and_read_file
from tests.test_permissions import test_permission_risk_levels
from tests.test_planner import test_mock_planner_open_vscode, test_mock_planner_create_folder
from tests.test_orchestrator import test_orchestrator_execution_flow
from tests.test_state_machine import test_task_states_completeness
from tests.test_voice_interfaces import (
    test_wake_word_provider_interface,
    test_stt_provider_interface,
    test_tts_provider_interface,
    test_device_manager,
)
from tests.test_voice_pipeline import test_audio_capture_and_mute, test_playback_interruption, test_voice_session_context
from tests.test_voice_interruption import test_fast_path_stop_talking, test_fast_path_cancel_task, test_voice_permission_confirmation
from tests.test_voice_integration import test_end_to_end_voice_command_flow
from tests.test_browser_driver import test_browser_driver_navigation, test_browser_driver_dom_parsing, test_browser_driver_click_and_type
from tests.test_browser_tools import test_browser_registered_tools, test_browser_tool_executions
from tests.test_browser_integration import test_end_to_end_browser_automation_flow

async def run_all_tests():
    print("==================================================")
    print("        AURA OS SYSTEM TEST SUITE (PHASE 3)       ")
    print("==================================================")

    # 1. State machine & Permissions
    test_task_states_completeness()
    test_permission_risk_levels()
    print("[PASS] State machine & permission evaluation tests passed.")

    # 2. Planner & System Tools
    await test_mock_planner_open_vscode()
    await test_mock_planner_create_folder()
    await test_tool_registration()
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        await test_create_and_read_file(Path(tmpdir))
    print("[PASS] AI planner & filesystem tools tests passed.")

    # 3. Orchestrator
    await test_orchestrator_execution_flow()
    print("[PASS] Orchestrator async execution loop test passed.")

    # 4. Voice Interfaces & Device Manager (Phase 2)
    await test_wake_word_provider_interface()
    await test_stt_provider_interface()
    await test_tts_provider_interface()
    test_device_manager()
    await test_audio_capture_and_mute()
    await test_playback_interruption()
    test_voice_session_context()
    await test_fast_path_stop_talking()
    await test_fast_path_cancel_task()
    await test_voice_permission_confirmation()
    await test_end_to_end_voice_command_flow()
    print("[PASS] Voice pipeline, speech interruption & voice permission tests passed.")

    # 5. Browser Automation Tools & Drivers (Phase 3)
    await test_browser_driver_navigation()
    await test_browser_driver_dom_parsing()
    await test_browser_driver_click_and_type()
    await test_browser_registered_tools()
    with tempfile.TemporaryDirectory() as tmpdir:
        await test_browser_tool_executions(Path(tmpdir))
    await test_end_to_end_browser_automation_flow()
    print("[PASS] Browser drivers, DOM parsing, browser tools & E2E browser automation tests passed.")

    print("\n--------------------------------------------------")
    print(" ALL 24 TEST SUITES PASSED SUCCESSFULLY! ")
    print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
