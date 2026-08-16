import os
import io
import asyncio
import logging
from typing import List
from agent.voice.text_to_speech.base import TextToSpeechProvider
from agent.config import settings

logger = logging.getLogger("AURA_OS.TTS")

class TTSService:
    def __init__(self):
        self.provider = os.getenv("TTS_PROVIDER", settings.tts_provider).lower()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default Rachel voice

    def synthesize(self, text: str) -> bytes:
        """
        Synthesizes text to speech.
        Returns audio bytes (MP3 format).
        """
        if not text.strip():
            return b""

        if self.provider == "elevenlabs" and self.elevenlabs_key:
            return self._synthesize_elevenlabs(text)
        elif self.provider == "openai" and self.openai_key:
            return self._synthesize_openai(text)
        else:
            # Default fallback to gTTS
            return self._synthesize_gtts(text)

    def _synthesize_gtts(self, text: str) -> bytes:
        try:
            from gtts import gTTS
            fp = io.BytesIO()
            tts = gTTS(text=text, lang='en')
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception as e:
            logger.warning(f"gTTS synthesis failed: {e}. Returning fallback bytes.")
            return b"MOCK_TTS_AUDIO_BYTES"

    def _synthesize_openai(self, text: str) -> bytes:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": "alloy"
            }
            response = requests.post(
                "https://api.openai.com/v1/audio/speech",
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(f"OpenAI TTS error: {response.text}. Falling back to gTTS.")
                return self._synthesize_gtts(text)
        except Exception as e:
            logger.warning(f"OpenAI TTS exception: {e}. Falling back to gTTS.")
            return self._synthesize_gtts(text)

    def _synthesize_elevenlabs(self, text: str) -> bytes:
        try:
            import requests
            headers = {
                "xi-api-key": self.elevenlabs_key,
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                logger.warning(f"ElevenLabs TTS error: {response.text}. Falling back to gTTS.")
                return self._synthesize_gtts(text)
        except Exception as e:
            logger.warning(f"ElevenLabs TTS exception: {e}. Falling back to gTTS.")
            return self._synthesize_gtts(text)

class MultiProviderTTS(TextToSpeechProvider):
    def __init__(self):
        self.service = TTSService()
        self.last_spoken_text: str = ""
        self.spoken_history: List[str] = []

    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        self.last_spoken_text = text
        self.spoken_history.append(text)
        loop = asyncio.get_running_loop()
        audio_bytes = await loop.run_in_executor(None, self.service.synthesize, text)
        return audio_bytes

class LocalTTSProvider(TextToSpeechProvider):
    """Local Text-to-Speech framework provider using gTTS / local engines."""
    def __init__(self):
        self.service = TTSService()
        self.last_spoken_text: str = ""
        self.spoken_history: List[str] = []

    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        self.last_spoken_text = text
        self.spoken_history.append(text)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.service._synthesize_gtts, text)

class CloudTTSProvider(TextToSpeechProvider):
    """Cloud Text-to-Speech provider using OpenAI / ElevenLabs APIs."""
    def __init__(self):
        self.service = TTSService()
        self.last_spoken_text: str = ""
        self.spoken_history: List[str] = []

    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        self.last_spoken_text = text
        self.spoken_history.append(text)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.service.synthesize, text)

class MockTTSProvider(TextToSpeechProvider):
    def __init__(self):
        self.last_spoken_text: str = ""
        self.spoken_history: List[str] = []

    async def synthesize(self, text: str, voice: str = "default", speed: float = 1.0) -> bytes:
        self.last_spoken_text = text
        self.spoken_history.append(text)
        logger.info(f"Synthesized Mock TTS speech: '{text}'")
        await asyncio.sleep(0.1)
        return b"MOCK_TTS_AUDIO_BYTES"

def get_tts_provider() -> TextToSpeechProvider:
    if settings.tts_provider == "mock":
        return MockTTSProvider()
    elif settings.tts_provider == "local":
        return LocalTTSProvider()
    elif settings.tts_provider == "cloud":
        return CloudTTSProvider()
    return MultiProviderTTS()

tts_provider = get_tts_provider()
