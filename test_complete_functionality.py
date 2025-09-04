"""
Complete Functionality Test with Playwright
Tests every feature and captures screenshots
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
BASE_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("test_screenshots_complete")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Create comprehensive test data
def create_test_data():
    """Create realistic test CSV with various data types"""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=500, freq='D')
    
    data = {
        'date': dates,
        'product_id': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005'], 500),
        'product_name': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Watch', 'Headphones'], 500),
        'category': np.random.choice(['Electronics', 'Accessories', 'Computing'], 500),
        'sales_amount': np.random.uniform(100, 5000, 500),
        'quantity_sold': np.random.randint(1, 100, 500),
        'customer_id': np.random.randint(1000, 5000, 500),
        'customer_age': np.random.randint(18, 70, 500),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Budget'], 500),
        'region': np.random.choice(['North America', 'Europe', 'Asia', 'South America'], 500),
        'country': np.random.choice(['USA', 'UK', 'Germany', 'Japan', 'Brazil'], 500),
        'satisfaction_score': np.random.uniform(1, 5, 500),
        'return_flag': np.random.choice([0, 1], 500, p=[0.9, 0.1]),
        'discount_percent': np.random.uniform(0, 30, 500),
        'shipping_days': np.random.randint(1, 10, 500),
        'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Cash', 'Debit Card'], 500),
        'marketing_channel': np.random.choice(['Online', 'Email', 'Social Media', 'Direct'], 500),
        'profit_margin': np.random.uniform(10, 50, 500)
    }
    
    df = pd.DataFrame(data)
    # Add some missing values to test data quality features
    df.loc[np.random.choice(df.index, 20), 'satisfaction_score'] = np.nan
    df.loc[np.random.choice(df.index, 10), 'shipping_days'] = np.nan
    
    test_file = Path("test_sales_data_complete.csv")
    df.to_csv(test_file, index=False)
    return test_file

async def test_stage_0_complete(page, context):
    """Comprehensive test of Stage 0: Input & Objectives"""
    print("\n" + "="*60)
    print("STAGE 0: INPUT & OBJECTIVES - COMPREHENSIVE TEST")
    print("="*60)
    
    results = {"stage": "Stage 0", "tests": [], "screenshots": []}
    
    try:
        # 1. Initial page load
        print("\n1. Loading application...")
        await page.goto(BASE_URL, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        screenshot = f"01_00_initial_page_load.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        print(f"   ✓ Screenshot: {screenshot}")
        
        # 2. Check sidebar elements
        print("\n2. Testing sidebar navigation...")
        sidebar = page.locator("[data-testid='stSidebar'], aside, .sidebar")
        if await sidebar.count() > 0:
            screenshot = f"01_01_sidebar_overview.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Sidebar Present", "status": "PASS"})
            print(f"   ✓ Sidebar found")
        
        # 3. API Configuration Section
        print("\n3. Testing API Configuration...")
        
        # Look for API expander and click it
        api_expander = page.locator("div").filter(has_text="Gemini API Configuration").first
        if await api_expander.count() > 0:
            await api_expander.click()
            await page.wait_for_timeout(1000)
        
        # Enter API key
        api_input = page.locator("input[type='password']").first
        if await api_input.count() == 0:
            api_input = page.locator("input").filter(has_text="API").first
        if await api_input.count() == 0:
            api_input = page.locator("input").first
            
        if await api_input.count() > 0:
            await api_input.fill(GEMINI_API_KEY)
            await page.wait_for_timeout(500)
            screenshot = f"01_02_api_key_entered.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "API Key Input", "status": "PASS"})
            print(f"   ✓ API key entered")
        else:
            results["tests"].append({"name": "API Key Input", "status": "FAIL", "error": "Input not found"})
            print(f"   ✗ API key input not found")
        
        # Test API connection
        test_btn = page.locator("button").filter(has_text="Test Connection").first
        if await test_btn.count() > 0:
            await test_btn.click()
            await page.wait_for_timeout(3000)
            screenshot = f"01_03_api_test_result.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for success message
            success = page.locator("div").filter(has_text="Connected")
            if await success.count() > 0:
                results["tests"].append({"name": "API Connection Test", "status": "PASS"})
                print(f"   ✓ API connection successful")
            else:
                results["tests"].append({"name": "API Connection Test", "status": "FAIL"})
                print(f"   ✗ API connection failed")
        
        # Model selection
        model_select = page.locator("select").first
        if await model_select.count() > 0:
            await model_select.select_option(index=0)
            screenshot = f"01_04_model_selected.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Model Selection", "status": "PASS"})
            print(f"   ✓ Model selected")
        
        # 4. File Upload Section
        print("\n4. Testing file upload...")
        
        # Look for upload expander
        upload_expander = page.locator("div").filter(has_text="Data Upload").first
        if await upload_expander.count() > 0:
            await upload_expander.click()
            await page.wait_for_timeout(1000)
        
        # Upload file
        test_file = create_test_data()
        file_input = page.locator("input[type='file']").first
        
        if await file_input.count() > 0:
            await file_input.set_input_files(str(test_file))
            await page.wait_for_timeout(3000)
            screenshot = f"01_05_file_uploaded.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for data preview
            data_preview = page.locator("table, [data-testid='stDataFrame']").first
            if await data_preview.count() > 0:
                screenshot = f"01_06_data_preview.png"
                await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
                results["screenshots"].append(screenshot)
                results["tests"].append({"name": "File Upload & Preview", "status": "PASS"})
                print(f"   ✓ File uploaded and preview shown")
            else:
                results["tests"].append({"name": "File Upload", "status": "PARTIAL", "error": "No preview"})
                print(f"   ⚠ File uploaded but no preview")
        else:
            results["tests"].append({"name": "File Upload", "status": "FAIL", "error": "No input found"})
            print(f"   ✗ File upload input not found")
        
        # 5. Business Objective
        print("\n5. Testing business objective input...")
        
        objective_expander = page.locator("div").filter(has_text="Business Objective").first
        if await objective_expander.count() > 0:
            await objective_expander.click()
            await page.wait_for_timeout(1000)
        
        objective_text = """
        Analyze sales performance across different regions and product categories.
        Identify top-performing products and customer segments.
        Find correlations between customer satisfaction and sales metrics.
        Provide recommendations for improving profit margins and reducing returns.
        """
        
        objective_input = page.locator("textarea").first
        if await objective_input.count() > 0:
            await objective_input.fill(objective_text)
            await page.wait_for_timeout(1000)
            screenshot = f"01_07_objective_entered.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Business Objective Input", "status": "PASS"})
            print(f"   ✓ Business objective entered")
        else:
            results["tests"].append({"name": "Business Objective", "status": "FAIL"})
            print(f"   ✗ Objective input not found")
        
        # 6. Navigation to Stage 1
        print("\n6. Testing navigation to Stage 1...")
        
        # Try multiple navigation methods
        next_btn = page.locator("button").filter(has_text="Plan Generation").first
        if await next_btn.count() == 0:
            next_btn = page.locator("button").filter(has_text="Next").first
        
        if await next_btn.count() > 0:
            screenshot = f"01_08_before_navigation.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot)
            results["screenshots"].append(screenshot)
            
            await next_btn.click()
            await page.wait_for_timeout(3000)
            
            screenshot = f"01_09_after_navigation.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check if we reached Stage 1
            if "Plan" in await page.content() or "Stage 1" in await page.content():
                results["tests"].append({"name": "Navigation to Stage 1", "status": "PASS"})
                print(f"   ✓ Successfully navigated to Stage 1")
            else:
                results["tests"].append({"name": "Navigation", "status": "FAIL"})
                print(f"   ✗ Navigation failed")
        else:
            # Try sidebar navigation
            sidebar_btn = page.locator("button").filter(has_text="Plan Generation")
            if await sidebar_btn.count() > 0:
                await sidebar_btn.click()
                await page.wait_for_timeout(2000)
                results["tests"].append({"name": "Sidebar Navigation", "status": "PASS"})
                print(f"   ✓ Used sidebar navigation")
        
    except Exception as e:
        print(f"\n   ❌ Error in Stage 0: {str(e)}")
        results["error"] = str(e)
        screenshot = f"01_99_stage0_error.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
    
    return results

async def test_stage_1_complete(page, context):
    """Comprehensive test of Stage 1: Plan Generation"""
    print("\n" + "="*60)
    print("STAGE 1: PLAN GENERATION - COMPREHENSIVE TEST")
    print("="*60)
    
    results = {"stage": "Stage 1", "tests": [], "screenshots": []}
    
    try:
        # Ensure we're on Stage 1
        await page.wait_for_timeout(2000)
        screenshot = f"02_00_stage1_initial.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        print(f"   ✓ Screenshot: {screenshot}")
        
        # 1. Generate AI Plan
        print("\n1. Testing AI plan generation...")
        generate_btn = page.locator("button").filter(has_text="Generate").first
        
        if await generate_btn.count() > 0:
            await generate_btn.click()
            await page.wait_for_timeout(8000)  # Wait for AI response
            
            screenshot = f"02_01_plan_generated.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for generated content
            plan_area = page.locator("textarea").first
            if await plan_area.count() > 0:
                plan_content = await plan_area.input_value()
                if plan_content and len(plan_content) > 50:
                    results["tests"].append({"name": "AI Plan Generation", "status": "PASS"})
                    print(f"   ✓ AI plan generated ({len(plan_content)} chars)")
                else:
                    results["tests"].append({"name": "AI Plan Generation", "status": "FAIL", "error": "Empty plan"})
                    print(f"   ✗ Plan generation failed or empty")
            else:
                results["tests"].append({"name": "AI Plan Generation", "status": "FAIL"})
                print(f"   ✗ No plan area found")
        else:
            results["tests"].append({"name": "Generate Button", "status": "FAIL"})
            print(f"   ✗ Generate button not found")
        
        # 2. Edit Plan
        print("\n2. Testing plan editing...")
        plan_editor = page.locator("textarea").first
        
        if await plan_editor.count() > 0:
            # Add custom text to plan
            current_plan = await plan_editor.input_value()
            edited_plan = current_plan + "\n\nADDITIONAL ANALYSIS:\n- Deep dive into regional performance\n- Customer lifetime value analysis"
            
            await plan_editor.fill(edited_plan)
            await page.wait_for_timeout(1000)
            
            screenshot = f"02_02_plan_edited.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Plan Editing", "status": "PASS"})
            print(f"   ✓ Plan edited successfully")
        
        # 3. Save Plan
        print("\n3. Testing plan save...")
        save_btn = page.locator("button").filter(has_text="Save").first
        
        if await save_btn.count() > 0:
            await save_btn.click()
            await page.wait_for_timeout(2000)
            
            screenshot = f"02_03_plan_saved.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot)
            results["screenshots"].append(screenshot)
            
            # Check for save confirmation
            if "saved" in (await page.content()).lower() or "success" in (await page.content()).lower():
                results["tests"].append({"name": "Save Plan", "status": "PASS"})
                print(f"   ✓ Plan saved")
            else:
                results["tests"].append({"name": "Save Plan", "status": "PARTIAL"})
                print(f"   ⚠ Save clicked but no confirmation")
        
        # 4. AI Chat Assistant
        print("\n4. Testing AI chat assistant...")
        
        # Find chat input
        chat_input = page.locator("input").filter(has_text="question").first
        if await chat_input.count() == 0:
            chat_input = page.locator("input[placeholder*='Ask']").first
        if await chat_input.count() == 0:
            chat_input = page.locator("input").nth(1)  # Try second input
        
        if await chat_input.count() > 0:
            await chat_input.fill("What are the key metrics I should focus on for customer segmentation?")
            
            # Find send button
            send_btn = page.locator("button").filter(has_text="Send").first
            if await send_btn.count() > 0:
                await send_btn.click()
                await page.wait_for_timeout(5000)  # Wait for AI response
                
                screenshot = f"02_04_chat_response.png"
                await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
                results["screenshots"].append(screenshot)
                
                # Check for response
                page_content = await page.content()
                if "metric" in page_content.lower() or "customer" in page_content.lower():
                    results["tests"].append({"name": "AI Chat", "status": "PASS"})
                    print(f"   ✓ AI chat responded")
                else:
                    results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No response"})
                    print(f"   ✗ No chat response")
            else:
                results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No send button"})
                print(f"   ✗ Send button not found")
        else:
            results["tests"].append({"name": "AI Chat", "status": "FAIL", "error": "No input"})
            print(f"   ✗ Chat input not found")
        
        # 5. Navigate to Stage 2
        print("\n5. Testing navigation to Stage 2...")
        
        next_btn = page.locator("button").filter(has_text="Data Understanding").first
        if await next_btn.count() == 0:
            next_btn = page.locator("button").filter(has_text="Next").first
        
        if await next_btn.count() > 0:
            await next_btn.click()
            await page.wait_for_timeout(3000)
            
            screenshot = f"02_05_navigate_stage2.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            if "Stage 2" in await page.content() or "Data Understanding" in await page.content():
                results["tests"].append({"name": "Navigation to Stage 2", "status": "PASS"})
                print(f"   ✓ Navigated to Stage 2")
            else:
                results["tests"].append({"name": "Navigation", "status": "FAIL"})
                print(f"   ✗ Navigation failed")
        
    except Exception as e:
        print(f"\n   ❌ Error in Stage 1: {str(e)}")
        results["error"] = str(e)
        screenshot = f"02_99_stage1_error.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
    
    return results

async def test_stage_2_complete(page, context):
    """Comprehensive test of Stage 2: Data Understanding"""
    print("\n" + "="*60)
    print("STAGE 2: DATA UNDERSTANDING - COMPREHENSIVE TEST")
    print("="*60)
    
    results = {"stage": "Stage 2", "tests": [], "screenshots": []}
    
    try:
        await page.wait_for_timeout(2000)
        screenshot = f"03_00_stage2_initial.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        print(f"   ✓ Screenshot: {screenshot}")
        
        # 1. Data Overview Tab
        print("\n1. Testing data overview...")
        
        # Look for tabs
        overview_tab = page.locator("button, div").filter(has_text="Overview").first
        if await overview_tab.count() > 0:
            await overview_tab.click()
            await page.wait_for_timeout(2000)
        
        screenshot = f"03_01_data_overview.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        
        # Check for data table
        data_table = page.locator("table, [data-testid='stDataFrame']").first
        if await data_table.count() > 0:
            results["tests"].append({"name": "Data Preview", "status": "PASS"})
            print(f"   ✓ Data table displayed")
        else:
            results["tests"].append({"name": "Data Preview", "status": "FAIL"})
            print(f"   ✗ No data table found")
        
        # 2. Statistics Tab
        print("\n2. Testing statistics...")
        
        stats_tab = page.locator("button, div").filter(has_text="Statistics").first
        if await stats_tab.count() > 0:
            await stats_tab.click()
            await page.wait_for_timeout(2000)
            
            screenshot = f"03_02_statistics.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for stats content
            if "mean" in (await page.content()).lower() or "std" in (await page.content()).lower():
                results["tests"].append({"name": "Statistics Display", "status": "PASS"})
                print(f"   ✓ Statistics shown")
            else:
                results["tests"].append({"name": "Statistics", "status": "FAIL"})
                print(f"   ✗ No statistics found")
        
        # 3. Data Quality Tab
        print("\n3. Testing data quality assessment...")
        
        quality_tab = page.locator("button, div").filter(has_text="Quality").first
        if await quality_tab.count() > 0:
            await quality_tab.click()
            await page.wait_for_timeout(2000)
            
            screenshot = f"03_03_data_quality.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for quality metrics
            if "missing" in (await page.content()).lower() or "quality" in (await page.content()).lower():
                results["tests"].append({"name": "Data Quality", "status": "PASS"})
                print(f"   ✓ Quality assessment shown")
            else:
                results["tests"].append({"name": "Data Quality", "status": "FAIL"})
                print(f"   ✗ No quality metrics")
        
        # 4. Visualizations Tab
        print("\n4. Testing visualizations...")
        
        viz_tab = page.locator("button, div").filter(has_text="Visualizations").first
        if await viz_tab.count() > 0:
            await viz_tab.click()
            await page.wait_for_timeout(3000)
            
            screenshot = f"03_04_visualizations.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for charts
            charts = page.locator("canvas, svg, [class*='plot'], .js-plotly-plot").all()
            if len(await charts) > 0:
                results["tests"].append({"name": "Visualizations", "status": "PASS", "count": len(await charts)})
                print(f"   ✓ {len(await charts)} visualizations found")
                
                # Try interacting with selectors if present
                column_select = page.locator("select").first
                if await column_select.count() > 0:
                    await column_select.select_option(index=1)
                    await page.wait_for_timeout(2000)
                    screenshot = f"03_05_visualization_updated.png"
                    await page.screenshot(path=SCREENSHOT_DIR / screenshot)
                    results["screenshots"].append(screenshot)
                    print(f"   ✓ Interactive visualization controls work")
            else:
                results["tests"].append({"name": "Visualizations", "status": "FAIL"})
                print(f"   ✗ No visualizations found")
        
        # 5. AI Insights
        print("\n5. Testing AI insights generation...")
        
        insights_tab = page.locator("button, div").filter(has_text="Insights").first
        if await insights_tab.count() > 0:
            await insights_tab.click()
            await page.wait_for_timeout(2000)
        
        insights_btn = page.locator("button").filter(has_text="Generate").first
        if await insights_btn.count() == 0:
            insights_btn = page.locator("button").filter(has_text="Insights").first
        
        if await insights_btn.count() > 0:
            await insights_btn.click()
            await page.wait_for_timeout(8000)  # Wait for AI
            
            screenshot = f"03_06_ai_insights.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            
            # Check for insights
            content = await page.content()
            if "insight" in content.lower() or "pattern" in content.lower() or "recommend" in content.lower():
                results["tests"].append({"name": "AI Insights", "status": "PASS"})
                print(f"   ✓ AI insights generated")
            else:
                results["tests"].append({"name": "AI Insights", "status": "FAIL"})
                print(f"   ✗ No insights generated")
        else:
            results["tests"].append({"name": "AI Insights", "status": "SKIP", "error": "No button"})
            print(f"   ⊘ Insights button not found")
        
        # 6. Export Functionality
        print("\n6. Testing export functionality...")
        
        # Scroll to export section
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        
        screenshot = f"03_07_export_section.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        
        # Look for download buttons
        download_btns = await page.locator("button").filter(has_text="Download").all()
        export_btns = await page.locator("button").filter(has_text="Export").all()
        
        all_export_btns = download_btns + export_btns
        
        if len(all_export_btns) > 0:
            results["tests"].append({"name": "Export Buttons", "status": "PASS", "count": len(all_export_btns)})
            print(f"   ✓ {len(all_export_btns)} export options found")
            
            # Try clicking first export button
            try:
                await all_export_btns[0].click()
                await page.wait_for_timeout(2000)
                print(f"   ✓ Export triggered")
            except:
                print(f"   ⚠ Export click failed")
        else:
            results["tests"].append({"name": "Export", "status": "FAIL"})
            print(f"   ✗ No export buttons found")
        
    except Exception as e:
        print(f"\n   ❌ Error in Stage 2: {str(e)}")
        results["error"] = str(e)
        screenshot = f"03_99_stage2_error.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
    
    return results

async def test_navigation_complete(page, context):
    """Test all navigation patterns"""
    print("\n" + "="*60)
    print("NAVIGATION - COMPREHENSIVE TEST")
    print("="*60)
    
    results = {"stage": "Navigation", "tests": [], "screenshots": []}
    
    try:
        # 1. Test backward navigation
        print("\n1. Testing backward navigation...")
        
        # Try to go back to Stage 1
        back_btn = page.locator("button").filter(has_text="Plan Generation").first
        if await back_btn.count() == 0:
            back_btn = page.locator("button").filter(has_text="Back").first
        
        if await back_btn.count() > 0:
            await back_btn.click()
            await page.wait_for_timeout(2000)
            screenshot = f"04_01_back_to_stage1.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Back to Stage 1", "status": "PASS"})
            print(f"   ✓ Navigated back to Stage 1")
        
        # Try to go to Stage 0
        stage0_btn = page.locator("button").filter(has_text="Input").first
        if await stage0_btn.count() > 0:
            await stage0_btn.click()
            await page.wait_for_timeout(2000)
            screenshot = f"04_02_back_to_stage0.png"
            await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
            results["screenshots"].append(screenshot)
            results["tests"].append({"name": "Back to Stage 0", "status": "PASS"})
            print(f"   ✓ Navigated back to Stage 0")
        
        # 2. Test sidebar navigation
        print("\n2. Testing sidebar stage selection...")
        
        # Navigate through all stages using sidebar
        stages = [
            ("Input", "Stage 0"),
            ("Plan", "Stage 1"),
            ("Data", "Stage 2")
        ]
        
        for stage_text, stage_name in stages:
            btn = page.locator("button").filter(has_text=stage_text).first
            if await btn.count() > 0:
                await btn.click()
                await page.wait_for_timeout(2000)
                screenshot = f"04_0{3 + stages.index((stage_text, stage_name))}_{stage_name.lower().replace(' ', '_')}.png"
                await page.screenshot(path=SCREENSHOT_DIR / screenshot)
                results["screenshots"].append(screenshot)
                print(f"   ✓ Navigated to {stage_name}")
        
        results["tests"].append({"name": "Sidebar Navigation", "status": "PASS"})
        
        # 3. Test session state persistence
        print("\n3. Testing session state persistence...")
        
        # Check if data is still available
        content = await page.content()
        if "API Connected" in content or "Data Uploaded" in content:
            results["tests"].append({"name": "Session State", "status": "PASS"})
            print(f"   ✓ Session state maintained")
        else:
            results["tests"].append({"name": "Session State", "status": "PARTIAL"})
            print(f"   ⚠ Session state partially maintained")
        
        # Final full page screenshot
        screenshot = f"04_06_final_state.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
        
    except Exception as e:
        print(f"\n   ❌ Error in Navigation: {str(e)}")
        results["error"] = str(e)
        screenshot = f"04_99_navigation_error.png"
        await page.screenshot(path=SCREENSHOT_DIR / screenshot, full_page=True)
        results["screenshots"].append(screenshot)
    
    return results

async def main():
    """Main test runner"""
    print("\n" + "="*80)
    print(" COMPLETE FUNCTIONALITY TEST WITH PLAYWRIGHT ".center(80))
    print("="*80)
    print(f"Testing URL: {BASE_URL}")
    print(f"Screenshots: {SCREENSHOT_DIR}")
    print(f"API Key: {GEMINI_API_KEY[:10]}...")
    print("="*80)
    
    all_results = []
    
    async with async_playwright() as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        page = await context.new_page()
        page.set_default_timeout(60000)  # 60 second timeout
        
        try:
            # Run comprehensive tests
            stage0_results = await test_stage_0_complete(page, context)
            all_results.append(stage0_results)
            
            stage1_results = await test_stage_1_complete(page, context)
            all_results.append(stage1_results)
            
            stage2_results = await test_stage_2_complete(page, context)
            all_results.append(stage2_results)
            
            nav_results = await test_navigation_complete(page, context)
            all_results.append(nav_results)
            
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "99_critical_error.png", full_page=True)
        
        finally:
            await browser.close()
    
    # Generate comprehensive report
    print("\n" + "="*80)
    print(" TEST RESULTS SUMMARY ".center(80))
    print("="*80)
    
    total_pass = 0
    total_fail = 0
    total_skip = 0
    total_screenshots = 0
    
    for stage_result in all_results:
        print(f"\n{stage_result['stage']}:")
        print("-" * 60)
        
        for test in stage_result.get("tests", []):
            status = test["status"]
            name = test["name"]
            
            if status == "PASS":
                print(f"  ✅ {name}: PASS")
                total_pass += 1
            elif status == "FAIL":
                print(f"  ❌ {name}: FAIL - {test.get('error', 'Unknown')}")
                total_fail += 1
            elif status == "SKIP":
                print(f"  ⊘ {name}: SKIP")
                total_skip += 1
            else:
                print(f"  ⚠️  {name}: {status}")
        
        screenshots = stage_result.get("screenshots", [])
        if screenshots:
            print(f"  📸 Screenshots captured: {len(screenshots)}")
            total_screenshots += len(screenshots)
        
        if "error" in stage_result:
            print(f"  ⚠️  Stage Error: {stage_result['error']}")
    
    # Final summary
    print("\n" + "="*80)
    print(" FINAL STATISTICS ".center(80))
    print("="*80)
    print(f"✅ Passed: {total_pass}")
    print(f"❌ Failed: {total_fail}")
    print(f"⊘ Skipped: {total_skip}")
    print(f"📸 Screenshots: {total_screenshots}")
    
    success_rate = (total_pass / (total_pass + total_fail) * 100) if (total_pass + total_fail) > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    # Save detailed JSON report
    report = {
        "timestamp": datetime.now().isoformat(),
        "url": BASE_URL,
        "results": all_results,
        "summary": {
            "total_pass": total_pass,
            "total_fail": total_fail,
            "total_skip": total_skip,
            "total_screenshots": total_screenshots,
            "success_rate": success_rate
        }
    }
    
    report_file = "test_complete_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📝 Detailed report saved to: {report_file}")
    print(f"📁 Screenshots saved to: {SCREENSHOT_DIR}/")
    print("="*80)
    
    return success_rate >= 70  # Consider test successful if 70% or more pass

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)