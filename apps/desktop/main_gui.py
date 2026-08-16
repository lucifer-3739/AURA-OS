import sys
import os
import time
import asyncio
import threading
from pathlib import Path
from typing import Optional

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QProgressBar, QFrame,
    QSplitter, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QBrush, QPen

# Try loading speech recognition & pyttsx3
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import pyttsx3
    HAS_TTS = True
except ImportError:
    HAS_TTS = False

try:
    import sounddevice as sd
    import numpy as np
    HAS_SD = True
except ImportError:
    HAS_SD = False

# Import AURA OS Core modules
from agent.core import orchestrator, TaskState
from agent.tools.system import system_information
from agent.browser import browser_driver
from agent.database import db

class NativeVoiceListenerThread(QThread):
    voice_recognized = pyqtSignal(str)
    volume_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.is_muted = False
        self.recognizer = sr.Recognizer() if HAS_SR else None

    def stop(self):
        self.is_running = False

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        return self.is_muted

    def run(self):
        if not HAS_SR:
            self.status_updated.emit("SpeechRecognition library missing. Run pip install speechrecognition.")
            return

        self.status_updated.emit("Microphone listening active. Speak into your mic...")

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.is_running:
                    if self.is_muted:
                        time.sleep(0.5)
                        continue

                    try:
                        self.status_updated.emit("Listening for voice...")
                        audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=8)
                        self.status_updated.emit("Processing speech...")
                        
                        text = self.recognizer.recognize_google(audio)
                        if text and text.strip():
                            self.voice_recognized.emit(text.strip())
                            self.status_updated.emit(f"Recognized: '{text.strip()}'")
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        self.status_updated.emit(f"Mic status: {str(e)}")
                    time.sleep(0.2)
        except Exception as e:
            self.status_updated.emit(f"Microphone hardware error: {str(e)}")

class AuraDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AURA OS — AI Native Desktop Voice Agent")
        self.resize(1300, 850)
        self.setMinimumSize(1000, 650)
        
        # Initialize Database in background event loop
        asyncio.run(db.initialize())

        # Setup Theme & Stylesheet
        self.apply_dark_theme()
        self.init_ui()

        # Initialize Native Voice Thread
        self.voice_thread = NativeVoiceListenerThread()
        self.voice_thread.voice_recognized.connect(self.on_voice_recognized)
        self.voice_thread.status_updated.connect(self.on_voice_status)
        self.voice_thread.start()

        # System Stats Timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(3000)
        self.update_system_stats()

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #090d16;
                color: #f1f5f9;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            QWidget {
                color: #f1f5f9;
            }
            .glass-panel {
                background-color: rgba(15, 23, 42, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            QPushButton {
                background-color: #1e293b;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #00e5ff;
            }
            QPushButton#stopBtn {
                background-color: rgba(244, 63, 94, 0.2);
                color: #f43f5e;
                border: 1px solid #f43f5e;
            }
            QPushButton#stopBtn:hover {
                background-color: #f43f5e;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 14px;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #00e5ff;
            }
            QTextEdit {
                background-color: #0b101d;
                border: 1px solid #1e293b;
                border-radius: 8px;
                color: #38bdf8;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
            QListWidget {
                background-color: #0b101d;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 6px;
            }
        """)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # 1. Top Header Bar
        header_layout = QHBoxLayout()
        logo_label = QLabel("⚡ AURA OS")
        logo_label.setStyleSheet("font-size: 22px; font-weight: 800; color: #00e5ff;")
        subtitle_label = QLabel("Native Windows Voice Assistant Agent • Phase 3")
        subtitle_label.setStyleSheet("font-size: 12px; color: #94a3b8;")

        header_info = QVBoxLayout()
        header_info.addWidget(logo_label)
        header_info.addWidget(subtitle_label)
        header_layout.addLayout(header_info)
        header_layout.addStretch()

        self.stats_label = QLabel("CPU: -- | RAM: -- | Disk: --")
        self.stats_label.setStyleSheet("font-size: 12px; color: #a7f3d0; font-weight: 600;")
        header_layout.addWidget(self.stats_label)
        main_layout.addLayout(header_layout)

        # 2. Voice Control Bar
        voice_panel = QFrame()
        voice_panel.setProperty("class", "glass-panel")
        voice_layout = QHBoxLayout(voice_panel)

        self.status_label = QLabel("Microphone Status: Initializing...")
        self.status_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #38bdf8;")
        voice_layout.addWidget(self.status_label, stretch=2)

        self.mute_btn = QPushButton("Mute Mic")
        self.mute_btn.clicked.connect(self.on_toggle_mute)
        voice_layout.addWidget(self.mute_btn)

        self.stop_btn = QPushButton("STOP ALL (Emergency Cancel)")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.clicked.connect(self.on_emergency_stop)
        voice_layout.addWidget(self.stop_btn)

        self.test_btn = QPushButton("Test Command")
        self.test_btn.clicked.connect(self.on_test_command)
        voice_layout.addWidget(self.test_btn)

        main_layout.addWidget(voice_panel)

        # 3. Central Splitter: Task Monitor | Browser Preview | Audit Logs
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Column 1: Task Checklist
        task_box = QWidget()
        task_layout = QVBoxLayout(task_box)
        task_layout.setContentsMargins(0, 0, 0, 0)
        task_title = QLabel("📋 Active Task Execution Checklist")
        task_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #c084fc;")
        task_layout.addWidget(task_title)
        self.task_list = QListWidget()
        task_layout.addWidget(self.task_list)
        splitter.addWidget(task_box)

        # Column 2: Browser Monitor Text Preview
        browser_box = QWidget()
        browser_layout = QVBoxLayout(browser_box)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_title = QLabel("🌐 Autonomous Browser Monitor")
        browser_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #38bdf8;")
        browser_layout.addWidget(browser_title)
        self.browser_view = QTextEdit()
        self.browser_view.setReadOnly(True)
        self.browser_view.setPlaceholderText("Browser session output...")
        browser_layout.addWidget(self.browser_view)
        splitter.addWidget(browser_box)

        # Column 3: Console Audit Log Stream
        log_box = QWidget()
        log_layout = QVBoxLayout(log_box)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_title = QLabel("💻 System Audit Log Stream")
        log_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #34d399;")
        log_layout.addWidget(log_title)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)
        splitter.addWidget(log_box)

        main_layout.addWidget(splitter, stretch=1)

        # 4. Command Input Row
        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Say 'Aura...' or type a natural language command (e.g., 'Open Chrome', 'Organize folder Downloads')...")
        self.cmd_input.returnPressed.connect(self.on_submit_text_command)
        input_layout.addWidget(self.cmd_input, stretch=1)

        send_btn = QPushButton("Execute")
        send_btn.clicked.connect(self.on_submit_text_command)
        input_layout.addWidget(send_btn)

        main_layout.addLayout(input_layout)

    def log(self, message: str, level: str = "INFO"):
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        self.log_view.append(formatted)

    def speak_natively(self, text: str):
        if HAS_TTS:
            def tts_thread():
                try:
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass
            threading.Thread(target=tts_thread, daemon=True).start()

    def update_system_stats(self):
        async def fetch_stats():
            info = await system_information()
            cpu = info.get("cpu_percent", 0)
            ram = info.get("ram_percent", 0)
            disk = info.get("disk_percent", 0)
            self.stats_label.setText(f"CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%")
        asyncio.run(fetch_stats())

    def on_voice_status(self, msg: str):
        self.status_label.setText(f"Mic Status: {msg}")
        self.log(msg, "VOICE")

    def on_voice_recognized(self, text: str):
        self.log(f"Voice Picked Up: '{text}'", "SPEECH")
        self.execute_command(text)

    def on_submit_text_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.cmd_input.clear()
        self.execute_command(cmd)

    def execute_command(self, cmd: str):
        self.log(f"Executing Command: '{cmd}'", "COMMAND")
        
        async def run_cmd():
            task_id = await orchestrator.run_command(cmd)
            self.log(f"Dispatched Task ID: {task_id}", "ORCHESTRATOR")
            
            # Fetch plan steps
            self.task_list.clear()
            plan = orchestrator.current_plan
            for step in plan:
                item = QListWidgetItem(f"[{step.get('status', 'pending')}] {step.get('description', '')}")
                self.task_list.addItem(item)
            
            # Fetch browser state preview
            b_state = await browser_driver.get_page_content()
            self.browser_view.setText(f"URL: {b_state.get('url')}\nTitle: {b_state.get('title')}\n\n{b_state.get('content')}")
            
            self.speak_natively(f"Completed command: {cmd}")

        asyncio.run(run_cmd())

    def on_toggle_mute(self):
        is_muted = self.voice_thread.toggle_mute()
        self.mute_btn.setText("Unmute Mic" if is_muted else "Mute Mic")
        self.log("Microphone muted" if is_muted else "Microphone unmuted", "VOICE")

    def on_emergency_stop(self):
        async def cancel_all():
            await orchestrator.cancel_task()
            self.task_list.clear()
            self.log("EMERGENCY STOP EXECUTED — All tasks & speech cancelled.", "WARN")
            self.speak_natively("All tasks cancelled.")
        asyncio.run(cancel_all())

    def on_test_command(self):
        self.execute_command("Open Visual Studio Code.")

    def closeEvent(self, event):
        self.voice_thread.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AuraDesktopApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
