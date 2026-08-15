from abc import ABC, abstractmethod

class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        """Synthesize text string into audio bytes."""
        pass
