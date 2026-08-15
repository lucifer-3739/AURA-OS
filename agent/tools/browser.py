import os
import webbrowser
import urllib.request
from pathlib import Path
from typing import Dict, Any, List
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel
from agent.browser import browser_driver

# 1. open_url
@registry.register(
    name="open_url",
    description="Navigate the browser session to a specified web URL.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Target web URL, e.g. https://react.dev"}
        },
        "required": ["url"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.open",
    verify_func=lambda result, **kwargs: result.get("success", False)
)
async def open_url(url: str) -> Dict[str, Any]:
    res = await browser_driver.navigate(url)
    # Also open in system default browser for visual user visibility
    try:
        webbrowser.open(res.get("url", url))
    except Exception:
        pass
    return res

# 2. search_web
@registry.register(
    name="search_web",
    description="Search the web for a given query and open results page.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query text"}
        },
        "required": ["query"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.search"
)
async def search_web(query: str) -> Dict[str, Any]:
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    res = await browser_driver.navigate(url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    res["query"] = query
    return res

# 3. click_element
@registry.register(
    name="click_element",
    description="Click a button, link, or DOM element matching selector or text label.",
    parameters={
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "CSS selector e.g. #submit-btn"},
            "text": {"type": "string", "description": "Text label e.g. 'Get Started'"}
        }
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="browser.click",
    verify_func=lambda result, **kwargs: result.get("success", False)
)
async def click_element(selector: str = "", text: str = "") -> Dict[str, Any]:
    return await browser_driver.click(selector, text)

# 4. type_text
@registry.register(
    name="type_text",
    description="Type text into a web input field or form.",
    parameters={
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "Target input CSS selector or id"},
            "text": {"type": "string", "description": "Text content to enter"},
            "press_enter": {"type": "boolean", "description": "Press enter after typing"}
        },
        "required": ["selector", "text"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="browser.type",
    verify_func=lambda result, **kwargs: result.get("success", False)
)
async def type_text(selector: str, text: str, press_enter: bool = True) -> Dict[str, Any]:
    return await browser_driver.type_text(selector, text, press_enter)

# 5. read_page
@registry.register(
    name="read_page",
    description="Extract clean text content, title, and interactive DOM elements from current page.",
    parameters={
        "type": "object",
        "properties": {
            "max_length": {"type": "integer", "description": "Maximum text characters to return"}
        }
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.read"
)
async def read_page(max_length: int = 5000) -> Dict[str, Any]:
    content = await browser_driver.get_page_content(max_length)
    content["success"] = True
    return content

# 6. extract_data
@registry.register(
    name="extract_data",
    description="Extract structured table or list data matching CSS selector.",
    parameters={
        "type": "object",
        "properties": {
            "selector": {"type": "string", "description": "Target list/table CSS selector"}
        },
        "required": ["selector"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.read"
)
async def extract_data(selector: str) -> Dict[str, Any]:
    data = await browser_driver.extract_data(selector)
    return {"success": True, "selector": selector, "data": data}

# 7. download_file
@registry.register(
    name="download_file",
    description="Download a file from URL to destination path.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "File download URL"},
            "destination": {"type": "string", "description": "Target local destination path"}
        },
        "required": ["url", "destination"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="browser.download",
    verify_func=lambda result, **kwargs: os.path.exists(kwargs.get("destination", ""))
)
async def download_file(url: str, destination: str) -> Dict[str, Any]:
    return await browser_driver.download(url, destination)

# 8. close_browser
@registry.register(
    name="close_browser",
    description="Close active browser session.",
    parameters={"type": "object", "properties": {}},
    risk_level=RiskLevel.SAFE,
    required_permission="browser.close"
)
async def close_browser() -> Dict[str, Any]:
    return await browser_driver.close()
