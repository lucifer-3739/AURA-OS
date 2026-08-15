# AURA OS — AI-Native Voice-Controlled Computer Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AURA OS** is an AI-native computer assistant environment designed to evolve from a local voice-first desktop application into an autonomous AI operating environment.

---

## 🌟 Architecture & Features

### 1. Observe → Plan → Act → Verify Loop
AURA OS uses a structured state machine cycle (`IDLE` → `WAITING_FOR_WAKE_WORD` → `LISTENING` → `PROCESSING_SPEECH` → `THINKING` → `PLANNING` → `WAITING_FOR_PERMISSION` → `EXECUTING` → `OBSERVING` → `VERIFYING` → `SPEAKING` → `COMPLETED`).

### 2. Multi-Level Security Permission System
* **Risk Levels**: `SAFE`, `MODERATE`, `DANGEROUS`, `CRITICAL`.
* **Interactive Confirmations**: Dangerous operations pause execution and prompt the user via UI modal or voice ("Yes"/"No").
* **Audit Trail**: Every tool invocation is logged into SQLite (`audit_log`) and structured system logs.

### 3. Voice Interaction Subsystem (Phase 2)
* **Provider Abstractions**: Decoupled interfaces for `WakeWordProvider`, `SpeechToTextProvider`, `TextToSpeechProvider`, and `AudioCaptureProvider`.
* **Wake-Word Engine**: Default keyword `"Hey Aura"`.
* **Fast-Path Interruption Layer**: Instant evaluation (< 50ms) for high-priority commands ("stop talking", "cancel task", "yes"/"no" permissions).
* **Live Transcription Streaming**: Real-time partial & final transcription feed emitted over WebSockets.

### 4. Tool Registry (`agent/tools/`)
* **Filesystem**: `create_file`, `read_file`, `write_file`, `copy_file`, `move_file`, `delete_file`, `create_folder`, `search_files`, `list_directory`
* **System**: `open_application`, `close_application`, `system_information`, `volume_control`, `shutdown`, `restart`
* **Browser**: `open_url`, `search_web`, `download_file`
* **Terminal**: `execute_command`, `get_command_output`
* **Computer**: `screenshot`

---

## 📁 Directory Structure

```
aura-os/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── run.txt
├── apps/
│   ├── desktop/
│   │   └── README.md              # Desktop shell placeholder (Phase 8)
│   ├── frontend/                  # React 18 + TypeScript + Vite UI
│   │   ├── src/
│   │   │   ├── components/        # VoiceController, TaskMonitor, ConsoleLog, etc.
│   │   │   ├── hooks/             # useWebSocket.ts
│   │   │   └── App.tsx
│   │   └── package.json
│   └── shell/                     # FastAPI Backend Server
│       ├── main.py
│       └── requirements.txt
├── agent/                         # Core Agent System
│   ├── core/                      # Orchestrator, Planner, Executor, Verifier, Context
│   ├── voice/                     # Audio, WakeWord, STT, TTS, VoicePipeline, Events
│   ├── tools/                     # Tool Registry & Implementation Modules
│   ├── memory/                    # SQLite Short-term, Long-term, Task Memory
│   ├── security/                  # Permission Manager, Audit Logger, Sandbox
│   ├── database/                  # SQLite async wrapper (db.py)
│   └── config/                    # Global settings (settings.py)
├── tests/                         # Automated Pytest Suite (18 tests)
└── scripts/                       # Test runner scripts
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env`:

```env
AI_PROVIDER=mock          # Options: mock, gemini
GEMINI_API_KEY=your_key   # Optional when using gemini provider
DATABASE_PATH=aura_os.db
LOG_LEVEL=INFO
PERMISSION_MODE=interactive # interactive, strict, permissive
HOST=127.0.0.1
PORT=8000

# Voice Settings
VOICE_ENABLED=true
WAKE_WORD_ENABLED=true
WAKE_WORD=Aura
WAKE_WORD_SENSITIVITY=0.5
STT_PROVIDER=mock         # mock, local, cloud
STT_LANGUAGE=en-US
TTS_ENABLED=true
TTS_PROVIDER=mock         # mock, local, cloud
TTS_VOICE=default
TTS_SPEED=1.0
VOICE_SESSION_TIMEOUT=30
VOICE_RECORDING_ENABLED=false
MICROPHONE_DEVICE=default
```

---

## 🚀 Quick Start Guide

### 1. Start FastAPI Backend Shell
```bash
# In project root: d:\Code\AURA OS
.\venv\Scripts\python apps/shell/main.py
```
* Backend runs at `http://127.0.0.1:8000`.

### 2. Start React Desktop UI
```bash
# In frontend directory: d:\Code\AURA OS\apps\frontend
npm run dev
```
* Frontend runs at `http://localhost:3000`.

---

## 🧪 Testing

Run the full automated Pytest suite (18 passed tests):
```bash
.\venv\Scripts\pytest
```

Or run the standalone runner:
```bash
.\venv\Scripts\python scripts/run_tests.py
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).
