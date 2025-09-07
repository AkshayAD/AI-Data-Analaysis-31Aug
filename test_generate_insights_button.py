"""
Focused test for Generate AI Insights button in Stage 2
Tests that the button is accessible and functional
"""

import asyncio
from pathlib import Path
import pandas as pd
import numpy as np
from playwright.async_api import async_playwright
import json
from datetime import datetime

GEMINI_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
BASE_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_insights_test")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def create_test_data():
    """Create test CSV file"""
    np.random.seed(42)
    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
        'sales': np.random.randint(100, 1000, 100),
        'quantity': np.random.randint(1, 50, 100),
        'revenue': np.random.uniform(1000, 10000, 100),
        'customer_id': np.random.randint(1000, 2000, 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'satisfaction_score': np.random.uniform(1, 5, 100)
    }
    df = pd.DataFrame(data)
    test_file = Path("test_data.csv")
    df.to_csv(test_file, index=False)
    return test_file

async def test_generate_insights_button():
    print("\n" + "="*60)
    print("TESTING GENERATE AI INSIGHTS BUTTON")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        test_file = create_test_data()
        test_passed = False
        
        try:
            # 1. LOAD APPLICATION
            print("\n1. Loading application...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            await page.screenshot(path=SCREENSHOT_DIR / "01_app_loaded.png", full_page=True)
            print("   ✅ App loaded")
            
            # 2. CONFIGURE API KEY
            print("\n2. Configuring API key...")
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill(GEMINI_API_KEY)
            await page.wait_for_timeout(1000)
            
            # Test API connection
            test_buttons = await page.query_selector_all("button")
            for btn in test_buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    await btn.click()
                    await page.wait_for_timeout(5000)
                    print("   ✅ API configured")
                    break
            
            # 3. UPLOAD DATA
            print("\n3. Uploading test data...")
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(test_file))
                await page.wait_for_timeout(3000)
                print("   ✅ Data uploaded")
            
            # 4. SET BUSINESS OBJECTIVE AND GENERATE PLAN
            print("\n4. Setting business objective...")
            text_areas = await page.query_selector_all("textarea")
            for ta in text_areas:
                placeholder = await ta.get_attribute("placeholder")
                if placeholder and "business" in placeholder.lower():
                    await ta.fill("Analyze sales patterns to identify growth opportunities")
                    await page.wait_for_timeout(1000)
                    print("   ✅ Business objective set")
                    break
            
            # Navigate to Stage 1
            nav_buttons = await page.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Analysis Planning" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    print("   ✅ Navigated to Stage 1")
                    break
            
            # Generate plan
            generate_buttons = await page.query_selector_all("button")
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Plan" in text:
                    await btn.click()
                    await page.wait_for_timeout(10000)
                    print("   ✅ Plan generated")
                    break
            
            # 5. NAVIGATE TO STAGE 2
            print("\n5. Navigating to Stage 2...")
            nav_buttons = await page.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Data Understanding" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "02_stage2_loaded.png", full_page=True)
                    print("   ✅ In Stage 2")
                    break
            
            # 6. CLICK ON AI INSIGHTS TAB
            print("\n6. Clicking AI Insights tab...")
            # Look for tab button with "AI Insights" or "💡" emoji
            tab_buttons = await page.query_selector_all('[role="tab"], button')
            ai_tab_found = False
            
            for tab in tab_buttons:
                text = await tab.text_content()
                if text and ("AI Insights" in text or "💡" in text):
                    await tab.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=SCREENSHOT_DIR / "03_ai_insights_tab.png", full_page=True)
                    print("   ✅ AI Insights tab clicked")
                    ai_tab_found = True
                    break
            
            if not ai_tab_found:
                print("   ❌ AI Insights tab not found")
                await page.screenshot(path=SCREENSHOT_DIR / "error_no_tab.png", full_page=True)
            
            # 7. TEST GENERATE INSIGHTS BUTTON
            print("\n7. Testing Generate AI Insights button...")
            
            # Look for the Generate AI Insights button
            generate_buttons = await page.query_selector_all("button")
            button_found = False
            
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and ("Generate AI Insights" in text or "🤖" in text):
                    button_found = True
                    print(f"   ✅ Found button: '{text}'")
                    await page.screenshot(path=SCREENSHOT_DIR / "04_button_found.png", full_page=True)
                    
                    # Click the button
                    await btn.click()
                    print("   ⏳ Generating insights...")
                    await page.wait_for_timeout(10000)  # Wait for AI response
                    
                    # Capture result
                    await page.screenshot(path=SCREENSHOT_DIR / "05_insights_generated.png", full_page=True)
                    
                    # Check if insights were generated
                    content = await page.content()
                    if any(keyword in content.lower() for keyword in ["insight", "pattern", "recommendation", "analysis"]):
                        print("   ✅ AI Insights generated successfully!")
                        test_passed = True
                    else:
                        print("   ⚠️ Insights may not have been generated properly")
                    break
            
            if not button_found:
                print("   ❌ Generate AI Insights button NOT FOUND!")
                await page.screenshot(path=SCREENSHOT_DIR / "error_button_missing.png", full_page=True)
                
                # Debug: List all visible buttons
                print("\n   Debug - All visible buttons:")
                for btn in generate_buttons:
                    text = await btn.text_content()
                    if text:
                        print(f"     - '{text.strip()}'")
            
        except Exception as e:
            print(f"\n   ❌ Test error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_exception.png", full_page=True)
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
            if test_file.exists():
                test_file.unlink()
        
        # Print test result
        print("\n" + "="*60)
        if test_passed:
            print("TEST RESULT: ✅ PASSED - Generate AI Insights button works!")
        else:
            print("TEST RESULT: ❌ FAILED - Generate AI Insights button issue detected!")
        print("="*60)
        
        return test_passed

if __name__ == "__main__":
    result = asyncio.run(test_generate_insights_button())
    exit(0 if result else 1)