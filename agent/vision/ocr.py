from typing import Dict, Any, List

class OCRProcessor:
    async def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        return [{"text": "File Edit Selection View", "bbox": [10, 10, 200, 30]}]

ocr_processor = OCRProcessor()
