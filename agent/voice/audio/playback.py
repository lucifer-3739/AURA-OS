import asyncio
import logging
from typing import Optional, Callable

logger = logging.getLogger("AURA_OS.AudioPlayback")

class AudioPlaybackController:
    def __init__(self):
        self.is_speaking: bool = False
        self._current_task: Optional[asyncio.Task] = None
        self.on_started_callback: Optional[Callable[[], None]] = None
        self.on_finished_callback: Optional[Callable[[], None]] = None

    def stop_speaking(self):
        """Immediately interrupt and stop active speech output."""
        if self.is_speaking:
            logger.info("Speech output interrupted by user command/action.")
            self.is_speaking = False
            if self._current_task and not self._current_task.done():
                self._current_task.cancel()
            if self.on_finished_callback:
                try:
                    self.on_finished_callback()
                except Exception:
                    pass

    async def play_audio(self, audio_bytes: bytes, duration_sec: float = 1.5):
        """Play audio bytes with interruption cancellation support."""
        self.stop_speaking()  # Cancel any prior active speech
        self.is_speaking = True

        if self.on_started_callback:
            try:
                self.on_started_callback()
            except Exception:
                pass

        try:
            self._current_task = asyncio.current_task()
            await asyncio.sleep(duration_sec)
        except asyncio.CancelledError:
            logger.info("Audio playback task cancelled.")
        finally:
            self.is_speaking = False
            if self.on_finished_callback:
                try:
                    self.on_finished_callback()
                except Exception:
                    pass

playback_controller = AudioPlaybackController()
