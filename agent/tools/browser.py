import webbrowser
import urllib.request
from pathlib import Path
from typing import Dict, Any
from agent.tools.registry import registry
from agent.security.permissions import RiskLevel

# 1. open_url
@registry.register(
    name="open_url",
    description="Open a specified web URL in default web browser.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to open, e.g. https://google.com"}
        },
        "required": ["url"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.open"
)
async def open_url(url: str) -> Dict[str, Any]:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    webbrowser.open(url)
    return {"success": True, "url": url}

# 2. search_web
@registry.register(
    name="search_web",
    description="Search the web for a given query in default browser.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"}
        },
        "required": ["query"]
    },
    risk_level=RiskLevel.SAFE,
    required_permission="browser.search"
)
async def search_web(query: str) -> Dict[str, Any]:
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    webbrowser.open(url)
    return {"success": True, "query": query, "url": url}

# 3. download_file
@registry.register(
    name="download_file",
    description="Download a file from a public URL to destination path.",
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Download source URL"},
            "destination": {"type": "string", "description": "Local target file path"}
        },
        "required": ["url", "destination"]
    },
    risk_level=RiskLevel.MODERATE,
    required_permission="browser.download",
    verify_func=lambda result, **kwargs: Path(kwargs.get("destination", "")).exists()
)
async def download_file(url: str, destination: str) -> Dict[str, Any]:
    dst = Path(destination).resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dst)
    return {"success": True, "url": url, "destination": str(dst)}
