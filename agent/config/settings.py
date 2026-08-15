import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Settings:
    ai_provider: str = os.getenv("AI_PROVIDER", "mock")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    database_path: str = os.getenv("DATABASE_PATH", "aura_os.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    permission_mode: str = os.getenv("PERMISSION_MODE", "interactive")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

    # Voice Configuration (Phase 2)
    voice_enabled: bool = os.getenv("VOICE_ENABLED", "true").lower() == "true"
    wake_word_enabled: bool = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
    wake_word: str = os.getenv("WAKE_WORD", "Aura")
    wake_word_sensitivity: float = float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5"))
    stt_provider: str = os.getenv("STT_PROVIDER", "mock")  # mock, local, cloud
    stt_language: str = os.getenv("STT_LANGUAGE", "en-US")
    tts_enabled: bool = os.getenv("TTS_ENABLED", "true").lower() == "true"
    tts_provider: str = os.getenv("TTS_PROVIDER", "mock")  # mock, local, cloud
    tts_voice: str = os.getenv("TTS_VOICE", "default")
    tts_speed: float = float(os.getenv("TTS_SPEED", "1.0"))
    voice_session_timeout: int = int(os.getenv("VOICE_SESSION_TIMEOUT", "30"))
    voice_recording_enabled: bool = os.getenv("VOICE_RECORDING_ENABLED", "false").lower() == "true"
    microphone_device: str = os.getenv("MICROPHONE_DEVICE", "default")

    # Project root path
    base_dir: Path = Path(__file__).resolve().parent.parent.parent

settings = Settings()
