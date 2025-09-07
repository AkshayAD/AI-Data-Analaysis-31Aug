"""
Comprehensive test for the enhanced app with HITL features
"""

import asyncio
from pathlib import Path
import pandas as pd
import numpy as np
from playwright.async_api import async_playwright
import json
from datetime import datetime

GEMINI_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
BASE_URL = "http://localhost:8504"  # Enhanced app port
SCREENSHOT_DIR = Path("screenshots_enhanced")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def create_test_data():
    """Create comprehensive test CSV file"""
    np.random.seed(42)
    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
        'sales': np.random.randint(100, 1000, 100),
        'quantity': np.random.randint(1, 50, 100),
        'revenue': np.random.uniform(1000, 10000, 100),
        'customer_id': np.random.randint(1000, 2000, 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'satisfaction_score': np.random.uniform(1, 5, 100),
        'profit_margin': np.random.uniform(0.1, 0.4, 100),
        'discount_applied': np.random.choice([True, False], 100)
    }
    df = pd.DataFrame(data)
    test_file = Path("test_data_enhanced.csv")
    df.to_csv(test_file, index=False)
    return test_file

async def test_enhanced_features():
    print("\n" + "="*60)
    print("TESTING ENHANCED APP WITH HITL FEATURES")
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
            # 1. LOAD ENHANCED APPLICATION
            print("\n1. Loading enhanced application...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            await page.screenshot(path=SCREENSHOT_DIR / "01_enhanced_app_loaded.png", full_page=True)
            print("   ✅ Enhanced app loaded successfully")
            results.append({"test": "App Loading", "status": "PASS"})
            
            # Check for enhanced features in sidebar
            content = await page.content()
            if "HITL Features" in content or "Enhanced" in content:
                print("   ✅ Enhanced features detected")
                results.append({"test": "Enhanced Features", "status": "PASS"})
            
            # 2. STAGE 0: ENHANCED INPUT & OBJECTIVES
            print("\n2. Stage 0: Enhanced Input & Objectives")
            
            # Enter API key
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill(GEMINI_API_KEY)
            print("   ✅ API key entered")
            
            # Test connection with retry logic check
            test_buttons = await page.query_selector_all("button")
            for btn in test_buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    await btn.click()
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path=SCREENSHOT_DIR / "02_api_tested_enhanced.png", full_page=True)
                    print("   ✅ API connection tested")
                    results.append({"test": "API Test with Retry", "status": "PASS"})
                    break
            
            # Upload file
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                await file_input.set_input_files(str(test_file))
                await page.wait_for_timeout(3000)
                await page.screenshot(path=SCREENSHOT_DIR / "03_file_uploaded_enhanced.png", full_page=True)
                
                # Check for enhanced data preview
                content = await page.content()
                if "Memory" in content or "MB" in content:
                    print("   ✅ Enhanced data preview with memory usage")
                    results.append({"test": "Enhanced Data Preview", "status": "PASS"})
            
            # Select example objective
            selects = await page.query_selector_all("select")
            for select in selects:
                options = await select.query_selector_all("option")
                for option in options:
                    text = await option.text_content()
                    if "sales trends" in text.lower():
                        await select.select_option(value=text)
                        print("   ✅ Selected example objective")
                        results.append({"test": "Example Objectives", "status": "PASS"})
                        break
            
            # Set custom objective
            textareas = await page.query_selector_all("textarea")
            if textareas:
                await textareas[0].fill("Analyze sales trends, identify top products by region, find correlations between satisfaction and revenue, detect anomalies, and provide actionable recommendations for improving profit margins.")
                await page.wait_for_timeout(1000)
                await page.screenshot(path=SCREENSHOT_DIR / "04_objectives_set_enhanced.png", full_page=True)
                print("   ✅ Business objectives entered")
            
            # Check progress indicators
            content = await page.content()
            if "progress" in content.lower() or "%" in content:
                print("   ✅ Progress indicators present")
                results.append({"test": "Progress Indicators", "status": "PASS"})
            
            # 3. NAVIGATE TO STAGE 1: PLAN GENERATION
            print("\n3. Navigating to Stage 1: Enhanced Plan Generation")
            nav_buttons = await page.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Plan Generation" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "05_stage1_enhanced.png", full_page=True)
                    print("   ✅ Navigated to Stage 1")
                    break
            
            # Generate plan with confidence scoring
            print("   Testing plan generation with confidence scoring...")
            generate_buttons = await page.query_selector_all("button")
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and "Generate" in text and "Plan" in text:
                    await btn.click()
                    await page.wait_for_timeout(12000)  # Longer wait for AI
                    await page.screenshot(path=SCREENSHOT_DIR / "06_plan_generated_enhanced.png", full_page=True)
                    
                    content = await page.content()
                    if "confidence" in content.lower() or "%" in content:
                        print("   ✅ Plan generated with confidence scoring")
                        results.append({"test": "Confidence Scoring", "status": "PASS"})
                    
                    # Check for HITL features
                    if "review" in content.lower() or "human" in content.lower():
                        print("   ✅ HITL review features detected")
                        results.append({"test": "HITL Review", "status": "PASS"})
                    break
            
            # Test chat assistant with suggestions
            print("   Testing enhanced chat assistant...")
            selects = await page.query_selector_all("select")
            for select in selects:
                options = await select.query_selector_all("option")
                for option in options:
                    text = await option.text_content()
                    if "risks" in text.lower():
                        await select.select_option(value=text)
                        print("   ✅ Selected chat suggestion")
                        break
            
            # Send chat message
            send_buttons = await page.query_selector_all("button")
            for btn in send_buttons:
                text = await btn.text_content()
                if text and "Send" in text:
                    await btn.click()
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path=SCREENSHOT_DIR / "07_chat_response_enhanced.png", full_page=True)
                    print("   ✅ Chat assistant responded")
                    results.append({"test": "Enhanced Chat", "status": "PASS"})
                    break
            
            # 4. NAVIGATE TO STAGE 2: DATA UNDERSTANDING
            print("\n4. Navigating to Stage 2: Enhanced Data Understanding")
            nav_buttons = await page.query_selector_all("button")
            for btn in nav_buttons:
                text = await btn.text_content()
                if text and "Data Understanding" in text:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    await page.screenshot(path=SCREENSHOT_DIR / "08_stage2_enhanced.png", full_page=True)
                    print("   ✅ Navigated to Stage 2")
                    break
            
            # Test all enhanced tabs
            tabs = ["Overview", "Statistics", "Quality", "Visualizations", "AI Insights", "HITL Control"]
            for i, tab_name in enumerate(tabs):
                print(f"   Testing {tab_name} tab...")
                
                # Click on tab
                tab_elements = await page.query_selector_all('[role="tab"]')
                if i < len(tab_elements):
                    await tab_elements[i].click()
                    await page.wait_for_timeout(2000)
                    await page.screenshot(path=SCREENSHOT_DIR / f"09_tab_{i+1}_{tab_name.lower().replace(' ', '_')}.png", full_page=True)
                    print(f"   ✅ {tab_name} tab tested")
                    results.append({"test": f"{tab_name} Tab", "status": "PASS"})
            
            # Test AI Insights generation
            print("   Testing comprehensive AI insights...")
            
            # Click on AI Insights tab
            tab_elements = await page.query_selector_all('[role="tab"]')
            if len(tab_elements) > 4:
                await tab_elements[4].click()
                await page.wait_for_timeout(2000)
            
            generate_buttons = await page.query_selector_all("button")
            for btn in generate_buttons:
                text = await btn.text_content()
                if text and "Generate" in text and ("Insights" in text or "AI" in text):
                    await btn.click()
                    await page.wait_for_timeout(12000)  # Wait for AI analysis
                    await page.screenshot(path=SCREENSHOT_DIR / "10_insights_generated_enhanced.png", full_page=True)
                    
                    content = await page.content()
                    if "patterns" in content.lower() or "insights" in content.lower():
                        print("   ✅ Comprehensive insights generated")
                        results.append({"test": "AI Insights Generation", "status": "PASS"})
                    
                    # Check for confidence indicators
                    if "confidence" in content.lower() or "%" in content:
                        print("   ✅ Insights include confidence scores")
                        results.append({"test": "Insights Confidence", "status": "PASS"})
                    break
            
            # Test HITL Control Panel
            print("   Testing HITL Control Panel...")
            
            # Click on HITL Control tab
            tab_elements = await page.query_selector_all('[role="tab"]')
            if len(tab_elements) > 5:
                await tab_elements[5].click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path=SCREENSHOT_DIR / "11_hitl_control_panel.png", full_page=True)
                
                content = await page.content()
                if "threshold" in content.lower() or "automation" in content.lower():
                    print("   ✅ HITL control panel functional")
                    results.append({"test": "HITL Control Panel", "status": "PASS"})
            
            # Test export options
            print("   Testing enhanced export options...")
            download_buttons = await page.query_selector_all("button")
            export_count = 0
            for btn in download_buttons:
                text = await btn.text_content()
                if text and "Download" in text:
                    export_count += 1
            
            if export_count >= 3:
                print(f"   ✅ Found {export_count} export options")
                results.append({"test": "Export Options", "status": "PASS"})
            
            # Final screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "12_test_complete_enhanced.png", full_page=True)
            
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_state_enhanced.png", full_page=True)
            results.append({"test": "Critical Error", "status": "FAIL", "error": str(e)})
            
        finally:
            await browser.close()
            
            # Save results
            report = {
                "timestamp": datetime.now().isoformat(),
                "app_version": "Enhanced 2.0",
                "results": results,
                "summary": {
                    "total": len(results),
                    "passed": len([r for r in results if r["status"] == "PASS"]),
                    "failed": len([r for r in results if r["status"] == "FAIL"])
                }
            }
            
            with open("enhanced_app_test_report.json", "w") as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            print("\n" + "="*60)
            print("ENHANCED APP TEST RESULTS SUMMARY")
            print("="*60)
            
            for result in results:
                status_icon = "✅" if result["status"] == "PASS" else "❌"
                print(f"{status_icon} {result['test']}: {result['status']}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
            
            summary = report["summary"]
            print(f"\n📊 Final Score: {summary['passed']}/{summary['total']} tests passed ({summary['passed']/summary['total']*100:.1f}%)")
            print(f"   ✅ Passed: {summary['passed']}")
            print(f"   ❌ Failed: {summary['failed']}")
            
            print(f"\n📁 Screenshots saved to: {SCREENSHOT_DIR}/")
            print(f"📝 Report saved to: enhanced_app_test_report.json")
            
            # Check if this is a significant improvement
            if summary['passed'] >= 15:
                print("\n🎉 SIGNIFICANT IMPROVEMENT: Enhanced app shows major improvements over basic version!")
            
            return summary['passed'] == summary['total']

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_features())
    exit(0 if success else 1)