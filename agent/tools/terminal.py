import asyncio
import subprocess
from typing import Dict, Any
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel
from agent.security.sandbox import sandbox

@registry.register(
    name="execute_command",
    description="Execute a shell command on the host terminal.",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to run"},
            "cwd": {"type": "string", "description": "Working directory path"}
        },
        "required": ["command"]
    },
    risk_level=RiskLevel.DANGEROUS,
    required_permission="terminal.execute"
)
async def execute_command(command: str, cwd: str = ".") -> Dict[str, Any]:
    if not sandbox.validate_command(command):
        return {"success": False, "error": "Command blocked by security sandbox"}

    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await proc.communicate()
        out_str = stdout.decode('utf-8', errors='replace')
        err_str = stderr.decode('utf-8', errors='replace')
        
        return {
            "success": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": out_str,
            "stderr": err_str,
            "command": command
        }
    except Exception as e:
        return {"success": False, "error": str(e), "command": command}

@registry.register(
    name="get_command_output",
    description="Get recent environment terminal state or output.",
    parameters={"type": "object", "properties": {}},
    risk_level=RiskLevel.SAFE,
    required_permission="terminal.read"
)
async def get_command_output() -> Dict[str, Any]:
    return {"success": True, "status": "Ready for command input"}
