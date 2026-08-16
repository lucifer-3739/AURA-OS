@echo off
title AURA OS — Native Windows Desktop Voice Assistant
echo ======================================================================
echo                  LAUNCHING AURA OS DESKTOP VOICE AGENT
echo ======================================================================
cd /d "%~dp0"
.\venv\Scripts\python apps/desktop/main_gui.py
pause
