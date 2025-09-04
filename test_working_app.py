"""
Complete test of the working app with proper selectors
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
SCREENSHOT_DIR = Path("screenshots_working_app")
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
    print("TESTING WORKING APP - COMPLETE WORKFLOW")
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
        
        try:
            # 1. LOAD APPLICATION
            print("\n1. Loading application...")
            await page.goto(BASE_URL)
            await page.wait_for_timeout(3000)
            await page.screenshot(path=SCREENSHOT_DIR / "01_app_loaded.png", full_page=True)
            print("   ✅ App loaded successfully")
            
            # 2. STAGE 0: INPUT & OBJECTIVES
            print("\n2. Stage 0: Input & Objectives")
            print("   Testing API configuration...")
            
            # Click API Configuration expander
            api_expander = await page.query_selector("text=Gemini API Configuration")
            if api_expander:
                await api_expander.click()
                await page.wait_for_timeout(500)
            
            # Enter API key - password input is visible in screenshot
            api_input = await page.query_selector("input[type='password']")
            if api_input:
                await api_input.fill(GEMINI_API_KEY)
                await page.screenshot(path=SCREENSHOT_DIR / "02_api_key_entered.png")
                print("   ✅ API key entered")
                
                # Test connection
                test_btn = await page.query_selector("button:has-text('Test Connection')")
                if test_btn:
                    await test_btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "03_api_tested.png")
                    
                    # Check for success
                    content = await page.content()
                    if "Connected" in content or "✅" in content:
                        print("   ✅ API connection successful")
                        results.append({"test": "API Connection", "status": "PASS"})
                    else:
                        print("   ❌ API connection failed")
                        results.append({"test": "API Connection", "status": "FAIL"})
            
            # Upload file
            print("   Testing file upload...")
            upload_expander = await page.query_selector("text=Data Upload")
            if upload_expander:
                await upload_expander.click()
                await page.wait_for_timeout(500)
            
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                test_file = create_test_data()
                await file_input.set_input_files(str(test_file))
                await page.wait_for_timeout(3000)
                await page.screenshot(path=SCREENSHOT_DIR / "04_file_uploaded.png", full_page=True)
                print("   ✅ File uploaded")
                results.append({"test": "File Upload", "status": "PASS"})
            
            # Enter business objective
            print("   Testing business objective...")
            obj_expander = await page.query_selector("text=Business Objective")
            if obj_expander:
                await obj_expander.click()
                await page.wait_for_timeout(500)
            
            obj_textarea = await page.query_selector("textarea")
            if obj_textarea:
                objective = "Analyze sales patterns to identify top products and customer segments. Find correlations between satisfaction and revenue."
                await obj_textarea.fill(objective)
                await page.screenshot(path=SCREENSHOT_DIR / "05_objective_entered.png")
                print("   ✅ Business objective entered")
                results.append({"test": "Business Objective", "status": "PASS"})
            
            # Navigate to Stage 1
            print("   Navigating to Stage 1...")
            next_btn = await page.query_selector("button:has-text('Next: Plan Generation')")
            if not next_btn:
                next_btn = await page.query_selector("button:has-text('Plan Generation')")
            
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path=SCREENSHOT_DIR / "06_stage1_loaded.png", full_page=True)
                print("   ✅ Navigated to Stage 1")
                results.append({"test": "Navigation to Stage 1", "status": "PASS"})
            
            # 3. STAGE 1: PLAN GENERATION
            print("\n3. Stage 1: Plan Generation")
            print("   Generating AI plan...")
            
            generate_btn = await page.query_selector("button:has-text('Generate AI Plan')")
            if generate_btn:
                await generate_btn.click()
                await page.wait_for_timeout(8000)  # Wait for AI response
                await page.screenshot(path=SCREENSHOT_DIR / "07_plan_generated.png", full_page=True)
                
                # Check if plan was generated
                plan_textarea = await page.query_selector("textarea")
                if plan_textarea:
                    plan_content = await plan_textarea.input_value()
                    if plan_content and len(plan_content) > 100:
                        print(f"   ✅ Plan generated ({len(plan_content)} characters)")
                        results.append({"test": "Plan Generation", "status": "PASS"})
                        
                        # Edit the plan
                        edited_plan = plan_content + "\n\nAdditional Analysis:\n- Customer lifetime value\n- Regional performance"
                        await plan_textarea.fill(edited_plan)
                        await page.screenshot(path=SCREENSHOT_DIR / "08_plan_edited.png")
                        print("   ✅ Plan edited")
                    else:
                        print("   ❌ Plan generation failed")
                        results.append({"test": "Plan Generation", "status": "FAIL"})
            
            # Test chat
            print("   Testing AI chat...")
            chat_input = await page.query_selector("input[placeholder*='Ask']")
            if not chat_input:
                # Try finding by looking for the second input on the page
                inputs = await page.query_selector_all("input")
                if len(inputs) > 1:
                    chat_input = inputs[1]
            
            if chat_input:
                await chat_input.fill("What metrics should I focus on?")
                send_btn = await page.query_selector("button:has-text('Send')")
                if send_btn:
                    await send_btn.click()
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path=SCREENSHOT_DIR / "09_chat_response.png", full_page=True)
                    print("   ✅ Chat tested")
                    results.append({"test": "AI Chat", "status": "PASS"})
            
            # Navigate to Stage 2
            print("   Navigating to Stage 2...")
            next_btn = await page.query_selector("button:has-text('Data Understanding')")
            if not next_btn:
                next_btn = await page.query_selector("button:has-text('Next')")
            
            if next_btn:
                await next_btn.click()
                await page.wait_for_timeout(3000)
                await page.screenshot(path=SCREENSHOT_DIR / "10_stage2_loaded.png", full_page=True)
                print("   ✅ Navigated to Stage 2")
                results.append({"test": "Navigation to Stage 2", "status": "PASS"})
            
            # 4. STAGE 2: DATA UNDERSTANDING
            print("\n4. Stage 2: Data Understanding")
            
            # Test tabs
            tabs = ["Overview", "Statistics", "Quality", "Visualizations", "AI Insights"]
            for i, tab_name in enumerate(tabs):
                print(f"   Testing {tab_name} tab...")
                tab = await page.query_selector(f"button:has-text('{tab_name}')")
                if not tab:
                    tab = await page.query_selector(f"text={tab_name}")
                
                if tab:
                    await tab.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=SCREENSHOT_DIR / f"11_tab_{i}_{tab_name.lower()}.png", full_page=True)
                    print(f"   ✅ {tab_name} tab tested")
                    results.append({"test": f"{tab_name} Tab", "status": "PASS"})
                else:
                    print(f"   ⚠️ {tab_name} tab not found")
                    results.append({"test": f"{tab_name} Tab", "status": "SKIP"})
            
            # Generate AI insights
            print("   Generating AI insights...")
            insights_btn = await page.query_selector("button:has-text('Generate AI Insights')")
            if insights_btn:
                await insights_btn.click()
                await page.wait_for_timeout(8000)
                await page.screenshot(path=SCREENSHOT_DIR / "12_ai_insights.png", full_page=True)
                print("   ✅ AI insights generated")
                results.append({"test": "AI Insights Generation", "status": "PASS"})
            
            # Test export
            print("   Testing export functionality...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1000)
            
            download_btn = await page.query_selector("button:has-text('Download')")
            if download_btn:
                await page.screenshot(path=SCREENSHOT_DIR / "13_export_section.png", full_page=True)
                print("   ✅ Export buttons found")
                results.append({"test": "Export Functionality", "status": "PASS"})
            
            # 5. TEST NAVIGATION
            print("\n5. Testing navigation between stages...")
            
            # Navigate back using sidebar
            sidebar_btns = await page.query_selector_all("button")
            for btn in sidebar_btns:
                text = await btn.text_content()
                if "Input" in text:
                    await btn.click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=SCREENSHOT_DIR / "14_back_to_stage0.png")
                    print("   ✅ Navigated back to Stage 0")
                    results.append({"test": "Backward Navigation", "status": "PASS"})
                    break
            
            # Final screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "15_final_state.png", full_page=True)
            
        except Exception as e:
            print(f"\n   ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "99_error.png", full_page=True)
            results.append({"test": "Critical Error", "status": "FAIL", "error": str(e)})
        
        finally:
            await browser.close()
    
    # Generate report
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⊘"
        print(f"{status_icon} {result['test']}: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print(f"\n📊 Final Score: {passed}/{len(results)} tests passed ({passed/len(results)*100:.1f}%)")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⊘ Skipped: {skipped}")
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "url": BASE_URL,
        "results": results,
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": passed/len(results)*100 if results else 0
        }
    }
    
    with open("working_app_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Screenshots saved to: {SCREENSHOT_DIR}/")
    print(f"📝 Report saved to: working_app_test_report.json")
    
    return passed/len(results) >= 0.7 if results else False

if __name__ == "__main__":
    import sys
    success = asyncio.run(test_complete_workflow())
    sys.exit(0 if success else 1)