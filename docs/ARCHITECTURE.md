# AURA OS Architecture Overview (Phases 1, 2 & 3)

## Overview
AURA OS is an AI-native voice-controlled computer assistant built around an observe → plan → act → verify loop.

```
Microphone → Audio Capture → Wake-Word Detection → STT → Command Normalization → AI Orchestrator → Context + Memory → Planner → Tool Router → Permission Manager → Tool Execution (OS / Browser / Tools) → Computer OS / Web → Observation → Verification → Response Generation → TTS → Audio Output
```

## Modular Layering

### 1. Browser Automation Subsystem (`agent/browser/`)
* **Driver Abstraction (`agent/browser/base.py`)**: `BrowserDriver` interface supporting `MockBrowserDriver` (zero-dependency offline driver) and `HeadlessBrowserDriver` (Playwright / Selenium).
* **DOM Parser (`agent/browser/dom_parser.py`)**: Extracts structured interactive DOM element trees (`inputs`, `buttons`, `links`) and clean markdown text content.
* **Registered Tools (`agent/tools/browser.py`)**: `open_url`, `search_web`, `click_element`, `type_text`, `read_page`, `extract_data`, `download_file`, `close_browser`.
* **Browser Monitor UI (`apps/frontend/src/components/BrowserMonitor.tsx`)**: Renders tab URL header, active page title, extracted clean text content, and interactive DOM element inspector tree.

### 2. Voice Interaction Subsystem (`agent/voice/`)
* **Audio**: Microphones discovery (`GET /api/audio/devices`), volume meter & VAD, playback controller & speech interruption.
* **Wake Word**: Keyword detector (`"Hey Aura"`).
* **Speech-to-Text**: STT engine with streaming partials and Web Speech API browser mic integration.
* **Text-to-Speech**: TTS synthesis output & browser speech synthesis playback.
* **Fast-Path Interruption Layer**: Instant evaluation for "stop talking", "cancel task", and voice permission confirmations ("yes"/"no").

### 3. Agent Core (`agent/core/`)
* **Orchestrator**: Maintains task, voice, and browser states. Broadcasts updates over WebSockets.
* **Planner**: Decomposes user goals into structured tool calls using `AIProvider` abstractions (Gemini + Mock fallback).
* **Executor**: Intercepts tool calls, evaluates security risks, invokes tools, and passes results to the verifier.
* **Verifier**: Assesses execution success using tool-specific verification methods.
* **Context**: Aggregates environment variables, active workspace paths, user preferences, and conversation histories into prompts.

### 4. Security System (`agent/security/`)
* **Risk Levels**: `SAFE`, `MODERATE`, `DANGEROUS`, `CRITICAL`.
* **Interruption Prompt**: `DANGEROUS` and `CRITICAL` operations pause execution and require explicit user approval via API, UI, or Voice ("Yes"/"No").
* **Audit Logging**: Every action is saved into SQLite table `audit_log` and logged via Python structured loggers.

### 5. Memory Subsystem (`agent/memory/`)
* Short-term conversation memory, long-term user preferences, task step history, and voice session context.
