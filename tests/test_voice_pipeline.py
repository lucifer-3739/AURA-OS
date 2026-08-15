import pytest
import asyncio
from agent.voice.audio import audio_capture, playback_controller
from agent.voice.pipeline import voice_pipeline, voice_session

@pytest.mark.asyncio
async def test_audio_capture_and_mute():
    audio_capture.mute()
    assert audio_capture.is_muted is True
    vol = audio_capture.calculate_volume_rms(b"\x01\x00\x02\x00")
    assert vol == 0.0

    audio_capture.unmute()
    assert audio_capture.is_muted is False

@pytest.mark.asyncio
async def test_playback_interruption():
    playback_controller.is_speaking = True
    playback_controller.stop_speaking()
    assert playback_controller.is_speaking is False

def test_voice_session_context():
    cmd = voice_session.new_command("Open Chrome", source="voice")
    assert cmd["transcript"] == "Open Chrome"
    assert cmd["source"] == "voice"
    assert "command_id" in cmd
