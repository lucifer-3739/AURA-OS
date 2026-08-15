from abc import ABC, abstractmethod

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        pass

class TextToSpeechProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        pass

class WakeWordProvider(ABC):
    @abstractmethod
    async def listen_for_wakeword((self) -> bool:
        pass

class MockSpeechToText(SpeechToTextProvider):
    async def transcribe(self, audio_data: bytes) -> str:
        return "Open VS Code."

class MockTextToSpeech(TextToSpeechProvider):
    async def synthesize(self, text: str) -> bytes:
        return b"MOCK_AUDIO_BYTES"

class MockWakeWord(WakeWordProvider):
    async def listen_for_wakeword(self) -> bool:
        return True
