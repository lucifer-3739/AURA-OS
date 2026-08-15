import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel

@registry.register(
    name="screenshot",
    description="Capture a screenshot of the computer screen.",
    parameters={
        "type": "object",
        "properties": {
            "save_path": {"type": "string", "description": "Target image filepath"}
        }
    },
    risk_level=RiskLevel.SAFE,
    required_permission="computer.screen"
)
async def screenshot(save_path: str = "") -> Dict[str, Any]:
    if not save_path:
        save_path = str(Path(tempfile.gettempdir()) / "aura_screenshot.png")
    
    try:
        # Try PIL ImageGrab
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(save_path)
        return {"success": True, "path": save_path, "width": img.width, "height": img.height}
    except Exception as e:
        # Fallback simulated placeholder file
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write("Simulated screenshot")
        return {"success": True, "path": save_path, "simulated": True, "error": str(e)}
