#!/usr/bin/env python3
"""
Manual API Test for Real Gemini Integration
Tests actual API calls with longer timeouts
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_real_api_workflow():
    """Test workflow with real API and longer timeouts"""
    print("🔄 Testing Real Gemini API Integration")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Step 1: Navigate and verify API connection
            print("📱 Step 1: Navigating to app...")
            await page.goto("http://localhost:8503")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Test API connection manually
            print("🔄 Testing API connection manually...")
            test_button = page.locator("button:has-text('Test Connection')")
            if await test_button.count() > 0:
                await test_button.click()
                print("   Clicked Test Connection button")
                
                # Wait for connection test result
                await asyncio.sleep(5)
                
                # Check for successful connection
                success_status = await page.locator("text=API Connected Successfully").count()
                if success_status > 0:
                    print("✅ Real API connection verified")
                    await page.screenshot(path="api_connected.png")
                else:
                    # Check for failure status
                    failed_status = await page.locator("text=Failed").count()
                    if failed_status > 0:
                        print("❌ API connection failed")
                        await page.screenshot(path="api_failed.png")
                        return
                    else:
                        print("⏳ Connection test still in progress...")
                        await asyncio.sleep(5)  # Wait a bit more
                        await page.screenshot(path="api_testing.png")
            else:
                print("❌ Test Connection button not found")
                await page.screenshot(path="no_test_button.png")
                return
            
            # Step 2: Upload data
            print("📁 Step 2: Uploading sample data...")
            file_input = page.locator('input[type="file"]')
            if await file_input.count() > 0:
                await file_input.set_input_files("sample_ecommerce_data.csv")
                await asyncio.sleep(2)
                print("✅ Data uploaded")
            
            # Step 3: Set objectives
            print("📝 Step 3: Setting objectives...")
            objectives_area = page.locator('textarea')
            if await objectives_area.count() > 0:
                await objectives_area.first.fill("Analyze e-commerce sales patterns and customer behavior for strategic insights")
                await asyncio.sleep(2)
                print("✅ Objectives set")
            
            # Step 4: Generate Plan with Real API
            print("🤖 Step 4: Testing Real Plan Generation...")
            next_button = page.locator("button:has-text('Next: Plan Generation')")
            if await next_button.count() > 0:
                await next_button.click()
                await asyncio.sleep(3)
                print("   Navigated to Plan Generation stage")
            
            # Click Generate AI Plan and wait for real response
            generate_button = page.locator("button:has-text('Generate AI Plan')")
            if await generate_button.count() > 0:
                print("   🔄 Clicking Generate AI Plan (Real API call)...")
                await generate_button.click()
                
                # Wait longer for real API response
                print("   ⏳ Waiting for real Gemini API response (up to 30 seconds)...")
                
                # Check for success message or plan content every 5 seconds
                plan_generated = False
                for i in range(6):  # 30 seconds total
                    await asyncio.sleep(5)
                    
                    # Check for success message
                    success_msg = await page.locator("text=Plan generated successfully").count()
                    if success_msg > 0:
                        print(f"   ✅ Plan generation succeeded after {(i+1)*5} seconds")
                        plan_generated = True
                        break
                    
                    # Check for plan content in textarea
                    plan_area = page.locator('textarea')
                    if await plan_area.count() > 0:
                        plan_content = await plan_area.first.input_value()
                        if plan_content and len(plan_content) > 200 and "Mock Mode" not in plan_content:
                            print(f"   ✅ Real plan content generated after {(i+1)*5} seconds")
                            print(f"   📊 Plan length: {len(plan_content)} characters")
                            plan_generated = True
                            break
                    
                    print(f"   ⏳ Still waiting... ({(i+1)*5}s elapsed)")
                
                await page.screenshot(path="real_plan_generation.png")
                
                if plan_generated:
                    print("🎉 Real AI Plan Generation: SUCCESS")
                else:
                    print("❌ Real AI Plan Generation: TIMEOUT")
            
            # Step 5: Test AI Insights Generation
            print("\n💡 Step 5: Testing Real AI Insights...")
            next_button = page.locator("button:has-text('Next: Data Understanding')")
            if await next_button.count() > 0:
                await next_button.click()
                await asyncio.sleep(3)
                print("   Navigated to Data Understanding stage")
            
            # Click AI Insights tab
            ai_tab = page.locator('[role="tab"]:has-text("AI Insights")')
            if await ai_tab.count() > 0:
                await ai_tab.click()
                await asyncio.sleep(2)
                print("   Navigated to AI Insights tab")
                
                # Click Generate AI Insights
                insights_button = page.locator("button:has-text('Generate AI Insights')")
                if await insights_button.count() > 0:
                    print("   🔄 Clicking Generate AI Insights (Real API call)...")
                    await insights_button.click()
                    
                    # Wait for real insights
                    print("   ⏳ Waiting for real AI insights (up to 30 seconds)...")
                    insights_generated = False
                    
                    for i in range(6):  # 30 seconds total
                        await asyncio.sleep(5)
                        
                        # Check for success message
                        success_msg = await page.locator("text=Insights generated successfully").count()
                        if success_msg > 0:
                            print(f"   ✅ Insights generation succeeded after {(i+1)*5} seconds")
                            insights_generated = True
                            break
                        
                        # Check for insights content
                        insights_content = await page.locator("text=Key Patterns and Trends, text=Statistical Insights").count()
                        if insights_content > 0:
                            print(f"   ✅ Real insights content generated after {(i+1)*5} seconds")
                            insights_generated = True
                            break
                        
                        print(f"   ⏳ Still waiting... ({(i+1)*5}s elapsed)")
                    
                    await page.screenshot(path="real_insights_generation.png")
                    
                    if insights_generated:
                        print("🎉 Real AI Insights Generation: SUCCESS")
                    else:
                        print("❌ Real AI Insights Generation: TIMEOUT")
            
            # Final screenshots
            await page.screenshot(path="final_real_api_test.png")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
            await page.screenshot(path="error_real_api_test.png")
        
        finally:
            await browser.close()
    
    print("\n" + "=" * 60)
    print("✅ Real API Integration Test Complete")
    print("📁 Screenshots saved for manual verification")

if __name__ == "__main__":
    asyncio.run(test_real_api_workflow())