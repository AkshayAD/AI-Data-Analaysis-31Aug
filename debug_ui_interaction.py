#!/usr/bin/env python3
"""
Debug UI interaction to understand why API key input is not working
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def debug_api_key_input():
    """Debug the API key input functionality"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to app
        print("🔍 Navigating to app...")
        await page.goto("http://localhost:8503")
        await page.wait_for_load_state("networkidle")
        
        # Take screenshot of initial state
        await page.screenshot(path="debug_01_initial.png")
        print("📸 Screenshot 1: Initial state")
        
        # Check for API key section
        print("\n🔍 Looking for API key elements...")
        
        # Check if override checkbox exists and is clickable
        override_checkbox = page.locator('input[type="checkbox"]').filter(has_text="Override with manual key")
        if await override_checkbox.count() > 0:
            print("✅ Override checkbox found")
            print(f"   Visible: {await override_checkbox.is_visible()}")
            print(f"   Enabled: {await override_checkbox.is_enabled()}")
            
            # Try to check the override box
            if await override_checkbox.is_enabled():
                await override_checkbox.check()
                await page.wait_for_timeout(1000)
                print("✅ Override checkbox checked")
                
                # Take screenshot after checking override
                await page.screenshot(path="debug_02_override_checked.png")
                print("📸 Screenshot 2: Override checked")
                
        else:
            print("❌ Override checkbox not found")
        
        # Look for the API key input field
        api_key_inputs = page.locator('input[type="password"]')
        input_count = await api_key_inputs.count()
        print(f"\n🔍 Found {input_count} password input fields")
        
        for i in range(input_count):
            input_field = api_key_inputs.nth(i)
            print(f"   Input {i+1}:")
            print(f"     Visible: {await input_field.is_visible()}")
            print(f"     Enabled: {await input_field.is_enabled()}")
            print(f"     Placeholder: {await input_field.get_attribute('placeholder')}")
            
            # Try to interact with enabled inputs
            if await input_field.is_enabled() and await input_field.is_visible():
                try:
                    await input_field.click()
                    await input_field.fill("test_api_key_123")
                    print(f"     ✅ Successfully filled input {i+1}")
                    
                    # Take screenshot after filling
                    await page.screenshot(path=f"debug_03_input_{i+1}_filled.png")
                    print(f"📸 Screenshot 3: Input {i+1} filled")
                    break
                    
                except Exception as e:
                    print(f"     ❌ Failed to fill input {i+1}: {e}")
        
        # Look for text inputs as well
        text_inputs = page.locator('input[type="text"]')
        text_count = await text_inputs.count()
        print(f"\n🔍 Found {text_count} text input fields")
        
        # Check for any input that might contain "api" or "key" in attributes
        all_inputs = page.locator('input')
        all_count = await all_inputs.count()
        print(f"\n🔍 Checking all {all_count} input elements...")
        
        for i in range(all_count):
            input_elem = all_inputs.nth(i)
            input_type = await input_elem.get_attribute('type') or 'text'
            placeholder = await input_elem.get_attribute('placeholder') or ''
            data_testid = await input_elem.get_attribute('data-testid') or ''
            
            if any(keyword in (placeholder + data_testid).lower() for keyword in ['api', 'key', 'gemini']):
                print(f"   Input {i+1} (type={input_type}):")
                print(f"     Placeholder: {placeholder}")
                print(f"     Data-testid: {data_testid}")
                print(f"     Visible: {await input_elem.is_visible()}")
                print(f"     Enabled: {await input_elem.is_enabled()}")
        
        # Look for Test Connection button
        test_buttons = page.locator('button').filter(has_text="Test Connection")
        if await test_buttons.count() > 0:
            button = test_buttons.first
            print(f"\n✅ Test Connection button found")
            print(f"   Visible: {await button.is_visible()}")
            print(f"   Enabled: {await button.is_enabled()}")
        else:
            print("\n❌ Test Connection button not found")
        
        # Final screenshot
        await page.screenshot(path="debug_04_final.png")
        print("📸 Screenshot 4: Final state")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_api_key_input())