import json
import urllib.request
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from agent.config import settings
from agent.tools import registry

class AIProvider(ABC):
    @abstractmethod
    async def generate_plan(self, request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

class MockAIProvider(AIProvider):
    async def generate_plan(self, request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        req_lower = request.lower().strip()

        # Handle specific common intent patterns for deterministic execution & testing
        if "open" in req_lower and ("vs code" in req_lower or "code" in req_lower):
            return [
                {
                    "id": 1,
                    "description": "Open Visual Studio Code",
                    "tool_name": "open_application",
                    "arguments": {"application": "code"},
                    "status": "pending"
                }
            ]
        elif "open" in req_lower and "chrome" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Open Google Chrome browser",
                    "tool_name": "open_application",
                    "arguments": {"application": "chrome"},
                    "status": "pending"
                }
            ]
        elif "create" in req_lower and "folder" in req_lower:
            folder_name = "Projects"
            if "called" in req_lower:
                parts = request.split("called")
                if len(parts) > 1:
                    folder_name = parts[1].strip().strip("'.\"")
            return [
                {
                    "id": 1,
                    "description": f"Create directory '{folder_name}'",
                    "tool_name": "create_folder",
                    "arguments": {"path": folder_name},
                    "status": "pending"
                }
            ]
        elif "delete" in req_lower or "remove" in req_lower:
            target = "Projects_Test"
            return [
                {
                    "id": 1,
                    "description": f"Delete path '{target}'",
                    "tool_name": "delete_file",
                    "arguments": {"path": target},
                    "status": "pending"
                }
            ]
        elif "search" in req_lower:
            query = request.replace("search", "").replace("for", "").strip() or "React documentation"
            return [
                {
                    "id": 1,
                    "description": f"Search web for '{query}'",
                    "tool_name": "search_web",
                    "arguments": {"query": query},
                    "status": "pending"
                }
            ]
        elif "system" in req_lower or "info" in req_lower or "stats" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Retrieve host system hardware information",
                    "tool_name": "system_information",
                    "arguments": {},
                    "status": "pending"
                }
            ]
        elif "click" in req_lower:
            target = request.replace("click", "").strip() or "Quick Start"
            return [
                {
                    "id": 1,
                    "description": f"Click element '{target}'",
                    "tool_name": "click_element",
                    "arguments": {"text": target},
                    "status": "pending"
                }
            ]
        elif "type" in req_lower:
            typed_text = request.replace("type", "").strip() or "React hooks"
            return [
                {
                    "id": 1,
                    "description": f"Type '{typed_text}' into search field",
                    "tool_name": "type_text",
                    "arguments": {"selector": "#search", "text": typed_text, "press_enter": True},
                    "status": "pending"
                }
            ]
        elif "read page" in req_lower or "extract text" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Read active browser page content",
                    "tool_name": "read_page",
                    "arguments": {"max_length": 5000},
                    "status": "pending"
                }
            ]
        elif "extract data" in req_lower or "extract table" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Extract structured data matching selector",
                    "tool_name": "extract_data",
                    "arguments": {"selector": ".data-table"},
                    "status": "pending"
                }
            ]
        elif "download" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Download documentation file",
                    "tool_name": "download_file",
                    "arguments": {"url": "https://example.com/docs.pdf", "destination": "Projects/docs.pdf"},
                    "status": "pending"
                }
            ]
        elif "close browser" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Close browser session",
                    "tool_name": "close_browser",
                    "arguments": {},
                    "status": "pending"
                }
            ]
        elif "screenshot" in req_lower:
            return [
                {
                    "id": 1,
                    "description": "Capture screen snapshot",
                    "tool_name": "screenshot",
                    "arguments": {},
                    "status": "pending"
                }
            ]

        # Generic fallback multi-step plan
        return [
            {
                "id": 1,
                "description": f"Execute action for user request: {request}",
                "tool_name": "system_information",
                "arguments": {},
                "status": "pending"
            }
        ]

class GeminiAIProvider(AIProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate_plan(self, request: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.api_key:
            # Fallback to mock provider if API key is not configured
            return await MockAIProvider().generate_plan(request, context)

        # Call Gemini REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
        tools_list = registry.list_tools()
        
        prompt = (
            f"You are the planner for AURA OS. The user request is: '{request}'.\n"
            f"Available tools schema: {json.dumps(tools_list)}\n"
            "Respond ONLY with a valid JSON array of step objects, like:\n"
            '[{"id": 1, "description": "...", "tool_name": "...", "arguments": {...}, "status": "pending"}]'
        )

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                text_resp = data['candidates'][0]['content']['parts'][0]['text']
                # Clean JSON code blocks if present
                clean_json = text_resp.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                
                steps = json.loads(clean_json.strip())
                return steps
        except Exception:
            # On network or parse error, fallback safely to mock plan
            return await MockAIProvider().generate_plan(request, context)

def get_ai_provider() -> AIProvider:
    if settings.ai_provider == "gemini" and settings.gemini_api_key:
        return GeminiAIProvider(settings.gemini_api_key)
    return MockAIProvider()

planner_provider = get_ai_provider()
