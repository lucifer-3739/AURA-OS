from typing import Dict, Any

class VisionAnalyzer:
    async def analyze_screen(self, image_path: str) -> Dict[str, Any]:
        return {
            "success": True,
            "detected_elements": [
                {"label": "VS Code Icon", "bbox": [100, 200, 50, 50]},
                {"label": "Chrome Window", "bbox": [0, 0, 1920, 1080]}
            ]
        }

vision_analyzer = VisionAnalyzer()
