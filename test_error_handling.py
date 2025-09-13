#!/usr/bin/env python3
"""
Test script for error handling improvements in the AI Analysis Platform
Tests TASK-004: Comprehensive error handling with retry logic and user-friendly messages
"""

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
import json
from datetime import datetime

# Configuration
APP_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_error_handling")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Test scenarios
TEST_SCENARIOS = {
    "invalid_api_key": {
        "api_key": "invalid_key_12345",
        "expected_error": "Invalid API key",
        "expected_action": "Get a valid API key"
    },
    "empty_api_key": {
        "api_key": "",
        "expected_error": "No API key",
        "expected_action": "enter an API key"
    },
    "malformed_csv": {
        "file_content": "broken,csv\n,data",
        "expected_error": "File Error",
        "expected_action": None
    },
    "no_data_for_plan": {
        "skip_upload": True,
        "expected_error": "No data uploaded",
        "expected_action": "upload data"
    },
    "no_objective_for_plan": {
        "skip_objective": True,
        "expected_error": "No business objective",
        "expected_action": "add your objective"
    }
}

async def test_api_connection_error(page: Page, scenario_name: str, api_key: str):
    """Test API connection error handling"""
    print(f"\n📝 Testing API connection error: {scenario_name}")
    
    # Navigate to app
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Enter API key
    await page.fill('input[type="password"]', api_key)
    
    # Click Test Connection
    await page.click('button:has-text("Test Connection")')
    
    # Wait for error message
    await page.wait_for_timeout(3000)
    
    # Capture screenshot
    screenshot_path = SCREENSHOT_DIR / f"api_error_{scenario_name}.png"
    await page.screenshot(path=str(screenshot_path))
    print(f"  📸 Screenshot saved: {screenshot_path}")
    
    # Check for error elements
    error_messages = await page.query_selector_all('.stAlert')
    if error_messages:
        print(f"  ✅ Error message displayed")
        
        # Check for error details expander
        expanders = await page.query_selector_all('[data-testid="stExpander"]')
        for expander in expanders:
            text = await expander.inner_text()
            if "Error Details" in text:
                print(f"  ✅ Error details expander found")
                await expander.click()
                await page.wait_for_timeout(1000)
                
                # Capture expanded error details
                detail_screenshot = SCREENSHOT_DIR / f"api_error_{scenario_name}_details.png"
                await page.screenshot(path=str(detail_screenshot))
                print(f"  📸 Error details screenshot: {detail_screenshot}")
                break
    else:
        print(f"  ❌ No error message found")
    
    return len(error_messages) > 0

async def test_file_upload_error(page: Page):
    """Test file upload error handling"""
    print(f"\n📝 Testing file upload error handling")
    
    # Navigate to app
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Create a malformed CSV file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("")  # Empty file
        temp_file = f.name
    
    try:
        # Upload the malformed file
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(temp_file)
            await page.wait_for_timeout(2000)
            
            # Check for error message
            error_messages = await page.query_selector_all('.stAlert')
            
            # Capture screenshot
            screenshot_path = SCREENSHOT_DIR / "file_upload_error.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"  📸 Screenshot saved: {screenshot_path}")
            
            if error_messages:
                print(f"  ✅ File upload error handled gracefully")
                return True
            else:
                print(f"  ⚠️ No error message for empty file")
                return False
    finally:
        # Clean up temp file
        os.unlink(temp_file)

async def test_plan_generation_validation(page: Page):
    """Test plan generation validation errors"""
    print(f"\n📝 Testing plan generation validation")
    
    # Navigate to app
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Navigate to Stage 1 without uploading data
    await page.click('button:has-text("🎯 Plan Generation")')
    await page.wait_for_timeout(2000)
    
    # Try to generate plan without prerequisites
    generate_button = await page.query_selector('button:has-text("Generate AI Plan")')
    if generate_button:
        await generate_button.click()
        await page.wait_for_timeout(2000)
        
        # Check for validation error
        error_messages = await page.query_selector_all('.stAlert')
        
        # Capture screenshot
        screenshot_path = SCREENSHOT_DIR / "plan_validation_error.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        if error_messages:
            error_text = await error_messages[0].inner_text()
            if "No API key" in error_text or "No data" in error_text:
                print(f"  ✅ Validation error displayed: {error_text[:50]}...")
                return True
        
    print(f"  ❌ Validation not working properly")
    return False

async def test_retry_logic_display(page: Page):
    """Test that retry logic is visible to users"""
    print(f"\n📝 Testing retry logic visibility")
    
    # This test checks if the retry count is displayed after multiple failures
    # We'll use an invalid API key to trigger retries
    
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Enter invalid API key
    await page.fill('input[type="password"]', 'invalid_key_retry_test')
    
    # Test connection multiple times
    for i in range(2):
        await page.click('button:has-text("Test Connection")')
        await page.wait_for_timeout(4000)  # Wait for retry logic
    
    # Look for retry count indication
    screenshot_path = SCREENSHOT_DIR / "retry_logic_display.png"
    await page.screenshot(path=str(screenshot_path))
    print(f"  📸 Screenshot saved: {screenshot_path}")
    
    # Check if error details show retry information
    expanders = await page.query_selector_all('[data-testid="stExpander"]')
    for expander in expanders:
        text = await expander.inner_text()
        if "Error Details" in text:
            await expander.click()
            await page.wait_for_timeout(1000)
            
            # Check for technical details checkbox
            checkboxes = await page.query_selector_all('input[type="checkbox"]')
            for checkbox in checkboxes:
                parent = await checkbox.evaluate_handle('el => el.parentElement.parentElement')
                label_text = await parent.inner_text()
                if "technical details" in label_text.lower():
                    print(f"  ✅ Technical details option available")
                    await checkbox.click()
                    await page.wait_for_timeout(1000)
                    
                    # Capture technical details
                    detail_screenshot = SCREENSHOT_DIR / "technical_details.png"
                    await page.screenshot(path=str(detail_screenshot))
                    print(f"  📸 Technical details screenshot: {detail_screenshot}")
                    return True
    
    print(f"  ⚠️ Retry information not clearly visible")
    return False

async def test_chat_error_handling(page: Page):
    """Test chat functionality error handling"""
    print(f"\n📝 Testing chat error handling")
    
    # Navigate to app and go to Plan Generation stage
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Navigate to Stage 1
    await page.click('button:has-text("🎯 Plan Generation")')
    await page.wait_for_timeout(2000)
    
    # Try to send a chat message without API key
    chat_input = await page.query_selector('input[placeholder*="Ask a question"]')
    if chat_input:
        await chat_input.fill("Test question without setup")
        
        send_button = await page.query_selector('button:has-text("Send")')
        if send_button:
            await send_button.click()
            await page.wait_for_timeout(2000)
            
            # Check for error message
            error_messages = await page.query_selector_all('.stAlert')
            
            # Capture screenshot
            screenshot_path = SCREENSHOT_DIR / "chat_error_handling.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"  📸 Screenshot saved: {screenshot_path}")
            
            if error_messages:
                error_text = await error_messages[0].inner_text()
                if "No API key" in error_text or "Validation Error" in error_text:
                    print(f"  ✅ Chat validation error displayed")
                    return True
    
    print(f"  ❌ Chat error handling not working")
    return False

async def test_insights_error_handling(page: Page):
    """Test AI insights generation error handling"""
    print(f"\n📝 Testing AI insights error handling")
    
    # Navigate to app
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Upload test data first
    import tempfile
    import pandas as pd
    import numpy as np
    
    # Create test data
    np.random.seed(42)
    test_df = pd.DataFrame({
        'column1': np.random.randn(100),
        'column2': np.random.choice(['A', 'B', 'C'], 100),
        'column3': np.random.randint(1, 100, 100)
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        test_df.to_csv(f, index=False)
        temp_file = f.name
    
    try:
        # Upload file
        file_input = await page.query_selector('input[type="file"]')
        if file_input:
            await file_input.set_input_files(temp_file)
            await page.wait_for_timeout(2000)
        
        # Navigate to Stage 2
        await page.click('button:has-text("📊 Data Understanding")')
        await page.wait_for_timeout(2000)
        
        # Click AI Insights tab
        tabs = await page.query_selector_all('[role="tab"]')
        for tab in tabs:
            text = await tab.inner_text()
            if "AI Insights" in text:
                await tab.click()
                await page.wait_for_timeout(1000)
                break
        
        # Try to generate insights without API key
        generate_button = await page.query_selector('button:has-text("Generate AI Insights")')
        if generate_button:
            await generate_button.click()
            await page.wait_for_timeout(3000)
            
            # Check for error message
            error_messages = await page.query_selector_all('.stAlert')
            
            # Capture screenshot
            screenshot_path = SCREENSHOT_DIR / "insights_error_handling.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"  📸 Screenshot saved: {screenshot_path}")
            
            if error_messages:
                error_text = await error_messages[0].inner_text()
                if "No API key" in error_text or "Validation Error" in error_text:
                    print(f"  ✅ Insights validation error displayed")
                    return True
    
    finally:
        os.unlink(temp_file)
    
    print(f"  ❌ Insights error handling not working")
    return False

async def run_all_tests():
    """Run all error handling tests"""
    print("=" * 60)
    print("🧪 ERROR HANDLING TEST SUITE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"App URL: {APP_URL}")
    print(f"Screenshot Directory: {SCREENSHOT_DIR}")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        tests = [
            ("API Connection - Invalid Key", lambda page: test_api_connection_error(page, "invalid_key", "invalid_test_key_123")),
            ("API Connection - Empty Key", lambda page: test_api_connection_error(page, "empty_key", "")),
            ("File Upload Error", test_file_upload_error),
            ("Plan Generation Validation", test_plan_generation_validation),
            ("Retry Logic Display", test_retry_logic_display),
            ("Chat Error Handling", test_chat_error_handling),
            ("AI Insights Error Handling", test_insights_error_handling)
        ]
        
        for test_name, test_func in tests:
            page = await context.new_page()
            try:
                print(f"\n{'='*40}")
                print(f"Running: {test_name}")
                print(f"{'='*40}")
                
                result = await test_func(page)
                
                results["tests"].append({
                    "name": test_name,
                    "passed": result,
                    "timestamp": datetime.now().isoformat()
                })
                
                results["summary"]["total"] += 1
                if result:
                    results["summary"]["passed"] += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    results["summary"]["failed"] += 1
                    print(f"❌ {test_name}: FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
                results["tests"].append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                results["summary"]["total"] += 1
                results["summary"]["failed"] += 1
            finally:
                await page.close()
        
        await browser.close()
    
    # Save results
    results_file = SCREENSHOT_DIR / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']} ✅")
    print(f"Failed: {results['summary']['failed']} ❌")
    print(f"Success Rate: {results['summary']['passed']/results['summary']['total']*100:.1f}%")
    print(f"\nResults saved to: {results_file}")
    print(f"Screenshots saved in: {SCREENSHOT_DIR}/")
    print("=" * 60)
    
    return results['summary']['failed'] == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)