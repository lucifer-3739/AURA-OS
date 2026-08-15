import asyncio
import logging
from typing import Dict, Any
from agent.voice.wake_word.base import WakeWordProvider
from agent.config import settings

logger = logging.getLogger("AURA_OS.WakeWord")

class MockWakeWordProvider(WakeWordProvider):
    def __init__(self):
        self.sensitivity: float = 0.5
        self.should_trigger: bool = False

    def trigger_once(self):
        self.should_trigger = True

    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        await asyncio.sleep(0.5)
        if self.should_trigger:
            self.should_trigger = False  # Reset after one trigger
            return True
        return False

    def configure(self, settings: Dict[str, Any]):
        self.sensitivity = settings.get("sensitivity", 0.5)

class LocalWakeWordProvider(WakeWordProvider):
    """Local wake word detection framework placeholder."""
    def __init__(self):
        self.sensitivity: float = 0.5
        self.should_trigger: bool = False

    def trigger_once(self):
        self.should_trigger = True

    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        await asyncio.sleep(0.5)
        if self.should_trigger:
            self.should_trigger = False
            return True
        return False

    def configure(self, settings: Dict[str, Any]):
        self.sensitivity = settings.get("sensitivity", 0.5)

class CloudWakeWordProvider(WakeWordProvider):
    """Cloud wake word detection framework placeholder."""
    def __init__(self):
        self.should_trigger: bool = False

    def trigger_once(self):
        self.should_trigger = True

    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        await asyncio.sleep(0.5)
        if self.should_trigger:
            self.should_trigger = False
            return True
        return False

    def configure(self, settings: Dict[str, Any]):
        pass

def get_wake_word_provider() -> WakeWordProvider:
    if settings.stt_provider == "local":
        return LocalWakeWordProvider()
    elif settings.stt_provider == "cloud":
        return CloudWakeWordProvider()
    return MockWakeWordProvider()

wake_word_provider = get_wake_word_provider()
