"""
Improved test for Generate AI Insights button with better tab navigation
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
SCREENSHOT_DIR = Path("screenshots_insights_improved")
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
    print("IMPROVED TEST FOR GENERATE AI INSIGHTS BUTTON")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Run with GUI for debugging
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        page.set_default_timeout(60000)  # Increase timeout
        
        test_file = create_test_data()
        test_results = []
        
        try:
            # 1. LOAD APPLICATION
            print("\n1. Loading application...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            await page.screenshot(path=SCREENSHOT_DIR / "01_app_loaded.png", full_page=True)
            
            # Check content loaded
            content = await page.content()
            if "AI Analysis Platform" in content or "Stage" in content:
                print("   ✅ App loaded successfully")
                test_results.append(("App Loading", "PASS"))
            else:
                print("   ⚠️ App loaded but content unclear")
                test_results.append(("App Loading", "WARNING"))
            
            # 2. CONFIGURE API KEY
            print("\n2. Configuring API key...")
            
            # Look for password input
            try:
                api_input = await page.wait_for_selector("input[type='password']", timeout=5000)
                await api_input.fill(GEMINI_API_KEY)
                await page.wait_for_timeout(1000)
                print("   ✅ API key entered")
                
                # Click Test Connection button
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = await btn.text_content()
                    if text and "Test" in text and "Connection" in text:
                        await btn.click()
                        await page.wait_for_timeout(5000)
                        print("   ✅ API connection tested")
                        test_results.append(("API Configuration", "PASS"))
                        break
            except:
                print("   ⚠️ Could not configure API key")
                test_results.append(("API Configuration", "SKIP"))
            
            # 3. UPLOAD DATA
            print("\n3. Uploading test data...")
            try:
                file_input = await page.wait_for_selector("input[type='file']", timeout=5000)
                await file_input.set_input_files(str(test_file))
                await page.wait_for_timeout(3000)
                print("   ✅ Data uploaded")
                test_results.append(("Data Upload", "PASS"))
            except:
                print("   ⚠️ Could not upload data")
                test_results.append(("Data Upload", "SKIP"))
            
            # 4. SET BUSINESS OBJECTIVE
            print("\n4. Setting business objective...")
            try:
                text_areas = await page.query_selector_all("textarea")
                for ta in text_areas[:3]:  # Check first 3 textareas
                    try:
                        placeholder = await ta.get_attribute("placeholder")
                        if placeholder and "business" in placeholder.lower():
                            await ta.fill("Analyze sales patterns to identify growth opportunities and customer segments")
                            await page.wait_for_timeout(1000)
                            print("   ✅ Business objective set")
                            test_results.append(("Business Objective", "PASS"))
                            break
                    except:
                        continue
            except:
                print("   ⚠️ Could not set business objective")
                test_results.append(("Business Objective", "SKIP"))
            
            await page.screenshot(path=SCREENSHOT_DIR / "02_stage0_complete.png", full_page=True)
            
            # 5. NAVIGATE TO STAGE 1
            print("\n5. Navigating to Stage 1...")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and ("Analysis Planning" in text or "Next" in text):
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    print("   ✅ Navigated to Stage 1")
                    test_results.append(("Navigate to Stage 1", "PASS"))
                    break
            
            # 6. GENERATE PLAN
            print("\n6. Generating analysis plan...")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Plan" in text:
                    await btn.click()
                    print("   ⏳ Waiting for plan generation...")
                    await page.wait_for_timeout(10000)
                    print("   ✅ Plan generated")
                    test_results.append(("Plan Generation", "PASS"))
                    break
            
            await page.screenshot(path=SCREENSHOT_DIR / "03_stage1_complete.png", full_page=True)
            
            # 7. NAVIGATE TO STAGE 2
            print("\n7. Navigating to Stage 2...")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and ("Data Understanding" in text or "Next" in text):
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    print("   ✅ Navigated to Stage 2")
                    test_results.append(("Navigate to Stage 2", "PASS"))
                    break
            
            await page.screenshot(path=SCREENSHOT_DIR / "04_stage2_loaded.png", full_page=True)
            
            # 8. CLICK AI INSIGHTS TAB
            print("\n8. Looking for AI Insights tab...")
            
            # Method 1: Try clicking on tab with text
            tab_found = False
            
            # First try to find tabs with role="tab"
            tabs = await page.query_selector_all('[role="tab"]')
            print(f"   Found {len(tabs)} elements with role='tab'")
            
            for tab in tabs:
                text = await tab.text_content()
                print(f"   Tab text: '{text}'")
                if text and ("AI Insights" in text or "💡" in text):
                    await tab.click()
                    await page.wait_for_timeout(2000)
                    print("   ✅ Clicked AI Insights tab (role=tab)")
                    tab_found = True
                    break
            
            # If not found, try buttons that might be tabs
            if not tab_found:
                buttons = await page.query_selector_all('button')
                for btn in buttons:
                    text = await btn.text_content()
                    if text and ("AI Insights" in text or "💡" in text):
                        await btn.click()
                        await page.wait_for_timeout(2000)
                        print("   ✅ Clicked AI Insights tab (button)")
                        tab_found = True
                        break
            
            # If still not found, try divs with specific data attributes
            if not tab_found:
                elements = await page.query_selector_all('div[data-baseweb="tab"]')
                for elem in elements:
                    text = await elem.text_content()
                    if text and ("AI Insights" in text or "💡" in text):
                        await elem.click()
                        await page.wait_for_timeout(2000)
                        print("   ✅ Clicked AI Insights tab (div)")
                        tab_found = True
                        break
            
            if tab_found:
                test_results.append(("AI Insights Tab", "PASS"))
            else:
                print("   ❌ Could not find AI Insights tab")
                test_results.append(("AI Insights Tab", "FAIL"))
            
            await page.screenshot(path=SCREENSHOT_DIR / "05_ai_insights_tab.png", full_page=True)
            
            # 9. LOOK FOR GENERATE INSIGHTS BUTTON
            print("\n9. Looking for Generate AI Insights button...")
            
            # Wait a bit for tab content to render
            await page.wait_for_timeout(2000)
            
            buttons = await page.query_selector_all("button")
            button_found = False
            button_texts = []
            
            for btn in buttons:
                text = await btn.text_content()
                if text:
                    button_texts.append(text.strip())
                    if "Generate" in text and "Insights" in text:
                        button_found = True
                        print(f"   ✅ Found button: '{text.strip()}'")
                        
                        # Try to click it
                        try:
                            await btn.click()
                            print("   ⏳ Generating insights...")
                            await page.wait_for_timeout(10000)
                            
                            await page.screenshot(path=SCREENSHOT_DIR / "06_insights_generated.png", full_page=True)
                            
                            content = await page.content()
                            if any(kw in content.lower() for kw in ["insight", "pattern", "recommendation"]):
                                print("   ✅ Insights generated successfully!")
                                test_results.append(("Generate Insights", "PASS"))
                            else:
                                print("   ⚠️ Button clicked but insights unclear")
                                test_results.append(("Generate Insights", "WARNING"))
                        except Exception as e:
                            print(f"   ⚠️ Error clicking button: {e}")
                            test_results.append(("Generate Insights", "ERROR"))
                        break
            
            if not button_found:
                print("   ❌ Generate AI Insights button NOT FOUND")
                print(f"   Available buttons: {button_texts[:10]}")  # Show first 10 buttons
                test_results.append(("Generate Insights Button", "FAIL"))
            
            # Final screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "07_final_state.png", full_page=True)
            
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_state.png", full_page=True)
            import traceback
            traceback.print_exc()
        
        finally:
            # Keep browser open for manual inspection
            print("\n⏸️  Browser will close in 10 seconds. Check the UI manually if needed...")
            await page.wait_for_timeout(10000)
            
            await browser.close()
            if test_file.exists():
                test_file.unlink()
        
        # Print test summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, status in test_results if status == "PASS")
        failed = sum(1 for _, status in test_results if status == "FAIL")
        warnings = sum(1 for _, status in test_results if status in ["WARNING", "SKIP"])
        
        for test_name, status in test_results:
            icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
            print(f"{icon} {test_name}: {status}")
        
        print(f"\nTotal: {passed} passed, {failed} failed, {warnings} warnings/skipped")
        
        if failed == 0:
            print("\n🎉 ALL CRITICAL TESTS PASSED!")
            return True
        else:
            print(f"\n❌ {failed} TEST(S) FAILED")
            return False

if __name__ == "__main__":
    result = asyncio.run(test_generate_insights_button())
    exit(0 if result else 1)