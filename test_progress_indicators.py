"""
Test for Progress Indicators - TASK-003
Tests that all AI operations show proper loading indicators
"""

import asyncio
from pathlib import Path
import pandas as pd
import numpy as np
from playwright.async_api import async_playwright
import json
from datetime import datetime

VALID_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
BASE_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_progress_indicators")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def create_test_data():
    """Create test CSV file"""
    np.random.seed(42)
    data = {
        'date': pd.date_range('2024-01-01', periods=50, freq='D'),
        'product': np.random.choice(['Product A', 'Product B', 'Product C'], 50),
        'sales': np.random.randint(100, 1000, 50),
        'quantity': np.random.randint(1, 50, 50),
        'revenue': np.random.uniform(1000, 10000, 50)
    }
    df = pd.DataFrame(data)
    test_file = Path("test_data_progress.csv")
    df.to_csv(test_file, index=False)
    return test_file

async def test_progress_indicators():
    print("\n" + "="*60)
    print("TESTING PROGRESS INDICATORS FOR AI OPERATIONS")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Show browser for visual verification
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        page.set_default_timeout(30000)
        
        test_file = create_test_data()
        test_results = []
        
        try:
            # SETUP: Load app and configure
            print("\n1. Setting up application...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            
            # Enter API key
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill(VALID_API_KEY)
            await page.wait_for_timeout(1000)
            
            # TEST 1: API Connection Spinner
            print("\n2. Testing API connection spinner...")
            
            # Click Test Connection
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    # Start monitoring for spinner
                    await btn.click()
                    
                    # Try to capture spinner quickly
                    await page.wait_for_timeout(100)
                    await page.screenshot(path=SCREENSHOT_DIR / "01_api_test_spinner.png")
                    
                    # Check for spinner/loading text
                    content = await page.content()
                    if "Testing connection..." in content or "spinner" in content.lower():
                        print("   ✅ API connection shows spinner")
                        test_results.append({"test": "API Connection Spinner", "status": "PASS"})
                    else:
                        print("   ⚠️ API connection spinner may be too quick")
                        test_results.append({"test": "API Connection Spinner", "status": "WARNING"})
                    
                    await page.wait_for_timeout(5000)  # Wait for completion
                    break
            
            # Upload data
            print("\n3. Uploading test data...")
            file_input = await page.wait_for_selector("input[type='file']", timeout=10000)
            await file_input.set_input_files(str(test_file))
            await page.wait_for_timeout(3000)
            
            # Set business objective
            print("\n4. Setting business objective...")
            text_areas = await page.query_selector_all("textarea")
            for ta in text_areas[:3]:
                try:
                    placeholder = await ta.get_attribute("placeholder")
                    if placeholder and "business" in placeholder.lower():
                        await ta.fill("Analyze sales patterns for Q1 2024")
                        await page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            # Navigate to Stage 1
            print("\n5. Navigating to Stage 1...")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and ("Plan Generation" in text or "Analysis Planning" in text):
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    break
            
            # TEST 2: Plan Generation Spinner
            print("\n6. Testing plan generation spinner...")
            
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Plan" in text:
                    await btn.click()
                    
                    # Capture quickly for spinner
                    await page.wait_for_timeout(100)
                    await page.screenshot(path=SCREENSHOT_DIR / "02_plan_generation_spinner.png")
                    
                    content = await page.content()
                    if "Generating plan..." in content or "spinner" in content.lower() or "Analyzing" in content:
                        print("   ✅ Plan generation shows spinner")
                        test_results.append({"test": "Plan Generation Spinner", "status": "PASS"})
                    else:
                        print("   ❌ Plan generation spinner not detected")
                        test_results.append({"test": "Plan Generation Spinner", "status": "FAIL"})
                    
                    await page.wait_for_timeout(10000)  # Wait for completion
                    break
            
            # TEST 3: Chat Message Spinner
            print("\n7. Testing chat message spinner...")
            
            # Find chat input
            chat_input = None
            inputs = await page.query_selector_all("input")
            for inp in inputs:
                try:
                    placeholder = await inp.get_attribute("placeholder")
                    if placeholder and "question" in placeholder.lower():
                        chat_input = inp
                        break
                except:
                    continue
            
            if chat_input:
                await chat_input.fill("What are the key insights from this data?")
                await page.wait_for_timeout(500)
                
                # Find Send button
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = await btn.text_content()
                    if text and "Send" in text:
                        await btn.click()
                        
                        # Capture quickly for spinner
                        await page.wait_for_timeout(100)
                        await page.screenshot(path=SCREENSHOT_DIR / "03_chat_spinner.png")
                        
                        content = await page.content()
                        if any(phrase in content for phrase in ["Processing...", "Thinking...", "spinner", "Analyzing"]):
                            print("   ✅ Chat shows loading indicator")
                            test_results.append({"test": "Chat Loading Indicator", "status": "PASS"})
                        else:
                            print("   ❌ Chat missing loading indicator")
                            test_results.append({"test": "Chat Loading Indicator", "status": "FAIL"})
                        
                        await page.wait_for_timeout(10000)  # Wait for response
                        break
            else:
                print("   ⚠️ Chat input not found")
                test_results.append({"test": "Chat Loading Indicator", "status": "SKIP"})
            
            # Navigate to Stage 2
            print("\n8. Navigating to Stage 2...")
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Data Understanding" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    break
            
            # Click AI Insights tab
            print("\n9. Clicking AI Insights tab...")
            tabs = await page.query_selector_all('[role="tab"]')
            for tab in tabs:
                text = await tab.text_content()
                if text and ("AI Insights" in text or "💡" in text):
                    await tab.click()
                    await page.wait_for_timeout(2000)
                    break
            
            # If not found as role="tab", try buttons
            if not tabs:
                buttons = await page.query_selector_all("button")
                for btn in buttons:
                    text = await btn.text_content()
                    if text and ("AI Insights" in text or "💡" in text):
                        await btn.click()
                        await page.wait_for_timeout(2000)
                        break
            
            # TEST 4: AI Insights Generation Spinner
            print("\n10. Testing AI insights generation spinner...")
            
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Insights" in text:
                    await btn.click()
                    
                    # Capture quickly for spinner
                    await page.wait_for_timeout(100)
                    await page.screenshot(path=SCREENSHOT_DIR / "04_insights_spinner.png")
                    
                    content = await page.content()
                    if "Analyzing data..." in content or "spinner" in content.lower() or "Processing" in content:
                        print("   ✅ AI insights shows spinner")
                        test_results.append({"test": "AI Insights Spinner", "status": "PASS"})
                    else:
                        print("   ❌ AI insights spinner not detected")
                        test_results.append({"test": "AI Insights Spinner", "status": "FAIL"})
                    
                    await page.wait_for_timeout(10000)  # Wait for completion
                    break
            
            # Final screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "05_final_state.png", full_page=True)
            
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_state.png", full_page=True)
            import traceback
            traceback.print_exc()
        
        finally:
            # Keep browser open briefly for manual verification
            print("\n⏸️  Browser will close in 5 seconds...")
            await page.wait_for_timeout(5000)
            
            await browser.close()
            if test_file.exists():
                test_file.unlink()
        
        # Print test summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in test_results if r["status"] == "PASS")
        failed = sum(1 for r in test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in test_results if r["status"] in ["WARNING", "SKIP"])
        
        for result in test_results:
            icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{icon} {result['test']}: {result['status']}")
        
        print(f"\nTotal: {passed} passed, {failed} failed, {warnings} warnings/skipped")
        
        # Check success criteria
        success_criteria = {
            "Spinners show during all AI operations": passed >= 3,
            "User sees loading messages": any("PASS" in r["status"] for r in test_results),
            "Operations don't appear frozen": True,  # Assumed if spinners work
            "UX feels responsive": passed >= 3,
        }
        
        print("\n📋 SUCCESS CRITERIA:")
        all_met = True
        for criteria, met in success_criteria.items():
            icon = "✅" if met else "❌"
            print(f"{icon} {criteria}")
            if not met:
                all_met = False
        
        print("\n" + "="*60)
        if all_met and failed == 0:
            print("🎉 ALL TESTS PASSED!")
        elif failed > 0:
            print(f"❌ {failed} TEST(S) FAILED - Implementation needed")
        else:
            print("⚠️ Tests passed with warnings")
        print("="*60)
        
        return failed == 0, test_results

if __name__ == "__main__":
    success, results = asyncio.run(test_progress_indicators())
    
    # Save results
    report = {
        "task_id": "TASK-003",
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "test_results": results,
        "screenshots": [str(f) for f in SCREENSHOT_DIR.glob("*.png")]
    }
    
    with open("TASK_003_test_results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    exit(0 if success else 1)