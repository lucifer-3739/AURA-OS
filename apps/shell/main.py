import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to sys.path so 'agent' package can be imported easily
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.config import settings
from agent.database import db
from agent.core import orchestrator
from agent.tools import registry
from agent.memory import long_term_memory, task_memory
from agent.security import permission_manager
from agent.tools.system import system_information

# Voice package imports (Phase 2)
from agent.voice import (
    device_manager,
    voice_pipeline,
    voice_event_emitter,
    audio_capture,
    stt_provider,
    tts_provider,
    playback_controller
)

app = FastAPI(
    title="AURA OS Shell API",
    description="AI-Native Voice & Desktop Computer Agent Shell API",
    version="0.2.0"
)

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket Connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

# Subscribe orchestrator & voice events to WebSocket broadcast
async def _ws_event_listener(event_payload: Dict[str, Any]):
    await ws_manager.broadcast(event_payload)

orchestrator.subscribe(_ws_event_listener)
voice_event_emitter.subscribe(_ws_event_listener)

# Startup Lifecycle
@app.on_event("startup")
async def startup_event():
    await db.initialize()
    if settings.voice_enabled:
        await voice_pipeline.start()

@app.on_event("shutdown")
async def shutdown_event():
    await voice_pipeline.stop()

# Pydantic Schemas
class CommandRequest(BaseModel):
    command: str
    session_id: str = "default_session"

class MemoryRequest(BaseModel):
    key: str
    value: Any

class DeviceSelectRequest(BaseModel):
    device_id: str

# REST Endpoints
@app.post("/api/command")
async def post_command(req: CommandRequest):
    if not req.command.strip():
        raise HTTPException(status_code=400, detail="Command cannot be empty")
    task_id = await orchestrator.run_command(req.command, req.session_id)
    return {"task_id": task_id, "status": orchestrator.current_state.value}

@app.post("/api/voice")
async def post_voice(req: CommandRequest):
    return await post_command(req)

@app.get("/api/status")
async def get_status():
    sys_info = await system_information()
    return {
        "state": orchestrator.current_state.value,
        "current_task_id": orchestrator.current_task_id,
        "permission_mode": settings.permission_mode,
        "voice_pipeline_running": voice_pipeline.is_running,
        "voice_muted": voice_pipeline.is_muted,
        "system": sys_info
    }

# Phase 2 Voice API Additions
@app.get("/api/audio/devices")
async def get_audio_devices():
    devices = device_manager.get_input_devices()
    return {"devices": devices, "selected_device": device_manager.selected_device}

@app.post("/api/audio/devices/select")
async def select_audio_device(req: DeviceSelectRequest):
    success = device_manager.set_device(req.device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"success": True, "selected_device": req.device_id}

@app.get("/api/voice/status")
async def get_voice_status():
    return {
        "voice_enabled": settings.voice_enabled,
        "is_running": voice_pipeline.is_running,
        "is_muted": voice_pipeline.is_muted,
        "is_speaking": playback_controller.is_speaking,
        "wake_word": settings.wake_word,
        "wake_word_enabled": settings.wake_word_enabled,
        "stt_provider": settings.stt_provider,
        "tts_provider": settings.tts_provider
    }

@app.post("/api/voice/start")
async def start_voice():
    await voice_pipeline.start()
    return {"success": True, "is_running": voice_pipeline.is_running}

@app.post("/api/voice/stop")
async def stop_voice():
    await voice_pipeline.stop()
    return {"success": True, "is_running": voice_pipeline.is_running}

@app.post("/api/voice/mute")
async def mute_voice():
    voice_pipeline.mute()
    return {"success": True, "is_muted": voice_pipeline.is_muted}

@app.post("/api/voice/unmute")
async def unmute_voice():
    voice_pipeline.unmute()
    return {"success": True, "is_muted": voice_pipeline.is_muted}

@app.post("/api/voice/interrupt")
async def interrupt_speech():
    playback_controller.stop_speaking()
    return {"success": True, "message": "Speech output interrupted"}

@app.post("/api/voice/test")
async def test_voice_command():
    """Trigger a simulated end-to-end voice command run."""
    task_id = await orchestrator.run_command("Open Visual Studio Code.", session_id="voice_test_session")
    if settings.tts_enabled:
        asyncio.create_task(playback_controller.play_audio(b"MOCK_TEST_AUDIO", duration_sec=1.0))
    return {"success": True, "task_id": task_id, "state": orchestrator.current_state.value}

@app.get("/api/voice/config")
async def get_voice_config():
    return {
        "voice_enabled": settings.voice_enabled,
        "wake_word": settings.wake_word,
        "wake_word_enabled": settings.wake_word_enabled,
        "stt_provider": settings.stt_provider,
        "stt_language": settings.stt_language,
        "tts_provider": settings.tts_provider,
        "tts_voice": settings.tts_voice,
        "voice_recording_enabled": settings.voice_recording_enabled
    }

# Memory & Tools APIs
@app.get("/api/tasks")
async def get_tasks():
    tasks = await task_memory.list_tasks()
    return {"tasks": tasks}

@app.get("/api/tasks/{task_id}")
async def get_task_by_id(task_id: str):
    task = await task_memory.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    playback_controller.stop_speaking()
    await orchestrator.cancel_task()
    return {"success": True, "task_id": task_id, "state": orchestrator.current_state.value}

@app.get("/api/memory")
async def get_memory():
    mems = await long_term_memory.get_all()
    return {"memory": mems}

@app.post("/api/memory")
async def set_memory(req: MemoryRequest):
    await long_term_memory.set_preference(req.key, req.value)
    return {"success": True, "key": req.key, "value": req.value}

@app.get("/api/tools")
async def get_tools():
    tools = registry.list_tools()
    return {"tools": tools}

@app.post("/api/permissions/approve")
async def approve_permission():
    asyncio.create_task(orchestrator.approve_permission())
    return {"success": True, "message": "Permission approved"}

@app.post("/api/permissions/reject")
async def reject_permission():
    asyncio.create_task(orchestrator.reject_permission())
    return {"success": True, "message": "Permission rejected"}

# WebSocket Endpoint
@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "event": "connection_established",
            "state": orchestrator.current_state.value,
            "task_id": orchestrator.current_task_id,
            "voice_pipeline_running": voice_pipeline.is_running
        })
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
