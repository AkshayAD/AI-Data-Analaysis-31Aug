#!/usr/bin/env python3
"""
Test Suite for TASK-006: Caching Performance Implementation
Tests Streamlit caching for API responses and performance improvements
"""

import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import os
import tempfile
import pandas as pd
import numpy as np

# Configuration
APP_URL = "http://localhost:8503"
SCREENSHOT_DIR = Path("screenshots_caching")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# Test data
TEST_OBJECTIVE = "Analyze customer churn patterns and identify key factors"
TEST_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8')

async def test_api_response_caching():
    """Test that API responses are cached and reused"""
    print("\n" + "="*60)
    print("🧪 TEST: API Response Caching")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to app
            await page.goto(APP_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Take initial screenshot
            await page.screenshot(path=SCREENSHOT_DIR / "01_initial_load.png")
            
            # Upload test data first
            # Create a test CSV file
            import tempfile
            import pandas as pd
            test_df = pd.DataFrame({
                'customer_id': range(1, 101),
                'age': np.random.randint(18, 70, 100),
                'purchase_amount': np.random.uniform(10, 500, 100),
                'loyalty_score': np.random.uniform(0, 10, 100)
            })
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                test_df.to_csv(f, index=False)
                test_file = f.name
            
            # Upload the file
            file_input = await page.wait_for_selector('input[type="file"]', timeout=5000)
            await file_input.set_input_files(test_file)
            await page.wait_for_timeout(2000)
            
            # Enter business objective (find by label text)
            await page.wait_for_selector('text=What is your analysis objective?', timeout=5000)
            objective_input = page.locator('textarea').first()
            await objective_input.fill(TEST_OBJECTIVE)
            
            # Navigate to Stage 1 (Plan Generation)
            stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
            await stage1_button.click()
            await page.wait_for_timeout(2000)
            
            # First API call - measure time
            print("  📊 Making first API call (should be uncached)...")
            start_time = time.time()
            
            generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
            await generate_button.click()
            
            # Wait for plan to be generated
            await page.wait_for_selector('text=Plan generated successfully', timeout=30000)
            first_call_time = time.time() - start_time
            print(f"  ⏱️ First call time: {first_call_time:.2f}s")
            
            await page.screenshot(path=SCREENSHOT_DIR / "02_first_generation.png")
            
            # Clear the plan to test regeneration
            await page.reload()
            await page.wait_for_timeout(2000)
            
            # Navigate back to Stage 1
            stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
            await stage1_button.click()
            await page.wait_for_timeout(1000)
            
            # Second API call - should use cache
            print("  📊 Making second API call (should be cached)...")
            start_time = time.time()
            
            generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
            await generate_button.click()
            
            # Wait for plan to be generated (should be faster)
            await page.wait_for_selector('text=Plan generated successfully', timeout=10000)
            second_call_time = time.time() - start_time
            print(f"  ⏱️ Second call time: {second_call_time:.2f}s")
            
            await page.screenshot(path=SCREENSHOT_DIR / "03_cached_generation.png")
            
            # Verify caching worked
            if second_call_time < first_call_time * 0.5:  # Should be at least 50% faster
                print(f"  ✅ Caching effective: {(1 - second_call_time/first_call_time)*100:.1f}% faster")
                return True
            else:
                print(f"  ❌ Caching not effective: Only {(1 - second_call_time/first_call_time)*100:.1f}% faster")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_caching.png")
            return False
        finally:
            await browser.close()

def clear_streamlit_cache():
    """Clear Streamlit cache by triggering cache clear"""
    # Note: In production, you'd use st.cache_data.clear() 
    # For testing, we rely on different inputs to test cache behavior
    pass

async def test_cache_invalidation():
    """Test that cache can be invalidated when needed"""
    print("\n" + "="*60)
    print("🧪 TEST: Cache Invalidation")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(APP_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Enter first objective
            await page.wait_for_selector('text=What is your analysis objective?', timeout=5000)
            objective_input = page.locator('textarea').first()
            await objective_input.fill("First objective: analyze sales data")
            
            # Generate plan
            stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
            await stage1_button.click()
            await page.wait_for_timeout(1000)
            
            generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
            await generate_button.click()
            await page.wait_for_selector('text=Plan generated successfully', timeout=30000)
            
            # Get first plan content
            first_plan = await page.inner_text('.stTextArea textarea')
            
            # Change objective (should invalidate cache)
            await page.goto(APP_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            await page.wait_for_selector('text=What is your analysis objective?', timeout=5000)
            objective_input = page.locator('textarea').first()
            await objective_input.fill("Different objective: predict customer churn")
            
            # Generate new plan
            stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
            await stage1_button.click()
            await page.wait_for_timeout(1000)
            
            generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
            await generate_button.click()
            await page.wait_for_selector('text=Plan generated successfully', timeout=30000)
            
            # Get second plan content
            second_plan = await page.inner_text('.stTextArea textarea')
            
            await page.screenshot(path=SCREENSHOT_DIR / "04_cache_invalidation.png")
            
            # Verify plans are different
            if first_plan != second_plan:
                print("  ✅ Cache invalidation working: Different plans for different objectives")
                return True
            else:
                print("  ❌ Cache invalidation failed: Same plan for different objectives")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_invalidation.png")
            return False
        finally:
            await browser.close()

async def test_performance_targets():
    """Test that cached operations meet performance targets (<3s)"""
    print("\n" + "="*60)
    print("🧪 TEST: Performance Targets")
    print("="*60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(APP_URL, wait_until='networkidle')
            await page.wait_for_timeout(2000)
            
            # Setup initial data
            await page.wait_for_selector('text=What is your analysis objective?', timeout=5000)
            objective_input = page.locator('textarea').first()
            await objective_input.fill(TEST_OBJECTIVE)
            
            # Prime the cache with first call
            stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
            await stage1_button.click()
            await page.wait_for_timeout(1000)
            
            generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
            await generate_button.click()
            await page.wait_for_selector('text=Plan generated successfully', timeout=30000)
            
            # Test cached operations performance
            print("  📊 Testing cached operation performance...")
            
            performance_results = []
            
            # Test multiple cached operations
            for i in range(3):
                await page.reload()
                await page.wait_for_timeout(1000)
                
                stage1_button = await page.wait_for_selector('button:has-text("Stage 1: Plan Generation")', timeout=5000)
                await stage1_button.click()
                await page.wait_for_timeout(500)
                
                start_time = time.time()
                generate_button = await page.wait_for_selector('button:has-text("Generate Plan")', timeout=5000)
                await generate_button.click()
                await page.wait_for_selector('text=Plan generated successfully', timeout=10000)
                operation_time = time.time() - start_time
                
                performance_results.append(operation_time)
                print(f"    Operation {i+1}: {operation_time:.2f}s")
            
            avg_time = sum(performance_results) / len(performance_results)
            print(f"  📊 Average cached operation time: {avg_time:.2f}s")
            
            await page.screenshot(path=SCREENSHOT_DIR / "05_performance_test.png")
            
            # Check if meets target (<3s)
            if avg_time < 3.0:
                print(f"  ✅ Performance target met: {avg_time:.2f}s < 3s")
                return True
            else:
                print(f"  ❌ Performance target not met: {avg_time:.2f}s >= 3s")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            await page.screenshot(path=SCREENSHOT_DIR / "error_performance.png")
            return False
        finally:
            await browser.close()

async def test_cache_decorator_present():
    """Test that cache decorators are present in the code"""
    print("\n" + "="*60)
    print("🧪 TEST: Cache Decorator Implementation")
    print("="*60)
    
    try:
        # Read the app file
        app_file = Path("human_loop_platform/app_working.py")
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check for cache decorators
        cache_patterns = [
            "@st.cache_data",
            "@st.cache_resource",
            "st.cache_data",
            "st.cache_resource"
        ]
        
        found_patterns = []
        for pattern in cache_patterns:
            if pattern in content:
                found_patterns.append(pattern)
                count = content.count(pattern)
                print(f"  ✅ Found '{pattern}' {count} time(s)")
        
        if found_patterns:
            print(f"  ✅ Cache decorators implemented")
            return True
        else:
            print(f"  ❌ No cache decorators found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error reading file: {str(e)}")
        return False

async def main():
    """Run all caching tests"""
    print("\n" + "="*60)
    print("🚀 CACHING PERFORMANCE TEST SUITE")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"App URL: {APP_URL}")
    print(f"Screenshot Directory: {SCREENSHOT_DIR}")
    print("="*60)
    
    # Ensure app is running
    print("\n📱 Checking if app is running...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(APP_URL, timeout=10000)
            await browser.close()
            print("✅ App is running")
    except:
        print("❌ App is not running. Please start it with:")
        print("   streamlit run human_loop_platform/app_working.py --server.port 8503")
        return
    
    # Run tests
    test_results = {
        "cache_decorator_present": await test_cache_decorator_present(),
        "api_response_caching": await test_api_response_caching(),
        "cache_invalidation": await test_cache_invalidation(),
        "performance_targets": await test_performance_targets()
    }
    
    # Save results
    results_file = SCREENSHOT_DIR / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": test_results,
            "passed": sum(test_results.values()),
            "failed": len(test_results) - sum(test_results.values()),
            "total": len(test_results)
        }, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    passed = sum(test_results.values())
    total = len(test_results)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print(f"\nResults saved to: {results_file}")
    print(f"Screenshots saved in: {SCREENSHOT_DIR}/")
    print("="*60)
    
    # Return overall success
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)