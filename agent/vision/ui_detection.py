from typing import Dict, Any, Optional

class UIDetector:
    async def find_element(self, element_name: str, screenshot_path: str) -> Optional[Dict[str, Any]]:
        return {"name": element_name, "x": 500, "y": 300, "confidence": 0.95}

ui_detector = UIDetector()
