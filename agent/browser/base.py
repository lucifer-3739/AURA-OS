from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BrowserDriver(ABC):
    @abstractmethod
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate browser session to target URL."""
        pass

    @abstractmethod
    async def click(self, selector: str = "", text: str = "") -> Dict[str, Any]:
        """Click element by CSS selector or text label."""
        pass

    @abstractmethod
    async def type_text(self, selector: str, text: str, press_enter: bool = True) -> Dict[str, Any]:
        """Type text into form input matching selector."""
        pass

    @abstractmethod
    async def get_page_content(self, max_length: int = 5000) -> Dict[str, Any]:
        """Return active page content, title, URL, and interactive elements."""
        pass

    @abstractmethod
    async def extract_data(self, query_selector: str) -> List[Dict[str, Any]]:
        """Extract structured data matching selector."""
        pass

    @abstractmethod
    async def download(self, url: str, destination: str) -> Dict[str, Any]:
        """Download file from URL to local destination."""
        pass

    @abstractmethod
    async def close(self):
        """Close browser session."""
        pass
