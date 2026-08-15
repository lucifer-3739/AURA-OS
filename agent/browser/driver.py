import os
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, List, Optional
from agent.browser.base import BrowserDriver
from agent.browser.dom_parser import dom_parser

class MockBrowserDriver(BrowserDriver):
    def __init__(self):
        self.current_url: str = "about:blank"
        self.current_title: str = "New Tab"
        self.page_html: str = "<html><body><h1>AURA OS Browser</h1></body></html>"
        self.history: List[str] = []
        self.is_closed: bool = False

    async def navigate(self, url: str) -> Dict[str, Any]:
        if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("about:"):
            url = "https://" + url
        
        self.current_url = url
        self.history.append(url)
        self.is_closed = False

        # Attempt basic HTTP fetch to get real page HTML if online
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'AURA-OS-Browser/1.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                raw_bytes = resp.read(50000)
                self.page_html = raw_bytes.decode('utf-8', errors='ignore')
                # Extract title
                import re
                t_match = re.search(r'<title>(.*?)</title>', self.page_html, re.IGNORECASE)
                self.current_title = t_match.group(1) if t_match else url
        except Exception:
            # Fallback simulated page
            domain = urllib.parse.urlparse(url).netloc or url
            self.current_title = f"{domain.capitalize()} — Page"
            self.page_html = f"<html><body><h1>{self.current_title}</h1><input id='search' placeholder='Search...' /><button>Submit</button></body></html>"

        return {
            "success": True,
            "url": self.current_url,
            "title": self.current_title,
            "status_code": 200
        }

    async def click(self, selector: str = "", text: str = "") -> Dict[str, Any]:
        if self.is_closed:
            return {"success": False, "error": "Browser session closed"}
        
        target = selector or text or "element"
        # Simulate navigation or click action
        if "install" in target.lower():
            self.current_url += "#installation"
            self.current_title += " - Installation"

        return {
            "success": True,
            "clicked": target,
            "current_url": self.current_url,
            "current_title": self.current_title
        }

    async def type_text(self, selector: str, text: str, press_enter: bool = True) -> Dict[str, Any]:
        if self.is_closed:
            return {"success": False, "error": "Browser session closed"}

        if press_enter:
            self.current_url = f"https://www.google.com/search?q={urllib.parse.quote(text)}"
            self.current_title = f"Search: {text}"

        return {
            "success": True,
            "selector": selector,
            "typed": text,
            "press_enter": press_enter,
            "current_url": self.current_url
        }

    async def get_page_content(self, max_length: int = 5000) -> Dict[str, Any]:
        elements = dom_parser.extract_interactive_elements(self.page_html)
        import re
        clean_text = re.sub(r'<[^>]+>', ' ', self.page_html)
        clean_text = ' '.join(clean_text.split())[:max_length]
        
        return {
            "url": self.current_url,
            "title": self.current_title,
            "content": clean_text,
            "interactive_elements": elements
        }

    async def extract_data(self, query_selector: str) -> List[Dict[str, Any]]:
        return [
            {"selector": query_selector, "label": "Sample Entry 1", "value": "100"},
            {"selector": query_selector, "label": "Sample Entry 2", "value": "200"}
        ]

    async def download(self, url: str, destination: str) -> Dict[str, Any]:
        dst = Path(destination).resolve()
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(url, dst)
            return {"success": True, "url": url, "destination": str(dst), "bytes": dst.stat().st_size}
        except Exception as e:
            with open(dst, "w") as f:
                f.write(f"Simulated download from {url}")
            return {"success": True, "url": url, "destination": str(dst), "bytes": 50, "simulated": True}

    async def close(self):
        self.is_closed = True
        self.current_url = "about:blank"
        self.current_title = "Closed Session"
        return {"success": True}

class HeadlessBrowserDriver(BrowserDriver):
    """Playwright / Selenium driver framework placeholder."""
    def __init__(self):
        self.mock_fallback = MockBrowserDriver()

    async def navigate(self, url: str) -> Dict[str, Any]:
        return await self.mock_fallback.navigate(url)

    async def click(self, selector: str = "", text: str = "") -> Dict[str, Any]:
        return await self.mock_fallback.click(selector, text)

    async def type_text(self, selector: str, text: str, press_enter: bool = True) -> Dict[str, Any]:
        return await self.mock_fallback.type_text(selector, text, press_enter)

    async def get_page_content(self, max_length: int = 5000) -> Dict[str, Any]:
        return await self.mock_fallback.get_page_content(max_length)

    async def extract_data(self, query_selector: str) -> List[Dict[str, Any]]:
        return await self.mock_fallback.extract_data(query_selector)

    async def download(self, url: str, destination: str) -> Dict[str, Any]:
        return await self.mock_fallback.download(url, destination)

    async def close(self):
        return await self.mock_fallback.close()

browser_driver = MockBrowserDriver()
