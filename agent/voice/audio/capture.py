import asyncio
import math
import struct
import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger("AURA_OS.AudioCapture")

class AudioCaptureProvider:
    def __init__(self):
        self.is_recording: bool = False
        self.is_muted: bool = False
        self.sample_rate: int = 16000
        self.chunk_size: int = 1024

    async def start_capture(self, on_chunk: Optional[Callable[[bytes], None]] = None):
        self.is_recording = True
        logger.info("Audio capture session started")

    async def stop_capture(self):
        self.is_recording = False
        logger.info("Audio capture session stopped")

    def mute(self):
        self.is_muted = True
        logger.info("Microphone muted")

    def unmute(self):
        self.is_muted = False
        logger.info("Microphone unmuted")

    def calculate_volume_rms(self, pcm_bytes: bytes) -> float:
        """Calculate Root Mean Square (RMS) volume level (0.0 to 1.0)."""
        if not pcm_bytes or self.is_muted:
            return 0.0
        try:
            count = len(pcm_bytes) // 2
            if count == 0:
                return 0.0
            shorts = struct.unpack(f"{count}h", pcm_bytes)
            sum_squares = sum(s * s for s in shorts)
            rms = math.sqrt(sum_squares / count)
            return min(1.0, rms / 32768.0)
        except Exception:
            return 0.0

    async def record_utterance(self, max_duration_sec: float = 8.0, silence_threshold_sec: float = 1.2) -> bytes:
        """Simulate/Capture a complete user audio utterance until speech ends."""
        if self.is_muted:
            return b""
        
        # Return simulated PCM audio frames for seamless local execution & testing
        await asyncio.sleep(0.5)
        simulated_pcm = b"\x00\x00\x01\x00" * 2000
        return simulated_pcm

audio_capture = AudioCaptureProvider()
