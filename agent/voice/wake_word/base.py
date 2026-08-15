from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class WakeWordProvider(ABC):
    @abstractmethod
    async def listen_for_wakeword(self, target_word: str = "Aura", sensitivity: float = 0.5) -> bool:
        """Listen audio stream for the target wake word."""
        pass

    @abstractmethod
    def configure(self, settings: Dict[str, Any]):
        """Update sensitivity or trigger settings."""
        pass
