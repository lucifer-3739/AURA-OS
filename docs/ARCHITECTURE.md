# AURA OS Architecture Overview (Phase 1 & 2)

## Overview
AURA OS is an AI-native voice-controlled computer assistant built around an observe → plan → act → verify loop.

```
Microphone → Audio Capture → Wake-Word Detection → STT → Command Normalization → AI Orchestrator → Context + Memory → Planner → Tool Router → Permission Manager → Tool Execution → Computer OS → Observation → Verification → Response Generation → TTS → Audio Output
```

## Modular Layering

### 1. Voice Interaction Subsystem (`agent/voice/`)
* **Audio (`agent/voice/audio/`)**: `device_manager.py` (microphones discovery), `capture.py` (RMS volume meter & Voice Activity Detection), `playback.py` (audio output & speech interruption).
* **Wake Word (`agent/voice/wake_word/`)**: `WakeWordProvider` interface supporting `LocalWakeWordProvider`, `CloudWakeWordProvider`, and `MockWakeWordProvider`. Default keyword: `"Aura"`.
* **Speech-to-Text (`agent/voice/speech_to_text/`)**: `SpeechToTextProvider` interface supporting `LocalSTTProvider`, `CloudSTTProvider`, and `MockSTTProvider` with streaming partial transcript support.
* **Text-to-Speech (`agent/voice/text_to_speech/`)**: `TextToSpeechProvider` interface supporting `LocalTTSProvider`, `CloudTTSProvider`, and `MockTTSProvider`.
* **Voice Pipeline (`agent/voice/pipeline/`)**: Central non-blocking background loop handling `WAITING_FOR_WAKE_WORD` → `LISTENING` → `PROCESSING_SPEECH` → `THINKING` → `EXECUTING` → `SPEAKING` transitions. Includes fast-path interruption layer ("stop talking", "cancel task", "yes"/"no" permissions).
* **Events (`agent/voice/events/`)**: `VoiceEventEmitter` bridging internal events to WebSocket broadcasts.

### 2. Agent Core (`agent/core/`)
* **Orchestrator**: Maintains task and voice states. Broadcasts updates over WebSockets.
* **Planner**: Decomposes user goals into structured tool calls using `AIProvider` abstractions (Gemini + Mock fallback).
* **Executor**: Intercepts tool calls, evaluates security risks, invokes tools, and passes results to the verifier.
* **Verifier**: Assesses execution success using tool-specific verification methods.
* **Context**: Aggregates environment variables, active workspace paths, user preferences, and conversation histories into prompts.

### 3. Security System (`agent/security/`)
* **Risk Levels**: `SAFE`, `MODERATE`, `DANGEROUS`, `CRITICAL`.
* **Interruption Prompt**: `DANGEROUS` and `CRITICAL` operations pause execution and require explicit user approval via API, UI, or Voice ("Yes"/"No").
* **Audit Logging**: Every action is saved into SQLite table `audit_log` and logged via Python structured loggers.

### 4. Memory Subsystem (`agent/memory/`)
* **Short-Term**: Live session context.
* **Long-Term**: Persistent user preferences.
* **Task Memory**: Plan execution step history.
* **Voice Session Context**: Context retention for follow-up voice commands.

### 5. Tool Registry (`agent/tools/`)
Decorated tools with parameter schemas, risk levels, and custom verification callbacks.
* `filesystem`: `create_file`, `read_file`, `write_file`, `copy_file`, `move_file`, `delete_file`, `create_folder`, `search_files`, `list_directory`
* `system`: `open_application`, `close_application`, `system_information`, `volume_control`, `shutdown`, `restart`
* `browser`: `open_url`, `search_web`, `download_file`
* `terminal`: `execute_command`, `get_command_output`
* `computer`: `screenshot`
