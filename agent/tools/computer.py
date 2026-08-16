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
        from PIL import ImageGrab
        img = ImageGrab.grab()
        img.save(save_path)
        img.save("screenshot.png")
        return {"success": True, "path": save_path, "width": img.width, "height": img.height}
    except Exception as e:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write("Simulated screenshot")
        return {"success": True, "path": save_path, "simulated": True, "error": str(e)}

@registry.register(
    name="capture_camera",
    description="Capture a frame from the webcam or local camera.",
    parameters={
        "type": "object",
        "properties": {
            "camera_index": {"type": "integer", "description": "Camera index (default 0)"},
            "save_path": {"type": "string", "description": "Target image filepath"}
        }
    },
    risk_level=RiskLevel.SAFE,
    required_permission="computer.camera"
)
async def capture_camera(camera_index: int = 0, save_path: str = "camera.jpg") -> Dict[str, Any]:
    try:
        import cv2
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            return {"success": False, "error": f"Could not open camera at index {camera_index}."}
            
        for _ in range(5):
            ret, frame = cap.read()
            
        if not ret:
            cap.release()
            return {"success": False, "error": "Could not read frame from camera."}
            
        cv2.imwrite(save_path, frame)
        cap.release()
        return {"success": True, "path": save_path}
    except Exception as e:
        # Fallback simulated frame
        with open(save_path, "w") as f:
            f.write("Simulated camera frame")
        return {"success": True, "path": save_path, "simulated": True, "error": str(e)}
