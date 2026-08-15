import re
from typing import Dict, Any, List

class DOMParser:
    @staticmethod
    def extract_interactive_elements(html_text: str) -> List[Dict[str, Any]]:
        """Extract links, buttons, and inputs from HTML/text."""
        elements = []
        
        # Extract inputs
        inputs = re.findall(r'<input[^>]*>', html_text, re.IGNORECASE)
        for inp in inputs[:10]:
            name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
            placeholder_match = re.search(r'placeholder=["\']([^"\']+)["\']', inp)
            id_match = re.search(r'id=["\']([^"\']+)["\']', inp)
            elements.append({
                "type": "input",
                "id": id_match.group(1) if id_match else "",
                "name": name_match.group(1) if name_match else "",
                "placeholder": placeholder_match.group(1) if placeholder_match else "input"
            })

        # Extract buttons & links
        buttons = re.findall(r'<button[^>]*>(.*?)</button>', html_text, re.IGNORECASE | re.DOTALL)
        for btn in buttons[:10]:
            clean_btn = re.sub(r'<[^>]+>', '', btn).strip()
            if clean_btn:
                elements.append({"type": "button", "text": clean_btn})

        links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html_text, re.IGNORECASE | re.DOTALL)
        for href, label in links[:15]:
            clean_label = re.sub(r'<[^>]+>', '', label).strip()
            if clean_label and not href.startswith("javascript:"):
                elements.append({"type": "link", "text": clean_label, "href": href})

        if not elements:
            # Fallback simulated interactive elements
            elements = [
                {"type": "input", "id": "search-box", "placeholder": "Search docs..."},
                {"type": "button", "text": "Quick Start", "selector": "#quick-start-btn"},
                {"type": "link", "text": "Installation", "href": "/learn/installation"}
            ]

        return elements

dom_parser = DOMParser()
