import pytest
import asyncio
from agent.database import db
from agent.core import orchestrator, TaskState
from agent.voice.wake_word import MockWakeWordProvider
from agent.voice.speech_to_text import MockSTTProvider
from agent.voice.text_to_speech import MockTTSProvider
from agent.voice.pipeline.state import voice_session

@pytest.mark.asyncio
async def test_end_to_end_voice_command_flow():
    # 1. Initialize Database & Voice Mocks
    await db.initialize()
    
    wake_word = MockWakeWordProvider()
    stt = MockSTTProvider("Open Visual Studio Code.")
    tts = MockTTSProvider()

    # 2. Simulate Wake Word Detection
    detected = await wake_word.listen_for_wakeword("Aura")
    assert detected is True

    # 3. Simulate STT Audio Recognition
    transcript = await stt.transcribe(b"SIMULATED_PCM_AUDIO")
    assert transcript == "Open Visual Studio Code."

    # 4. Generate Voice Command Payload
    cmd_payload = voice_session.new_command(transcript, source="voice")
    assert cmd_payload["source"] == "voice"

    # 5. Dispatch Command to Existing Orchestrator
    task_id = await orchestrator.run_command(cmd_payload["transcript"], session_id=cmd_payload["session_id"])
    assert task_id is not None

    await asyncio.sleep(0.8)

    # 6. Simulate TTS Response Synthesis
    response_audio = await tts.synthesize(f"Completed task '{transcript}'.")
    assert response_audio == b"MOCK_TTS_AUDIO_BYTES"
    assert tts.last_spoken_text == "Completed task 'Open Visual Studio Code.'."
