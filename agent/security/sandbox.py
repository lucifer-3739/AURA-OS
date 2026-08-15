"""
Sandbox abstraction for future containerized or restricted environment execution.
"""
from typing import Dict, Any

class ExecutionSandbox:
    def validate_command(self, command: str) -> bool:
        """Basic validation to prevent catastrophic raw system commands if needed."""
        forbidden = ["rm -rf /", "format c:", "del /f /s /q c:\\"]
        cmd_lower = command.lower().strip()
        for f in forbidden:
            if f in cmd_lower:
                return False
        return True

sandbox = ExecutionSandbox()
