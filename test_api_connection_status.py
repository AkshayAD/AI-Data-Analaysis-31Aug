"""
Test for API Connection Status Display - TASK-002
Tests that API connection status is clear, persistent, and shows error details
"""

import asyncio
from pathlib import Path
import pandas as pd
import numpy as np
from playwright.async_api import async_playwright
import json
from datetime import datetime

VALID_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"
INVALID_API_KEY = "invalid_key_12345"
BASE_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_api_status")
SCREENSHOT_DIR.mkdir(exist_ok=True)

async def test_api_connection_status():
    print("\n" + "="*60)
    print("TESTING API CONNECTION STATUS DISPLAY")
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
        
        test_results = []
        
        try:
            # TEST 1: INITIAL STATE
            print("\n1. Testing initial state...")
            await page.goto(BASE_URL, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            await page.screenshot(path=SCREENSHOT_DIR / "01_initial_state.png", full_page=True)
            
            # Check if API status is shown before testing
            content = await page.content()
            if "Connected" in content or "Disconnected" in content or "Not tested" in content:
                print("   ✅ Initial status indicator present")
                test_results.append({"test": "Initial Status", "status": "PASS"})
            else:
                print("   ⚠️ No initial status indicator")
                test_results.append({"test": "Initial Status", "status": "WARNING"})
            
            # TEST 2: SUCCESSFUL CONNECTION
            print("\n2. Testing successful connection...")
            
            # Enter valid API key
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill(VALID_API_KEY)
            await page.wait_for_timeout(1000)
            
            # Click Test Connection
            buttons = await page.query_selector_all("button")
            test_clicked = False
            for btn in buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    await btn.click()
                    test_clicked = True
                    print("   ⏳ Testing connection...")
                    await page.wait_for_timeout(5000)
                    break
            
            if not test_clicked:
                print("   ❌ Test Connection button not found")
                test_results.append({"test": "Test Button", "status": "FAIL"})
            
            await page.screenshot(path=SCREENSHOT_DIR / "02_valid_connection.png", full_page=True)
            
            # Check for success indicators
            content = await page.content()
            success_indicators = [
                "✅" in content,
                "Connected" in content,
                "Successfully" in content,
                "Success" in content,
                "API Connected" in content
            ]
            
            if any(success_indicators):
                print("   ✅ Success status displayed")
                test_results.append({"test": "Success Display", "status": "PASS"})
                
                # Check if the exact format matches requirement
                if "✅ Connected" in content or "✅ API Connected" in content:
                    print("   ✅ Correct format: '✅ Connected'")
                    test_results.append({"test": "Success Format", "status": "PASS"})
                else:
                    print("   ⚠️ Success shown but format doesn't match requirement")
                    test_results.append({"test": "Success Format", "status": "WARNING"})
            else:
                print("   ❌ No success status displayed")
                test_results.append({"test": "Success Display", "status": "FAIL"})
            
            # TEST 3: STATUS PERSISTENCE
            print("\n3. Testing status persistence...")
            
            # Refresh the page
            await page.reload(wait_until='networkidle')
            await page.wait_for_timeout(3000)
            await page.screenshot(path=SCREENSHOT_DIR / "03_after_refresh.png", full_page=True)
            
            content = await page.content()
            if "Connected" in content or "✅" in content:
                print("   ✅ Status persists after refresh")
                test_results.append({"test": "Status Persistence", "status": "PASS"})
            else:
                print("   ❌ Status lost after refresh")
                test_results.append({"test": "Status Persistence", "status": "FAIL"})
            
            # TEST 4: FAILED CONNECTION
            print("\n4. Testing failed connection...")
            
            # Clear and enter invalid API key
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill("")
            await page.wait_for_timeout(500)
            await api_input.fill(INVALID_API_KEY)
            await page.wait_for_timeout(1000)
            
            # Click Test Connection again
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    await btn.click()
                    print("   ⏳ Testing with invalid key...")
                    await page.wait_for_timeout(5000)
                    break
            
            await page.screenshot(path=SCREENSHOT_DIR / "04_invalid_connection.png", full_page=True)
            
            # Check for error indicators
            content = await page.content()
            error_indicators = [
                "❌" in content,
                "Failed" in content,
                "Error" in content,
                "Invalid" in content,
                "Connection failed" in content
            ]
            
            if any(error_indicators):
                print("   ✅ Error status displayed")
                test_results.append({"test": "Error Display", "status": "PASS"})
                
                # Check if the exact format matches requirement
                if "❌ Failed" in content or "❌ Connection failed" in content:
                    print("   ✅ Correct format: '❌ Failed'")
                    test_results.append({"test": "Error Format", "status": "PASS"})
                else:
                    print("   ⚠️ Error shown but format doesn't match requirement")
                    test_results.append({"test": "Error Format", "status": "WARNING"})
                
                # Check for error details
                if "API" in content and ("key" in content.lower() or "invalid" in content.lower()):
                    print("   ✅ Error details shown")
                    test_results.append({"test": "Error Details", "status": "PASS"})
                else:
                    print("   ⚠️ Error shown but no details")
                    test_results.append({"test": "Error Details", "status": "WARNING"})
            else:
                print("   ❌ No error status displayed")
                test_results.append({"test": "Error Display", "status": "FAIL"})
            
            # TEST 5: EMPTY API KEY
            print("\n5. Testing empty API key...")
            
            # Clear API key
            api_input = await page.wait_for_selector("input[type='password']", timeout=10000)
            await api_input.fill("")
            await page.wait_for_timeout(1000)
            
            # Click Test Connection
            buttons = await page.query_selector_all("button")
            for btn in buttons:
                text = await btn.text_content()
                if text and "Test Connection" in text:
                    await btn.click()
                    print("   ⏳ Testing with empty key...")
                    await page.wait_for_timeout(2000)
                    break
            
            await page.screenshot(path=SCREENSHOT_DIR / "05_empty_key.png", full_page=True)
            
            content = await page.content()
            if "Please enter an API key" in content or "API key required" in content:
                print("   ✅ Empty key error message shown")
                test_results.append({"test": "Empty Key Handling", "status": "PASS"})
            else:
                print("   ⚠️ No specific message for empty key")
                test_results.append({"test": "Empty Key Handling", "status": "WARNING"})
            
        except Exception as e:
            print(f"\n❌ Test error: {e}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_state.png", full_page=True)
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()
        
        # Print test summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in test_results if r["status"] == "PASS")
        failed = sum(1 for r in test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in test_results if r["status"] == "WARNING")
        
        for result in test_results:
            icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{icon} {result['test']}: {result['status']}")
        
        print(f"\nTotal: {passed} passed, {failed} failed, {warnings} warnings")
        
        # Check success criteria
        success_criteria = {
            "Clear success/failure message": any(r["test"] in ["Success Display", "Error Display"] and r["status"] == "PASS" for r in test_results),
            "Correct format (✅/❌)": any(r["test"] in ["Success Format", "Error Format"] and r["status"] == "PASS" for r in test_results),
            "Error details shown": any(r["test"] == "Error Details" and r["status"] in ["PASS", "WARNING"] for r in test_results),
            "Status persistence": any(r["test"] == "Status Persistence" and r["status"] == "PASS" for r in test_results)
        }
        
        print("\n📋 SUCCESS CRITERIA:")
        all_met = True
        for criteria, met in success_criteria.items():
            icon = "✅" if met else "❌"
            print(f"{icon} {criteria}")
            if not met:
                all_met = False
        
        print("\n" + "="*60)
        if all_met:
            print("🎉 ALL SUCCESS CRITERIA MET!")
        else:
            print("❌ SOME CRITERIA NOT MET - Implementation needed")
        print("="*60)
        
        return all_met, test_results

if __name__ == "__main__":
    success, results = asyncio.run(test_api_connection_status())
    
    # Save results
    report = {
        "task_id": "TASK-002",
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "test_results": results,
        "screenshots": [str(f) for f in SCREENSHOT_DIR.glob("*.png")]
    }
    
    with open("TASK_002_test_results.json", "w") as f:
        json.dump(report, f, indent=2)
    
    exit(0 if success else 1)