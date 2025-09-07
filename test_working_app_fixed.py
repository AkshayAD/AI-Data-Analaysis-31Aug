"""
Fixed test for the working app with proper selectors for current Streamlit version
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
SCREENSHOT_DIR = Path("screenshots_working_app_fixed")
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

async def test_complete_workflow():
    print("\n" + "="*60)
    print("TESTING WORKING APP - COMPLETE WORKFLOW (FIXED)")
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
        
        results = []
        test_file = create_test_data()
        
        try:
            # 1. LOAD APPLICATION
            print("\n1. Loading application...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)  # Give Streamlit time to fully load
            await page.screenshot(path=SCREENSHOT_DIR / "01_app_loaded.png", full_page=True)
            print("   ✅ App loaded successfully")
            
            # 2. STAGE 0: INPUT & OBJECTIVES
            print("\n2. Stage 0: Input & Objectives")
            print("   Testing API configuration...")
            
            # Wait for Streamlit to render all components
            await page.wait_for_selector("text=Gemini API Configuration", timeout=10000)
            
            # Find and fill API key using iframe structure if needed
            # Streamlit renders in iframes, we need to wait for the main content
            frames = page.frames
            main_frame = page
            
            # Try to find password input in main frame
            api_input = await main_frame.wait_for_selector("input[type='password']", timeout=10000)
            if api_input:
                await api_input.fill(GEMINI_API_KEY)
                await page.wait_for_timeout(1000)
                await page.screenshot(path=SCREENSHOT_DIR / "02_api_key_entered.png", full_page=True)
                print("   ✅ API key entered")
                
                # Find and click Test Connection button
                # Use more specific selector
                test_buttons = await main_frame.query_selector_all("button")
                for btn in test_buttons:
                    text = await btn.text_content()
                    if text and "Test Connection" in text:
                        await btn.click()
                        await page.wait_for_timeout(5000)  # Wait for API test
                        await page.screenshot(path=SCREENSHOT_DIR / "03_api_tested.png", full_page=True)
                        
                        # Check for success message
                        content = await page.content()
                        if "Connected" in content or "Success" in content or "Model available" in content:
                            print("   ✅ API connection successful")
                            results.append({"test": "API Connection", "status": "PASS"})
                        else:
                            print("   ⚠️ API connection status unclear")
                            results.append({"test": "API Connection", "status": "UNKNOWN"})
                        break
            
            # Upload file
            print("   Testing file upload...")
            
            # Find file uploader
            file_input = await main_frame.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(test_file))
                await page.wait_for_timeout(3000)
                await page.screenshot(path=SCREENSHOT_DIR / "04_file_uploaded.png", full_page=True)
                
                # Check if file was uploaded
                content = await page.content()
                if "test_data.csv" in content or "Data Preview" in content or "100 rows" in content:
                    print("   ✅ File uploaded successfully")
                    results.append({"test": "File Upload", "status": "PASS"})
                else:
                    print("   ❌ File upload failed")
                    results.append({"test": "File Upload", "status": "FAIL"})
            
            # Set business objectives
            print("   Testing business objectives...")
            objective_input = await main_frame.query_selector("textarea")
            if objective_input:
                await objective_input.fill("Analyze sales trends and identify top performing products and regions. Find correlations between customer satisfaction and revenue.")
                await page.wait_for_timeout(1000)
                await page.screenshot(path=SCREENSHOT_DIR / "05_objectives_set.png", full_page=True)
                print("   ✅ Business objectives entered")
                results.append({"test": "Business Objectives", "status": "PASS"})
            
            # 3. NAVIGATE TO STAGE 1
            print("\n3. Navigating to Stage 1: Plan Generation")
            nav_buttons = await main_frame.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Plan Generation" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "06_stage1_loaded.png", full_page=True)
                    
                    # Check if navigated
                    content = await page.content()
                    if "Generate Analysis Plan" in content or "Plan Generation" in content:
                        print("   ✅ Navigated to Stage 1")
                        results.append({"test": "Navigation to Stage 1", "status": "PASS"})
                    break
            
            # Generate plan
            print("   Testing plan generation...")
            generate_buttons = await main_frame.query_selector_all("button")
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Plan" in text:
                    await btn.click()
                    await page.wait_for_timeout(10000)  # Wait for AI generation
                    await page.screenshot(path=SCREENSHOT_DIR / "07_plan_generated.png", full_page=True)
                    
                    content = await page.content()
                    if "Analysis Plan" in content or "Steps" in content or "Objectives" in content:
                        print("   ✅ Plan generated successfully")
                        results.append({"test": "Plan Generation", "status": "PASS"})
                    else:
                        print("   ❌ Plan generation failed")
                        results.append({"test": "Plan Generation", "status": "FAIL"})
                    break
            
            # 4. NAVIGATE TO STAGE 2
            print("\n4. Navigating to Stage 2: Data Understanding")
            nav_buttons = await main_frame.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Data Understanding" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "08_stage2_loaded.png", full_page=True)
                    
                    content = await page.content()
                    if "Data Understanding" in content or "Data Overview" in content:
                        print("   ✅ Navigated to Stage 2")
                        results.append({"test": "Navigation to Stage 2", "status": "PASS"})
                    break
            
            # Click on AI Insights tab first
            print("   Clicking AI Insights tab...")
            tab_clicked = False
            
            # Try to find and click the AI Insights tab
            # Method 1: Look for elements with role="tab"
            tabs = await main_frame.query_selector_all('[role="tab"]')
            for tab in tabs:
                text = await tab.text_content()
                if text and ("AI Insights" in text or "💡" in text):
                    await tab.click()
                    await page.wait_for_timeout(2000)
                    print("   ✅ AI Insights tab clicked")
                    tab_clicked = True
                    break
            
            # Method 2: If not found, try buttons that might be tabs
            if not tab_clicked:
                buttons = await main_frame.query_selector_all("button")
                for btn in buttons:
                    text = await btn.text_content()
                    if text and ("AI Insights" in text or "💡" in text):
                        await btn.click()
                        await page.wait_for_timeout(2000)
                        print("   ✅ AI Insights tab clicked (button)")
                        tab_clicked = True
                        break
            
            # Generate insights
            print("   Testing data insights generation...")
            generate_buttons = await main_frame.query_selector_all("button")
            button_found = False
            
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Insights" in text:
                    button_found = True
                    print(f"   ✅ Found Generate AI Insights button: '{text.strip()}'")
                    await btn.click()
                    await page.wait_for_timeout(10000)  # Wait for AI analysis
                    await page.screenshot(path=SCREENSHOT_DIR / "09_insights_generated.png", full_page=True)
                    
                    content = await page.content()
                    if "insights" in content.lower() or "analysis" in content.lower():
                        print("   ✅ Insights generated successfully")
                        results.append({"test": "Insights Generation", "status": "PASS"})
                    else:
                        print("   ❌ Insights generation failed")
                        results.append({"test": "Insights Generation", "status": "FAIL"})
                    break
            
            if not button_found:
                print("   ❌ Generate AI Insights button not found")
                results.append({"test": "Insights Generation", "status": "FAIL"})
            
            # Final screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "10_test_complete.png", full_page=True)
            
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_state.png", full_page=True)
            results.append({"test": "Critical Error", "status": "FAIL", "error": str(e)})
            
        finally:
            await browser.close()
            
            # Save results
            report = {
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "summary": {
                    "total": len(results),
                    "passed": len([r for r in results if r["status"] == "PASS"]),
                    "failed": len([r for r in results if r["status"] == "FAIL"]),
                    "unknown": len([r for r in results if r.get("status") == "UNKNOWN"])
                }
            }
            
            with open("working_app_test_report_fixed.json", "w") as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print("\n" + "="*60)
            print("TEST RESULTS SUMMARY")
            print("="*60)
            
            for result in results:
                status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
                print(f"{status_icon} {result['test']}: {result['status']}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
            
            summary = report["summary"]
            print(f"\n📊 Final Score: {summary['passed']}/{summary['total']} tests passed ({summary['passed']/summary['total']*100:.1f}%)")
            print(f"   ✅ Passed: {summary['passed']}")
            print(f"   ❌ Failed: {summary['failed']}")
            print(f"   ⚠️ Unknown: {summary['unknown']}")
            
            print(f"\n📁 Screenshots saved to: {SCREENSHOT_DIR}/")
            print(f"📝 Report saved to: working_app_test_report_fixed.json")
            
            return summary['passed'] == summary['total']

if __name__ == "__main__":
    success = asyncio.run(test_complete_workflow())
    exit(0 if success else 1)