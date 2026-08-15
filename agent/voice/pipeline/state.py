import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from agent.config import settings

class VoiceSessionContext:
    def __init__(self):
        self.session_id: str = str(uuid.uuid4())
        self.last_command_id: Optional[str] = None
        self.last_transcript: str = ""
        self.last_action_context: Dict[str, Any] = {}
        self.last_activity_timestamp: datetime = datetime.now(timezone.utc)
        self.is_active: bool = False

    def new_command(self, transcript: str, source: str = "voice") -> Dict[str, Any]:
        cmd_id = str(uuid.uuid4())
        self.last_command_id = cmd_id
        self.last_transcript = transcript
        self.last_activity_timestamp = datetime.now(timezone.utc)
        
        return {
            "session_id": self.session_id,
            "command_id": cmd_id,
            "source": source,
            "transcript": transcript,
            "timestamp": self.last_activity_timestamp.isoformat()
        }

    def is_session_expired(self) -> bool:
        elapsed = (datetime.now(timezone.utc) - self.last_activity_timestamp).total_seconds()
        return elapsed > settings.voice_session_timeout

    def reset_session(self):
        self.session_id = str(uuid.uuid4())
        self.last_command_id = None
        self.last_transcript = ""
        self.last_action_context = {}
        self.is_active = False

voice_session = VoiceSessionContext()
