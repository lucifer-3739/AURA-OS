from enum import Enum
from typing import Dict, Any, Callable, List
import asyncio
import logging

logger = logging.getLogger("AURA_OS.VoiceEvents")

class VoiceEventType(str, Enum):
    WAKE_WORD_DETECTED = "wake_word_detected"
    LISTENING_STARTED = "listening_started"
    LISTENING_STOPPED = "listening_stopped"
    SPEECH_STARTED = "speech_started"
    SPEECH_PARTIAL = "speech_partial"
    SPEECH_FINAL = "speech_final"
    COMMAND_RECEIVED = "command_received"
    AI_RESPONSE_STARTED = "ai_response_started"
    TOOL_EXECUTION_STARTED = "tool_execution_started"
    TOOL_EXECUTION_FINISHED = "tool_execution_finished"
    PERMISSION_REQUESTED = "permission_requested"
    PERMISSION_APPROVED = "permission_approved"
    PERMISSION_REJECTED = "permission_rejected"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    SPEECH_STOPPED = "speech_stopped"
    VOICE_ERROR = "voice_error"

class VoiceEventEmitter:
    def __init__(self):
        self.listeners: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        self.listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]):
        if callback in self.listeners:
            self.listeners.remove(callback)

    async def emit(self, event_type: VoiceEventType, data: Optional[Dict[str, Any]] = None):
        payload = {
            "event": event_type.value,
            "data": data or {}
        }
        for listener in self.listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(payload)
                else:
                    listener(payload)
            except Exception as e:
                logger.error(f"Error in voice event listener: {e}")

voice_event_emitter = VoiceEventEmitter()
