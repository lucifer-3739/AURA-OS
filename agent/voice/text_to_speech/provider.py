import asyncio
import logging
from typing import List
from agent.voice.text_to_speech.base import TextToSpeechProvider
from agent.config import settings

logger = logging.getLogger("AURA_OS.TTS")

class MockTTSProvider(TextToSpeechProvider):
    def __init__(self):
        self.last_spoken_text: str = ""
        self.spoken_history: List[str] = []

    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        self.last_spoken_text = text
        self.spoken_history.append(text)
        logger.info(f"Synthesized TTS speech: '{text}' (Voice={voice}, Speed={speed})")
        await asyncio.sleep(0.1)
        return b"MOCK_TTS_AUDIO_BYTES"

class LocalTTSProvider(TextToSpeechProvider):
    """Local Text-to-Speech framework placeholder (pyttsx3/EdgeTTS)."""
    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        logger.info(f"Local TTS synthesizing: '{text}'")
        await asyncio.sleep(0.2)
        return b"LOCAL_TTS_BYTES"

class CloudTTSProvider(TextToSpeechProvider):
    """Cloud Text-to-Speech framework placeholder (ElevenLabs/Google TTS)."""
    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        logger.info(f"Cloud TTS synthesizing: '{text}'")
        await asyncio.sleep(0.2)
        return b"CLOUD_TTS_BYTES"

def get_tts_provider() -> TextToSpeechProvider:
    if settings.tts_provider == "local":
        return LocalTTSProvider()
    elif settings.tts_provider == "cloud":
        return CloudTTSProvider()
    return MockTTSProvider()

tts_provider = get_tts_provider()
