"""
Manual test of the working app to verify functionality
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

SCREENSHOT_DIR = Path("manual_test_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

async def test_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        print("Loading app...")
        await page.goto("http://localhost:8503")
        await page.wait_for_timeout(5000)  # Wait for app to fully load
        
        # Take screenshot of loaded page
        await page.screenshot(path=SCREENSHOT_DIR / "01_loaded.png", full_page=True)
        print("✓ App loaded")
        
        # Check page content
        content = await page.content()
        print(f"Page title contains 'AI': {'AI' in content}")
        print(f"Page has sidebar: {'sidebar' in content.lower()}")
        print(f"Page has input fields: {'input' in content.lower()}")
        
        # Look for specific elements
        headers = await page.locator("h1, h2, h3").all_text_contents()
        print(f"Headers found: {headers[:5] if headers else 'None'}")
        
        buttons = await page.locator("button").all()
        print(f"Buttons found: {len(buttons)}")
        
        inputs = await page.locator("input").all()
        print(f"Input fields found: {len(inputs)}")
        
        await browser.close()

asyncio.run(test_app())