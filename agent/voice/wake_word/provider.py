import asyncio
import logging
from typing import Dict, Any
from agent.voice.wake_word.base import WakeWordProvider
from agent.config import settings

logger = logging.getLogger("AURA_OS.WakeWord")

class MockWakeWordProvider(WakeWordProvider):
    def __init__(self):
        self.sensitivity: float = 0.5
        self.should_trigger: bool = True

    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        await asyncio.sleep(0.2)
        return self.should_trigger

    def configure(self, settings: Dict[str, Any]):
        self.sensitivity = settings.get("sensitivity", 0.5)

class LocalWakeWordProvider(WakeWordProvider):
    """Local wake word detection framework placeholder."""
    def __init__(self):
        self.sensitivity: float = 0.5

    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        logger.info(f"Local WakeWord engine checking stream for keyword '{target_word}'")
        await asyncio.sleep(0.3)
        return True

    def configure(self, settings: Dict[str, Any]):
        self.sensitivity = settings.get("sensitivity", 0.5)

class CloudWakeWordProvider(WakeWordProvider):
    """Cloud wake word detection framework placeholder."""
    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        await asyncio.sleep(0.3)
        return True

    def configure(self, settings: Dict[str, Any]):
        pass

def get_wake_word_provider() -> WakeWordProvider:
    if settings.stt_provider == "local":
        return LocalWakeWordProvider()
    elif settings.stt_provider == "cloud":
        return CloudWakeWordProvider()
    return MockWakeWordProvider()

wake_word_provider = get_wake_word_provider()
