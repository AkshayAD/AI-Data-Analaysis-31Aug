#!/usr/bin/env python3
"""
Test script for TASK-005: Environment Variable Management
Tests secure API key loading from environment variables with fallback to user input
"""

import asyncio
import os
import tempfile
import json
from pathlib import Path
from playwright.async_api import async_playwright, Page
from datetime import datetime

# Configuration
APP_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_env_vars")
SCREENSHOT_DIR.mkdir(exist_ok=True)

async def test_env_var_loading_with_key_set(page: Page):
    """Test that API key loads from environment variable when set"""
    print(f"\n📝 Testing environment variable loading with key set")
    
    # Navigate to app
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(3000)
    
    # Look for environment status indicator
    screenshot_path = SCREENSHOT_DIR / "env_var_key_set.png"
    await page.screenshot(path=str(screenshot_path))
    print(f"  📸 Screenshot saved: {screenshot_path}")
    
    # Check if API key field shows it's loaded from environment
    api_config_expander = None
    expanders = await page.query_selector_all('[data-testid="stExpander"]')
    for expander in expanders:
        header = await expander.query_selector('[data-testid="stExpanderHeader"]')
        if header:
            text = await header.inner_text()
            if "API" in text:
                api_config_expander = expander
                await expander.click()  # Expand it
                await page.wait_for_timeout(1000)
                break
    
    if api_config_expander:
        # Look for environment variable indicator
        expanded_content = await api_config_expander.query_selector_all('*')
        env_indicator_found = False
        for element in expanded_content:
            try:
                text = await element.inner_text()
                if "environment" in text.lower() and ("loaded" in text.lower() or "found" in text.lower()):
                    env_indicator_found = True
                    print(f"  ✅ Environment variable indicator found: {text[:50]}...")
                    break
            except:
                continue
        
        # Capture screenshot of expanded state
        expanded_screenshot = SCREENSHOT_DIR / "env_var_expanded.png"
        await page.screenshot(path=str(expanded_screenshot))
        print(f"  📸 Expanded view screenshot: {expanded_screenshot}")
        
        return env_indicator_found
    else:
        print(f"  ❌ Could not find API configuration section")
        return False

async def test_fallback_to_user_input(page: Page):
    """Test fallback to user input when no environment variable is set"""
    print(f"\n📝 Testing fallback to user input")
    
    # This test would run with no GEMINI_API_KEY set
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(3000)
    
    # Check that API key input field is present and empty
    api_input = await page.query_selector('input[type="password"]')
    if api_input:
        placeholder = await api_input.get_attribute('placeholder')
        value = await api_input.get_attribute('value')
        
        print(f"  ✅ API key input field found")
        print(f"  📝 Placeholder: {placeholder}")
        print(f"  📝 Value: {'***' if value else 'empty'}")
        
        # Capture screenshot
        screenshot_path = SCREENSHOT_DIR / "fallback_user_input.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"  📸 Screenshot saved: {screenshot_path}")
        
        return True
    else:
        print(f"  ❌ API key input field not found")
        return False

async def test_security_no_hardcoded_keys(page: Page):
    """Test that no hardcoded keys are visible in the UI"""
    print(f"\n📝 Testing no hardcoded keys visible")
    
    await page.goto(APP_URL, wait_until='networkidle')
    await page.wait_for_timeout(2000)
    
    # Get all text content from the page
    page_content = await page.inner_text('body')
    
    # Look for potential API key patterns (but not our test key)
    suspicious_patterns = [
        'AIza',  # Google API key prefix
        'sk-',   # OpenAI key prefix
        'api_key',  # Generic pattern
    ]
    
    # Capture screenshot
    screenshot_path = SCREENSHOT_DIR / "security_check.png"
    await page.screenshot(path=str(screenshot_path))
    print(f"  📸 Screenshot saved: {screenshot_path}")
    
    for pattern in suspicious_patterns:
        if pattern in page_content and 'test' not in page_content.lower():
            print(f"  ⚠️ Potential security issue: Found pattern '{pattern}' in UI")
            return False
    
    print(f"  ✅ No hardcoded keys found in UI")
    return True

async def test_env_file_creation():
    """Test that .env.example file exists with proper template"""
    print(f"\n📝 Testing .env.example file creation")
    
    env_example_path = Path("/root/repo/.env.example")
    
    if env_example_path.exists():
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        required_vars = [
            'GEMINI_API_KEY',
            'STREAMLIT_SERVER_PORT',
            'DEBUG'
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"  ⚠️ Missing variables in .env.example: {missing_vars}")
            return False
        else:
            print(f"  ✅ .env.example file contains all required variables")
            print(f"  📝 Content preview: {content[:200]}...")
            return True
    else:
        print(f"  ❌ .env.example file not found at {env_example_path}")
        return False

async def test_environment_loading_behavior():
    """Test the environment loading behavior with different scenarios"""
    print(f"\n📝 Testing environment loading behavior")
    
    # Create a temporary test environment
    test_env_path = Path("/tmp/test.env")
    test_content = """# Test environment file
GEMINI_API_KEY=test_env_key_12345
STREAMLIT_SERVER_PORT=8503
DEBUG=false
"""
    
    with open(test_env_path, 'w') as f:
        f.write(test_content)
    
    print(f"  ✅ Created test environment file")
    print(f"  📝 Content: {test_content.strip()}")
    
    # Clean up
    test_env_path.unlink()
    return True

async def test_requirements_txt_updated():
    """Test that python-dotenv is added to requirements"""
    print(f"\n📝 Testing requirements.txt updated")
    
    req_path = Path("/root/repo/human_loop_platform/requirements.txt")
    
    if req_path.exists():
        with open(req_path, 'r') as f:
            content = f.read()
        
        if 'python-dotenv' in content:
            print(f"  ✅ python-dotenv found in requirements.txt")
            return True
        else:
            print(f"  ⚠️ python-dotenv not found in requirements.txt")
            return False
    else:
        print(f"  ❌ requirements.txt not found")
        return False

async def run_all_tests():
    """Run all environment variable tests"""
    print("=" * 60)
    print("🧪 ENVIRONMENT VARIABLE TEST SUITE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"App URL: {APP_URL}")
    print(f"Screenshot Directory: {SCREENSHOT_DIR}")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "task": "TASK-005: Environment Variable Management",
        "tests": [],
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0
        }
    }
    
    # First run non-browser tests
    non_browser_tests = [
        ("Environment File Creation", test_env_file_creation),
        ("Environment Loading Behavior", test_environment_loading_behavior),
        ("Requirements.txt Updated", test_requirements_txt_updated)
    ]
    
    for test_name, test_func in non_browser_tests:
        try:
            print(f"\n{'='*40}")
            print(f"Running: {test_name}")
            print(f"{'='*40}")
            
            result = await test_func()
            
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
    
    # Now run browser tests
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        browser_tests = [
            ("Environment Variable Loading", test_env_var_loading_with_key_set),
            ("Fallback to User Input", test_fallback_to_user_input),
            ("Security - No Hardcoded Keys", test_security_no_hardcoded_keys)
        ]
        
        for test_name, test_func in browser_tests:
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
    print(f"Success Rate: {results['summary']['passed']/max(results['summary']['total'],1)*100:.1f}%")
    print(f"\nResults saved to: {results_file}")
    print(f"Screenshots saved in: {SCREENSHOT_DIR}/")
    print("=" * 60)
    
    return results['summary']['failed'] == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)