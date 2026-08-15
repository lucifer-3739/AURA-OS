from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "en-US") -> str:
        """Convert recorded PCM audio bytes into recognized text transcript."""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_chunk: bytes) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield partial and final transcript updates as user speaks."""
        pass
