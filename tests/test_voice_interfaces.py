import pytest
from agent.voice.wake_word import MockWakeWordProvider
from agent.voice.speech_to_text import MockSTTProvider
from agent.voice.text_to_speech import MockTTSProvider
from agent.voice.audio import device_manager

@pytest.mark.asyncio
async def test_wake_word_provider_interface():
    provider = MockWakeWordProvider()
    provider.trigger_once()
    triggered = await provider.listen_for_wakeword("Aura", sensitivity=0.5)
    assert triggered is True

@pytest.mark.asyncio
async def test_stt_provider_interface():
    stt = MockSTTProvider("Open Visual Studio Code.")
    res = await stt.transcribe(b"MOCK_PCM_DATA")
    assert res == "Open Visual Studio Code."

    partials = []
    async for chunk in stt.transcribe_stream(b"MOCK_PCM_DATA"):
        partials.append(chunk)
    assert len(partials) > 0
    assert partials[-1]["final"] is True

@pytest.mark.asyncio
async def test_tts_provider_interface():
    tts = MockTTSProvider()
    audio = await tts.synthesize("Opening Visual Studio Code.")
    assert audio == b"MOCK_TTS_AUDIO_BYTES"
    assert tts.last_spoken_text == "Opening Visual Studio Code."

def test_device_manager():
    devs = device_manager.get_input_devices()
    assert len(devs) > 0
    assert device_manager.check_health()["status"] == "healthy"
