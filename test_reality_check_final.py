"""
Comprehensive Reality Check Test with Playwright
Tests the actual functionality with real Gemini API integration
"""

import asyncio
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np
from playwright.async_api import async_playwright, expect

# Test configuration
GEMINI_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
BASE_URL = "http://localhost:8502"
SCREENSHOT_DIR = Path("test_screenshots_final")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Create test data file
def create_test_data():
    """Create a realistic test CSV file"""
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
    test_file = Path("test_sales_data.csv")
    df.to_csv(test_file, index=False)
    return test_file

async def test_stage_0_input_objective(page, context):
    """Test Stage 0: Input & Objective with real functionality"""
    print("\n=== Testing Stage 0: Input & Objective ===")
    results = {"stage": "Stage 0", "tests": []}
    
    try:
        # Navigate to the app
        await page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        await page.screenshot(path=SCREENSHOT_DIR / "00_initial_load.png")
        
        # Check if we're on the right page
        title_element = page.locator("h1, h2").filter(has_text="Input")
        if await title_element.count() == 0:
            # Try to navigate to Stage 0
            stage_0_link = page.locator("a, button").filter(has_text="Input")
            if await stage_0_link.count() > 0:
                await stage_0_link.first.click()
                await page.wait_for_load_state('networkidle')
        
        await page.screenshot(path=SCREENSHOT_DIR / "01_stage0_loaded.png")
        
        # Test 1: API Key Input
        print("Test 1: Entering Gemini API Key...")
        api_key_input = page.locator("input[type='text'], input[type='password']").filter(has_text="API")
        if await api_key_input.count() == 0:
            api_key_input = page.locator("input").nth(0)
        
        if await api_key_input.count() > 0:
            await api_key_input.fill(GEMINI_API_KEY)
            await page.screenshot(path=SCREENSHOT_DIR / "02_api_key_entered.png")
            results["tests"].append({"name": "API Key Input", "status": "PASS"})
        else:
            results["tests"].append({"name": "API Key Input", "status": "FAIL", "error": "No API key input found"})
        
        # Test 2: Model Selection
        print("Test 2: Selecting Gemini Model...")
        model_select = page.locator("select, [role='combobox']").filter(has_text="gemini")
        if await model_select.count() == 0:
            model_select = page.locator("select").first
        
        if await model_select.count() > 0:
            await model_select.select_option(index=0)
            await page.screenshot(path=SCREENSHOT_DIR / "03_model_selected.png")
            results["tests"].append({"name": "Model Selection", "status": "PASS"})
        else:
            results["tests"].append({"name": "Model Selection", "status": "FAIL", "error": "No model selector found"})
        
        # Test 3: File Upload
        print("Test 3: Uploading test data file...")
        test_file = create_test_data()
        file_input = page.locator("input[type='file']")
        
        if await file_input.count() > 0:
            await file_input.set_input_files(str(test_file))
            await page.wait_for_timeout(2000)
            await page.screenshot(path=SCREENSHOT_DIR / "04_file_uploaded.png")
            results["tests"].append({"name": "File Upload", "status": "PASS"})
        else:
            results["tests"].append({"name": "File Upload", "status": "FAIL", "error": "No file input found"})
        
        # Test 4: Business Objective
        print("Test 4: Entering business objective...")
        objective_input = page.locator("textarea").filter(has_text="objective")
        if await objective_input.count() == 0:
            objective_input = page.locator("textarea").first
        
        if await objective_input.count() > 0:
            await objective_input.fill("Analyze sales patterns to identify top-performing products and regions. Find correlations between customer satisfaction and revenue.")
            await page.screenshot(path=SCREENSHOT_DIR / "05_objective_entered.png")
            results["tests"].append({"name": "Business Objective", "status": "PASS"})
        else:
            results["tests"].append({"name": "Business Objective", "status": "FAIL", "error": "No objective input found"})
        
        # Test 5: Test API Connection
        print("Test 5: Testing API connection...")
        test_button = page.locator("button").filter(has_text="Test")
        if await test_button.count() > 0:
            await test_button.click()
            await page.wait_for_timeout(3000)
            
            # Check for success message
            success_msg = page.locator("text=/connected|success|working/i")
            if await success_msg.count() > 0:
                await page.screenshot(path=SCREENSHOT_DIR / "06_api_test_success.png")
                results["tests"].append({"name": "API Connection Test", "status": "PASS"})
            else:
                await page.screenshot(path=SCREENSHOT_DIR / "06_api_test_fail.png")
                results["tests"].append({"name": "API Connection Test", "status": "FAIL", "error": "No success message"})
        else:
            results["tests"].append({"name": "API Connection Test", "status": "SKIP", "error": "No test button found"})
        
        # Test 6: Navigate to Stage 1
        print("Test 6: Navigating to Stage 1...")
        next_button = page.locator("button").filter(has_text="Next")
        if await next_button.count() == 0:
            next_button = page.locator("button").filter(has_text="Plan")
        
        if await next_button.count() > 0:
            await next_button.click()
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=SCREENSHOT_DIR / "07_navigate_to_stage1.png")
            
            # Check if we reached Stage 1
            stage1_title = page.locator("h1, h2").filter(has_text="Plan")
            if await stage1_title.count() > 0:
                results["tests"].append({"name": "Navigation to Stage 1", "status": "PASS"})
            else:
                results["tests"].append({"name": "Navigation to Stage 1", "status": "FAIL", "error": "Did not reach Stage 1"})
        else:
            results["tests"].append({"name": "Navigation to Stage 1", "status": "FAIL", "error": "No navigation button found"})
        
    except Exception as e:
        results["error"] = str(e)
        await page.screenshot(path=SCREENSHOT_DIR / "stage0_error.png")
    
    return results

async def test_stage_1_plan_generation(page, context):
    """Test Stage 1: Plan Generation with real AI"""
    print("\n=== Testing Stage 1: Plan Generation ===")
    results = {"stage": "Stage 1", "tests": []}
    
    try:
        # Ensure we're on Stage 1
        current_url = page.url
        if "Plan" not in current_url and "01_" not in current_url:
            # Try to navigate to Stage 1
            stage1_link = page.locator("a, button").filter(has_text="Plan Generation")
            if await stage1_link.count() > 0:
                await stage1_link.click()
                await page.wait_for_load_state('networkidle')
        
        await page.screenshot(path=SCREENSHOT_DIR / "10_stage1_loaded.png")
        
        # Test 1: Generate Plan button
        print("Test 1: Generating AI plan...")
        generate_button = page.locator("button").filter(has_text="Generate")
        if await generate_button.count() > 0:
            await generate_button.click()
            await page.wait_for_timeout(5000)  # Wait for AI response
            
            # Check for generated plan
            plan_content = page.locator("text=/analysis|plan|steps|data/i")
            if await plan_content.count() > 0:
                await page.screenshot(path=SCREENSHOT_DIR / "11_plan_generated.png")
                results["tests"].append({"name": "AI Plan Generation", "status": "PASS"})
            else:
                await page.screenshot(path=SCREENSHOT_DIR / "11_plan_generation_fail.png")
                results["tests"].append({"name": "AI Plan Generation", "status": "FAIL", "error": "No plan content found"})
        else:
            results["tests"].append({"name": "AI Plan Generation", "status": "FAIL", "error": "No generate button found"})
        
        # Test 2: Plan Editor
        print("Test 2: Testing plan editor...")
        editor = page.locator("textarea, [contenteditable='true']")
        if await editor.count() > 0:
            # Try to edit the plan
            await editor.first.click()
            await editor.first.fill("Updated plan: Focus on revenue analysis and customer segmentation")
            await page.screenshot(path=SCREENSHOT_DIR / "12_plan_edited.png")
            results["tests"].append({"name": "Plan Editor", "status": "PASS"})
        else:
            results["tests"].append({"name": "Plan Editor", "status": "FAIL", "error": "No editor found"})
        
        # Test 3: AI Chat
        print("Test 3: Testing AI chat...")
        chat_input = page.locator("input, textarea").filter(has_text="chat")
        if await chat_input.count() == 0:
            chat_input = page.locator("input[placeholder*='Ask'], textarea[placeholder*='Ask']")
        
        if await chat_input.count() > 0:
            await chat_input.fill("What are the key metrics I should focus on?")
            
            # Find send button
            send_button = page.locator("button").filter(has_text="Send")
            if await send_button.count() == 0:
                send_button = page.locator("button[type='submit']")
            
            if await send_button.count() > 0:
                await send_button.click()
                await page.wait_for_timeout(5000)  # Wait for AI response
                
                # Check for chat response
                chat_response = page.locator("text=/metric|revenue|sales|customer/i")
                if await chat_response.count() > 0:
                    await page.screenshot(path=SCREENSHOT_DIR / "13_chat_response.png")
                    results["tests"].append({"name": "AI Chat", "status": "PASS"})
                else:
                    results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No chat response"})
            else:
                results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No send button"})
        else:
            results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No chat input found"})
        
        # Test 4: Save Plan
        print("Test 4: Saving plan...")
        save_button = page.locator("button").filter(has_text="Save")
        if await save_button.count() > 0:
            await save_button.click()
            await page.wait_for_timeout(2000)
            
            # Check for save confirmation
            saved_msg = page.locator("text=/saved|success/i")
            if await saved_msg.count() > 0:
                await page.screenshot(path=SCREENSHOT_DIR / "14_plan_saved.png")
                results["tests"].append({"name": "Save Plan", "status": "PASS"})
            else:
                results["tests"].append({"name": "Save Plan", "status": "WARNING", "error": "No save confirmation"})
        else:
            results["tests"].append({"name": "Save Plan", "status": "SKIP", "error": "No save button found"})
        
        # Test 5: Navigate to Stage 2
        print("Test 5: Navigating to Stage 2...")
        next_button = page.locator("button").filter(has_text="Next")
        if await next_button.count() == 0:
            next_button = page.locator("button").filter(has_text="Data Understanding")
        
        if await next_button.count() > 0:
            await next_button.click()
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=SCREENSHOT_DIR / "15_navigate_to_stage2.png")
            
            # Check if we reached Stage 2
            stage2_title = page.locator("h1, h2").filter(has_text="Data Understanding")
            if await stage2_title.count() > 0:
                results["tests"].append({"name": "Navigation to Stage 2", "status": "PASS"})
            else:
                results["tests"].append({"name": "Navigation to Stage 2", "status": "FAIL", "error": "Did not reach Stage 2"})
        else:
            results["tests"].append({"name": "Navigation to Stage 2", "status": "FAIL", "error": "No navigation button found"})
        
    except Exception as e:
        results["error"] = str(e)
        await page.screenshot(path=SCREENSHOT_DIR / "stage1_error.png")
    
    return results

async def test_stage_2_data_understanding(page, context):
    """Test Stage 2: Data Understanding with real data processing"""
    print("\n=== Testing Stage 2: Data Understanding ===")
    results = {"stage": "Stage 2", "tests": []}
    
    try:
        # Ensure we're on Stage 2
        current_url = page.url
        if "Data" not in current_url and "02_" not in current_url:
            # Try to navigate to Stage 2
            stage2_link = page.locator("a, button").filter(has_text="Data Understanding")
            if await stage2_link.count() > 0:
                await stage2_link.click()
                await page.wait_for_load_state('networkidle')
        
        await page.screenshot(path=SCREENSHOT_DIR / "20_stage2_loaded.png")
        
        # Test 1: Data Preview
        print("Test 1: Checking data preview...")
        data_table = page.locator("table, [role='table']")
        if await data_table.count() > 0:
            await page.screenshot(path=SCREENSHOT_DIR / "21_data_preview.png")
            results["tests"].append({"name": "Data Preview", "status": "PASS"})
        else:
            results["tests"].append({"name": "Data Preview", "status": "FAIL", "error": "No data table found"})
        
        # Test 2: Statistical Summary
        print("Test 2: Checking statistical summary...")
        stats_section = page.locator("text=/mean|std|min|max|count/i")
        if await stats_section.count() > 0:
            await page.screenshot(path=SCREENSHOT_DIR / "22_statistics.png")
            results["tests"].append({"name": "Statistical Summary", "status": "PASS"})
        else:
            results["tests"].append({"name": "Statistical Summary", "status": "FAIL", "error": "No statistics found"})
        
        # Test 3: Data Quality Assessment
        print("Test 3: Checking data quality...")
        quality_section = page.locator("text=/quality|missing|duplicate|outlier/i")
        if await quality_section.count() > 0:
            await page.screenshot(path=SCREENSHOT_DIR / "23_data_quality.png")
            results["tests"].append({"name": "Data Quality", "status": "PASS"})
        else:
            results["tests"].append({"name": "Data Quality", "status": "FAIL", "error": "No quality metrics found"})
        
        # Test 4: Visualizations
        print("Test 4: Checking visualizations...")
        # Look for chart containers or canvas elements
        charts = page.locator("canvas, svg, [class*='chart'], [id*='chart']")
        if await charts.count() > 0:
            await page.screenshot(path=SCREENSHOT_DIR / "24_visualizations.png")
            results["tests"].append({"name": "Visualizations", "status": "PASS", "count": await charts.count()})
        else:
            results["tests"].append({"name": "Visualizations", "status": "FAIL", "error": "No charts found"})
        
        # Test 5: AI Insights
        print("Test 5: Generating AI insights...")
        insights_button = page.locator("button").filter(has_text="Insights")
        if await insights_button.count() == 0:
            insights_button = page.locator("button").filter(has_text="Generate")
        
        if await insights_button.count() > 0:
            await insights_button.click()
            await page.wait_for_timeout(5000)  # Wait for AI response
            
            # Check for insights
            insights_text = page.locator("text=/pattern|trend|correlation|insight/i")
            if await insights_text.count() > 0:
                await page.screenshot(path=SCREENSHOT_DIR / "25_ai_insights.png")
                results["tests"].append({"name": "AI Insights", "status": "PASS"})
            else:
                results["tests"].append({"name": "AI Insights", "status": "FAIL", "error": "No insights generated"})
        else:
            results["tests"].append({"name": "AI Insights", "status": "SKIP", "error": "No insights button found"})
        
        # Test 6: Export functionality
        print("Test 6: Testing export functionality...")
        export_button = page.locator("button").filter(has_text="Export")
        if await export_button.count() == 0:
            export_button = page.locator("button").filter(has_text="Download")
        
        if await export_button.count() > 0:
            # Set up download handler
            async with page.expect_download() as download_info:
                await export_button.click()
                download = await download_info.value
                await page.screenshot(path=SCREENSHOT_DIR / "26_export_triggered.png")
                results["tests"].append({"name": "Export Data", "status": "PASS", "file": download.suggested_filename})
        else:
            results["tests"].append({"name": "Export Data", "status": "SKIP", "error": "No export button found"})
        
    except Exception as e:
        results["error"] = str(e)
        await page.screenshot(path=SCREENSHOT_DIR / "stage2_error.png")
    
    return results

async def test_navigation_flow(page, context):
    """Test navigation between all stages"""
    print("\n=== Testing Navigation Flow ===")
    results = {"stage": "Navigation", "tests": []}
    
    try:
        # Test backward navigation
        print("Testing backward navigation...")
        
        # Try to go back to Stage 1
        stage1_link = page.locator("a, button").filter(has_text="Plan Generation")
        if await stage1_link.count() > 0:
            await stage1_link.click()
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=SCREENSHOT_DIR / "30_back_to_stage1.png")
            results["tests"].append({"name": "Navigate back to Stage 1", "status": "PASS"})
        else:
            results["tests"].append({"name": "Navigate back to Stage 1", "status": "FAIL", "error": "No Stage 1 link"})
        
        # Try to go back to Stage 0
        stage0_link = page.locator("a, button").filter(has_text="Input")
        if await stage0_link.count() > 0:
            await stage0_link.click()
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=SCREENSHOT_DIR / "31_back_to_stage0.png")
            results["tests"].append({"name": "Navigate back to Stage 0", "status": "PASS"})
        else:
            results["tests"].append({"name": "Navigate back to Stage 0", "status": "FAIL", "error": "No Stage 0 link"})
        
        # Test sidebar navigation
        print("Testing sidebar navigation...")
        sidebar = page.locator("[data-testid='stSidebar'], aside")
        if await sidebar.count() > 0:
            await page.screenshot(path=SCREENSHOT_DIR / "32_sidebar_navigation.png")
            results["tests"].append({"name": "Sidebar Navigation", "status": "PASS"})
        else:
            results["tests"].append({"name": "Sidebar Navigation", "status": "WARNING", "error": "No sidebar found"})
        
    except Exception as e:
        results["error"] = str(e)
        await page.screenshot(path=SCREENSHOT_DIR / "navigation_error.png")
    
    return results

async def main():
    """Main test runner"""
    print("=" * 60)
    print("COMPREHENSIVE REALITY CHECK TEST")
    print("Testing with Real Gemini API Integration")
    print("=" * 60)
    
    all_results = []
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,  # Running in headless mode
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        
        # Set longer timeout for slow operations
        page.set_default_timeout(60000)
        
        try:
            # Run all tests
            stage0_results = await test_stage_0_input_objective(page, context)
            all_results.append(stage0_results)
            
            stage1_results = await test_stage_1_plan_generation(page, context)
            all_results.append(stage1_results)
            
            stage2_results = await test_stage_2_data_understanding(page, context)
            all_results.append(stage2_results)
            
            nav_results = await test_navigation_flow(page, context)
            all_results.append(nav_results)
            
        except Exception as e:
            print(f"Critical error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "critical_error.png")
        
        finally:
            await browser.close()
    
    # Generate test report
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_pass = 0
    total_fail = 0
    total_skip = 0
    
    for stage_result in all_results:
        print(f"\n{stage_result['stage']}:")
        print("-" * 40)
        
        for test in stage_result.get("tests", []):
            status = test["status"]
            name = test["name"]
            
            if status == "PASS":
                print(f"  ✓ {name}: PASS")
                total_pass += 1
            elif status == "FAIL":
                print(f"  ✗ {name}: FAIL - {test.get('error', 'Unknown error')}")
                total_fail += 1
            elif status == "SKIP":
                print(f"  ⊘ {name}: SKIP - {test.get('error', 'Skipped')}")
                total_skip += 1
            else:
                print(f"  ⚠ {name}: {status} - {test.get('error', '')}")
        
        if "error" in stage_result:
            print(f"  Stage Error: {stage_result['error']}")
    
    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {total_pass} PASS, {total_fail} FAIL, {total_skip} SKIP")
    print(f"Success Rate: {total_pass / (total_pass + total_fail) * 100:.1f}%" if (total_pass + total_fail) > 0 else "N/A")
    print("=" * 60)
    
    # Save detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results,
        "summary": {
            "total_pass": total_pass,
            "total_fail": total_fail,
            "total_skip": total_skip,
            "success_rate": total_pass / (total_pass + total_fail) * 100 if (total_pass + total_fail) > 0 else 0
        }
    }
    
    with open("test_report_final.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
    print(f"Detailed report saved to: test_report_final.json")
    
    return total_fail == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)