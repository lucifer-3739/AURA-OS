import asyncio
import logging
from typing import Optional, Dict, Any
from agent.config import settings
from agent.core import orchestrator, TaskState
from agent.voice.audio import audio_capture, playback_controller, device_manager
from agent.voice.wake_word import wake_word_provider
from agent.voice.speech_to_text import stt_provider
from agent.voice.text_to_speech import tts_provider
from agent.voice.events import voice_event_emitter, VoiceEventType
from agent.voice.pipeline.state import voice_session

logger = logging.getLogger("AURA_OS.VoicePipeline")

class VoicePipeline:
    def __init__(self):
        self.is_running: bool = False
        self.is_muted: bool = False
        self._loop_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the background voice listening pipeline."""
        if self.is_running:
            return
        self.is_running = True
        self._loop_task = asyncio.create_task(self._pipeline_loop())
        logger.info("Voice pipeline started.")

    async def stop(self):
        """Stop the background voice listening pipeline."""
        self.is_running = False
        playback_controller.stop_speaking()
        if self._loop_task and not self._loop_task.done():
            self._loop_task.cancel()
        logger.info("Voice pipeline stopped.")

    def mute(self):
        self.is_muted = True
        audio_capture.mute()

    def unmute(self):
        self.is_muted = False
        audio_capture.unmute()

    async def _pipeline_loop(self):
        """Main non-blocking voice detection & execution loop."""
        while self.is_running:
            try:
                # 1. WAITING FOR WAKE WORD
                if settings.wake_word_enabled and not self.is_muted:
                    await orchestrator._set_state(TaskState.WAITING_FOR_WAKE_WORD)
                    await voice_event_emitter.emit(VoiceEventType.LISTENING_STARTED)
                    
                    detected = await wake_word_provider.listen_for_wakeword(
                        target_word=settings.wake_word,
                        sensitivity=settings.wake_word_sensitivity
                    )
                    
                    if not detected or not self.is_running:
                        await asyncio.sleep(0.5)
                        continue

                    # WAKE WORD DETECTED
                    await orchestrator._set_state(TaskState.WAKE_WORD_DETECTED)
                    await voice_event_emitter.emit(VoiceEventType.WAKE_WORD_DETECTED)
                    await asyncio.sleep(0.2)

                # 2. LISTENING FOR USER SPEECH
                await orchestrator._set_state(TaskState.LISTENING)
                await voice_event_emitter.emit(VoiceEventType.SPEECH_STARTED)
                
                audio_bytes = await audio_capture.record_utterance()
                if not audio_bytes or self.is_muted:
                    await orchestrator._set_state(TaskState.IDLE)
                    await asyncio.sleep(1.0)
                    continue

                # 3. PROCESSING SPEECH (STT)
                await orchestrator._set_state(TaskState.PROCESSING_SPEECH)
                
                # Stream partials if supported
                final_transcript = ""
                async for chunk in stt_provider.transcribe_stream(audio_bytes):
                    partial_text = chunk.get("text", "")
                    is_final = chunk.get("final", False)
                    await voice_event_emitter.emit(
                        VoiceEventType.SPEECH_FINAL if is_final else VoiceEventType.SPEECH_PARTIAL,
                        {"text": partial_text, "final": is_final}
                    )
                    if is_final:
                        final_transcript = partial_text

                if not final_transcript.strip():
                    await orchestrator._set_state(TaskState.IDLE)
                    await asyncio.sleep(1.0)
                    continue

                # 4. FAST-PATH HIGH-PRIORITY COMMAND INTERRUPT EVALUATION
                command_payload = voice_session.new_command(final_transcript, source="voice")
                await voice_event_emitter.emit(VoiceEventType.COMMAND_RECEIVED, command_payload)

                handled_fast = await self._handle_fast_path_command(final_transcript)
                if handled_fast:
                    await asyncio.sleep(0.5)
                    continue

                # 5. SEND NORMALIZED COMMAND TO EXISTING ORCHESTRATOR
                await orchestrator._set_state(TaskState.THINKING, {"transcript": final_transcript})
                task_id = await orchestrator.run_command(final_transcript, session_id=voice_session.session_id)

                # 6. SPEAK RESPONSE VIA TTS AFTER EXECUTION
                await self._speak_response(f"Completed task '{final_transcript}'.")
                
                await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in voice pipeline loop: {e}")
                await orchestrator._set_state(TaskState.ERROR, {"error": str(e)})
                await voice_event_emitter.emit(VoiceEventType.VOICE_ERROR, {"error": str(e)})
                await asyncio.sleep(2.0)

    async def _handle_fast_path_command(self, transcript: str) -> bool:
        """Evaluate fast-path interruption commands (< 50ms execution)."""
        t_lower = transcript.lower().strip()

        # A. Stop Speaking / Interruption
        if t_lower in ["stop talking", "be quiet", "shut up", "stop speaking", "hush"]:
            playback_controller.stop_speaking()
            await orchestrator._set_state(TaskState.INTERRUPTED, {"reason": "Speech stopped by voice"})
            await voice_event_emitter.emit(VoiceEventType.SPEECH_STOPPED)
            return True

        # B. Cancel Task
        if t_lower in ["cancel", "cancel task", "stop task", "abort"]:
            playback_controller.stop_speaking()
            await orchestrator.cancel_task()
            return True

        # C. Permission Confirmation (Yes / No)
        if t_lower in ["yes", "sure", "confirm", "approve", "do it"]:
            if orchestrator.current_state == TaskState.WAITING_FOR_PERMISSION:
                await orchestrator.approve_permission()
                await voice_event_emitter.emit(VoiceEventType.PERMISSION_APPROVED)
                return True

        if t_lower in ["no", "deny", "reject", "dont do it", "don't"]:
            if orchestrator.current_state == TaskState.WAITING_FOR_PERMISSION:
                await orchestrator.reject_permission()
                await voice_event_emitter.emit(VoiceEventType.PERMISSION_REJECTED)
                return True

        return False

    async def _speak_response(self, text: str):
        """Synthesize and play audio response."""
        if not settings.tts_enabled:
            return
        
        await orchestrator._set_state(TaskState.SPEAKING, {"response_text": text})
        await voice_event_emitter.emit(VoiceEventType.AI_RESPONSE_STARTED, {"text": text})

        audio_data = await tts_provider.synthesize(text, voice=settings.tts_voice, speed=settings.tts_speed)
        await playback_controller.play_audio(audio_data, duration_sec=1.0)
        
        await voice_event_emitter.emit(VoiceEventType.SPEECH_STOPPED)

voice_pipeline = VoicePipeline()
