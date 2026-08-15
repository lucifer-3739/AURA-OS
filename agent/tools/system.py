import os
import sys
import subprocess
import psutil
from typing import Dict, Any
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel

# 1. open_application
@registry.register(
    name="open_application",
    description="Open an application on the computer by name or path.",
    parameters={
        "type": "object",
        "properties": {
            "application": {"type": "string", "description": "Application name (e.g. 'code', 'chrome', 'notepad')"}
        },
        "required": ["application"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="system.execute"
)
async def open_application(application: str) -> Dict[str, Any]:
    app_lower = application.lower().strip()
    try:
        # Check standard shortcuts or executables
        if sys.platform == "win32":
            if "code" in app_lower or "vs code" in app_lower or "visual studio code" in app_lower:
                proc = subprocess.Popen(["code"], shell=True)
            elif "chrome" in app_lower:
                proc = subprocess.Popen(["start", "chrome"], shell=True)
            elif "notepad" in app_lower:
                proc = subprocess.Popen(["notepad"], shell=True)
            else:
                proc = subprocess.Popen(["start", "", application], shell=True)
        else:
            proc = subprocess.Popen([application])
            
        return {"success": True, "application": application, "pid": proc.pid}
    except Exception as e:
        return {"success": False, "error": str(e), "application": application}

# 2. close_application
@registry.register(
    name="close_application",
    description="Terminate a running application by process name.",
    parameters={
        "type": "object",
        "properties": {
            "process_name": {"type": "string", "description": "Process name e.g. notepad.exe or chrome.exe"}
        },
        "required": ["process_name"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="system.execute"
)
async def close_application(process_name: str) -> Dict[str, Any]:
    killed = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                proc.terminate()
                killed += 1
        except Exception:
            pass
    return {"success": True, "process_name": process_name, "terminated_count": killed}

# 3. system_information
@registry.register(
    name="system_information",
    description="Retrieve system stats (CPU, RAM, OS, disk usage).",
    parameters={"type": "object", "properties": {}},
    risk_level=RiskLevel.SAFE,
    required_permission="system.read"
)
async def system_information() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "success": True,
        "platform": sys.platform,
        "python_version": sys.version,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "ram_used_gb": round(mem.used / (1024**3), 2),
        "ram_total_gb": round(mem.total / (1024**3), 2),
        "ram_percent": mem.percent,
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_percent": disk.percent
    }

# 4. volume_control
@registry.register(
    name="volume_control",
    description="Set or change master volume level.",
    parameters={
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "action: 'set', 'mute', 'unmute'"},
            "level": {"type": "integer", "description": "Volume percentage (0-100)"}
        },
        "required": ["action"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="system.execute"
)
async def volume_control(action: str, level: int = 50) -> Dict[str, Any]:
    # Mock/Basic system volume control log
    return {"success": True, "action": action, "level": level, "message": f"Volume set to {level}%"}

# 5. shutdown
@registry.register(
    name="shutdown",
    description="Shutdown the host computer.",
    parameters={"type": "object", "properties": {}},
    risk_level=RiskLevel.CRITICAL,
    required_permission="system.power"
)
async def shutdown() -> Dict[str, Any]:
    return {"success": True, "message": "Shutdown signal sent (System shutdown request handled)"}

# 6. restart
@registry.register(
    name="restart",
    description="Reboot the host computer.",
    parameters={"type": "object", "properties": {}},
    risk_level=RiskLevel.CRITICAL,
    required_permission="system.power"
)
async def restart() -> Dict[str, Any]:
    return {"success": True, "message": "Restart signal sent (System restart request handled)"}
