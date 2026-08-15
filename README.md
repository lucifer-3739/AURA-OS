# AURA OS — AI-Native Voice-Controlled Computer Agent

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AURA OS** is an AI-native computer assistant environment designed to evolve from a local voice-first desktop application into an autonomous AI operating environment.

---

## 🌟 Architecture & Capabilities

### Phase 1: Local AI Command System
* FastAPI backend shell and WebSocket task streaming engine (`apps/shell/`).
* React 18 + TypeScript dark-mode desktop frontend (`apps/frontend/`).
* SQLite memory engine (`agent/memory/`) and audit logger (`agent/security/audit.py`).
* Risk-level permission engine (`agent/security/permissions.py`).

### Phase 2: Voice Interaction Subsystem
* Provider-independent voice interfaces (`WakeWordProvider`, `SpeechToTextProvider`, `TextToSpeechProvider`, `AudioCaptureProvider`).
* Web Speech API real-time microphone voice recognition and speech synthesis output.
* Fast-path interruption layer ("stop talking", "cancel task", "yes"/"no" permissions).

### Phase 3: Browser Automation Subsystem
* **Driver Abstraction (`agent/browser/`)**: `BrowserDriver` interface supporting `MockBrowserDriver` (zero-dependency offline driver) and `HeadlessBrowserDriver` (Playwright / Selenium).
* **DOM Element Parser (`agent/browser/dom_parser.py`)**: Extracts structured interactive DOM element trees (`inputs`, `buttons`, `links`) and clean markdown text content.
* **Registered Tools (`agent/tools/browser.py`)**: `open_url`, `search_web`, `click_element`, `type_text`, `read_page`, `extract_data`, `download_file`, `close_browser`.
* **Browser Monitor UI (`apps/frontend/src/components/BrowserMonitor.tsx`)**: Renders tab URL header, active page title, extracted clean text content, and interactive DOM element inspector tree.

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

## 🧪 Running Tests

Run the complete 24-suite Pytest suite (100% pass rate):
```bash
.\venv\Scripts\pytest
```

Or run the standalone test runner:
```bash
.\venv\Scripts\python scripts/run_tests.py
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).
