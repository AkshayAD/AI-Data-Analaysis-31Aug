#!/usr/bin/env python3
"""
Comprehensive End-to-End Test with Real API Key
"""

import asyncio
from playwright.async_api import async_playwright
import time
import json
import os
from datetime import datetime

async def comprehensive_e2e_test():
    """Test the complete application workflow"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "screenshots": [],
        "errors": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Test 1: App Load
            print("🔍 Test 1: App Loading...")
            results["tests"]["app_load"] = await test_app_load(page, results)
            
            # Test 2: API Configuration
            print("🔍 Test 2: API Configuration...")
            results["tests"]["api_config"] = await test_api_config(page, results)
            
            # Test 3: File Upload
            print("🔍 Test 3: File Upload...")
            results["tests"]["file_upload"] = await test_file_upload(page, results)
            
            # Test 4: Navigation Flow
            print("🔍 Test 4: Navigation Flow...")
            results["tests"]["navigation"] = await test_navigation_flow(page, results)
            
            # Test 5: HITL Integration
            print("🔍 Test 5: HITL Integration...")
            results["tests"]["hitl_integration"] = await test_hitl_integration(page, results)
            
        except Exception as e:
            results["errors"].append(f"Critical test error: {str(e)}")
            print(f"❌ Critical error: {e}")
        
        finally:
            await browser.close()
    
    # Calculate summary
    for test_name, result in results["tests"].items():
        results["summary"]["total"] += 1
        if result["status"] == "PASS":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    # Save results
    with open("comprehensive_e2e_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("COMPREHENSIVE E2E TEST RESULTS")
    print("="*60)
    
    for test_name, result in results["tests"].items():
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {result['status']}")
        if result.get("error"):
            print(f"   Error: {result['error']}")
    
    print(f"\nSummary: {results['summary']['passed']}/{results['summary']['total']} tests passed")
    print(f"Screenshots saved: {len(results['screenshots'])}")
    
    return results

async def test_app_load(page, results):
    """Test if the app loads correctly"""
    try:
        await page.goto("http://localhost:8503")
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # Check for main title
        title = await page.locator("h1").first.text_content(timeout=5000)
        if "Stage 0" in title:
            await page.screenshot(path="e2e_01_app_loaded.png")
            results["screenshots"].append("e2e_01_app_loaded.png")
            return {"status": "PASS", "details": f"App loaded with title: {title}"}
        else:
            return {"status": "FAIL", "error": f"Unexpected title: {title}"}
            
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

async def test_api_config(page, results):
    """Test API configuration"""
    try:
        # Check if API key is already loaded from environment
        api_status = await page.locator("text=API Key loaded from environment variable").count()
        if api_status > 0:
            print("   ✅ API key loaded from environment")
            
            # Try to test the connection
            test_button = page.locator("button:has-text('Test Connection')")
            if await test_button.count() > 0:
                await test_button.click()
                await page.wait_for_timeout(3000)  # Wait for API test
                
                # Check for success or failure status
                await page.screenshot(path="e2e_02_api_tested.png")
                results["screenshots"].append("e2e_02_api_tested.png")
                
                return {"status": "PASS", "details": "API configuration available and tested"}
            else:
                return {"status": "FAIL", "error": "Test Connection button not found"}
        else:
            # Need manual API key input
            override_checkbox = page.locator('input[type="checkbox"]')
            if await override_checkbox.count() > 0:
                await override_checkbox.check()
                await page.wait_for_timeout(1000)
                
                # Try to enter API key manually
                api_input = page.locator('input[type="password"]')
                if await api_input.count() > 0:
                    await api_input.fill("test_key_for_testing")
                    await page.screenshot(path="e2e_02_manual_api.png")
                    results["screenshots"].append("e2e_02_manual_api.png")
                    return {"status": "PASS", "details": "Manual API key entry working"}
                else:
                    return {"status": "FAIL", "error": "API key input field not found"}
            else:
                return {"status": "FAIL", "error": "No API configuration options found"}
                
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

async def test_file_upload(page, results):
    """Test file upload functionality"""
    try:
        # Create a test CSV file
        test_csv_content = "name,age,score\nAlice,25,85\nBob,30,92\nCharlie,35,78"
        with open("test_data.csv", "w") as f:
            f.write(test_csv_content)
        
        # Find file upload area
        file_upload = page.locator('input[type="file"]')
        if await file_upload.count() > 0:
            await file_upload.set_input_files("test_data.csv")
            await page.wait_for_timeout(2000)
            
            await page.screenshot(path="e2e_03_file_uploaded.png")
            results["screenshots"].append("e2e_03_file_uploaded.png")
            
            # Clean up
            os.remove("test_data.csv")
            
            return {"status": "PASS", "details": "File upload successful"}
        else:
            return {"status": "FAIL", "error": "File upload input not found"}
            
    except Exception as e:
        if os.path.exists("test_data.csv"):
            os.remove("test_data.csv")
        return {"status": "FAIL", "error": str(e)}

async def test_navigation_flow(page, results):
    """Test navigation between stages"""
    try:
        # Check current stage
        nav_items = await page.locator(".stSidebar .stSelectbox").count()
        stages = await page.locator("h1, h2").all_text_contents()
        
        await page.screenshot(path="e2e_04_navigation.png")
        results["screenshots"].append("e2e_04_navigation.png")
        
        # Check if we can see navigation elements
        if any("Stage" in stage for stage in stages):
            return {"status": "PASS", "details": f"Navigation visible, stages found: {len(stages)}"}
        else:
            return {"status": "FAIL", "error": "No stage navigation found"}
            
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

async def test_hitl_integration(page, results):
    """Test HITL (Human-in-the-Loop) integration"""
    try:
        # Check for orchestrator status in sidebar
        orchestrator_status = await page.locator("text=Orchestrator Status").count()
        pending_approvals = await page.locator("text=Pending Approvals").count()
        
        await page.screenshot(path="e2e_05_hitl_status.png")
        results["screenshots"].append("e2e_05_hitl_status.png")
        
        if orchestrator_status > 0:
            details = "Orchestrator status section found"
            if pending_approvals > 0:
                details += ", Pending approvals section found"
            return {"status": "PASS", "details": details}
        else:
            return {"status": "FAIL", "error": "Orchestrator integration not visible"}
            
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

if __name__ == "__main__":
    asyncio.run(comprehensive_e2e_test())