import pytest
from agent.browser import MockBrowserDriver, dom_parser

@pytest.mark.asyncio
async def test_browser_driver_navigation():
    driver = MockBrowserDriver()
    res = await driver.navigate("https://react.dev")
    assert res["success"] is True
    assert "react.dev" in driver.current_url

@pytest.mark.asyncio
async def test_browser_driver_dom_parsing():
    driver = MockBrowserDriver()
    await driver.navigate("https://react.dev")
    content = await driver.get_page_content()
    assert "url" in content
    assert "interactive_elements" in content
    assert len(content["interactive_elements"]) > 0

@pytest.mark.asyncio
async def test_browser_driver_click_and_type():
    driver = MockBrowserDriver()
    await driver.navigate("https://google.com")
    
    typed = await driver.type_text("#search", "React documentation", press_enter=True)
    assert typed["success"] is True
    assert "search" in typed["current_url"]

    clicked = await driver.click(text="Installation")
    assert clicked["success"] is True
