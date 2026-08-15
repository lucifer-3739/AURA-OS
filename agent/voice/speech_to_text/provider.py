import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from agent.voice.speech_to_text.base import SpeechToTextProvider
from agent.config import settings

logger = logging.getLogger("AURA_OS.STT")

class MockSTTProvider(SpeechToTextProvider):
    def __init__(self, default_transcript: str = "Open Visual Studio Code."):
        self.preset_transcript: str = default_transcript

    def set_transcript(self, transcript: str):
        self.preset_transcript = transcript

    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> str:
        await asyncio.sleep(0.2)
        return self.preset_transcript

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        words = self.preset_transcript.split()
        partial = ""
        for i, word in enumerate(words):
            partial = (partial + " " + word).strip()
            is_final = (i == len(words) - 1)
            yield {"text": partial, "final": is_final}
            await asyncio.sleep(0.1)

class LocalSTTProvider(SpeechToTextProvider):
    """Local Speech-to-Text framework placeholder (Whisper/Vosk)."""
    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> str:
        logger.info(f"Local STT transcribing audio chunk (Language: {language})")
        await asyncio.sleep(0.3)
        return "Open Chrome."

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"text": "Open Chrome.", "final": True}

class CloudSTTProvider(SpeechToTextProvider):
    """Cloud Speech-to-Text framework placeholder."""
    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> str:
        await asyncio.sleep(0.3)
        return "Search the web for React documentation."

    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"text": "Search the web for React documentation.", "final": True}

def get_stt_provider() -> SpeechToTextProvider:
    if settings.stt_provider == "local":
        return LocalSTTProvider()
    elif settings.stt_provider == "cloud":
        return CloudSTTProvider()
    return MockSTTProvider()

stt_provider = get_stt_provider()
