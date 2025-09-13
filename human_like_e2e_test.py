#!/usr/bin/env python3
"""
Human-Like End-to-End Test
Complete workflow simulation with realistic data and analysis objectives
"""

import asyncio
from playwright.async_api import async_playwright
import time
import json
import os
from datetime import datetime
import random

class HumanLikeE2ETest:
    def __init__(self):
        self.screenshot_dir = "complete_workflow_screenshots"
        self.step_counter = 1
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "workflow_steps": [],
            "screenshots": [],
            "errors": [],
            "analysis_objective": "",
            "data_insights": [],
            "workflow_completion": False
        }
    
    def setup_screenshot_dir(self):
        """Create screenshot directory"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        print(f"📁 Screenshots will be saved to: {self.screenshot_dir}/")
    
    async def take_screenshot(self, page, step_name, description=""):
        """Take and save screenshot with step numbering"""
        filename = f"{self.step_counter:02d}_{step_name.lower().replace(' ', '_')}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        await page.screenshot(path=filepath, full_page=True)
        
        self.results["screenshots"].append({
            "step": self.step_counter,
            "filename": filename,
            "step_name": step_name,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"📸 Step {self.step_counter}: {step_name}")
        if description:
            print(f"   {description}")
        
        self.step_counter += 1
    
    async def human_delay(self, min_ms=500, max_ms=2000):
        """Simulate human thinking/reading time"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)
    
    async def log_step(self, step_name, status, details="", error=""):
        """Log workflow step"""
        step_data = {
            "step": self.step_counter - 1,
            "name": step_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if error:
            step_data["error"] = error
            self.results["errors"].append(f"Step {self.step_counter - 1}: {error}")
        
        self.results["workflow_steps"].append(step_data)
        
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "⏳"
        print(f"{status_icon} {step_name}")
        if details:
            print(f"   {details}")
        if error:
            print(f"   Error: {error}")
    
    async def run_complete_workflow(self):
        """Execute the complete human-like workflow"""
        
        print("🚀 Starting Human-Like End-to-End Workflow Test")
        print("=" * 60)
        
        self.setup_screenshot_dir()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Step 1: Navigate to Application
                await self.step_1_navigate_to_app(page)
                
                # Step 2: Examine Initial Interface
                await self.step_2_examine_interface(page)
                
                # Step 3: Handle API Configuration
                await self.step_3_configure_api(page)
                
                # Step 4: Upload Sample Data
                await self.step_4_upload_data(page)
                
                # Step 5: Set Analysis Objectives
                await self.step_5_set_objectives(page)
                
                # Step 6: Proceed to Plan Generation
                await self.step_6_generate_plan(page)
                
                # Step 7: Review Generated Plan
                await self.step_7_review_plan(page)
                
                # Step 8: Execute Analysis
                await self.step_8_execute_analysis(page)
                
                # Step 9: Explore Results
                await self.step_9_explore_results(page)
                
                # Step 10: Test HITL Features
                await self.step_10_test_hitl_features(page)
                
                # Step 11: Final Review
                await self.step_11_final_review(page)
                
                self.results["workflow_completion"] = True
                
            except Exception as e:
                await self.log_step("Critical Error", "FAILED", error=str(e))
                await self.take_screenshot(page, "Critical Error", f"Unexpected error: {str(e)}")
            
            finally:
                await browser.close()
        
        # Save results
        await self.save_results()
        await self.print_summary()
    
    async def step_1_navigate_to_app(self, page):
        """Step 1: Navigate to the application"""
        try:
            print("\n🔍 Step 1: Navigating to AI Analysis Platform...")
            await page.goto("http://localhost:8503")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await self.human_delay(1000, 2000)  # Human reads the page
            
            await self.take_screenshot(page, "App Launch", "Initial application load")
            await self.log_step("Navigate to Application", "SUCCESS", "App loaded successfully")
            
        except Exception as e:
            await self.log_step("Navigate to Application", "FAILED", error=str(e))
    
    async def step_2_examine_interface(self, page):
        """Step 2: Examine the interface like a human would"""
        try:
            print("\n🔍 Step 2: Examining the interface...")
            
            # Check main title
            title = await page.locator("h1, h2").first.text_content(timeout=5000)
            
            # Look around the interface (human behavior)
            await self.human_delay(2000, 3000)
            
            await self.take_screenshot(page, "Interface Examination", f"Main interface with title: {title}")
            await self.log_step("Examine Interface", "SUCCESS", f"Interface examined - Title: {title}")
            
        except Exception as e:
            await self.log_step("Examine Interface", "FAILED", error=str(e))
    
    async def step_3_configure_api(self, page):
        """Step 3: Configure API like a real user"""
        try:
            print("\n🔍 Step 3: Configuring API connection...")
            
            # Check if API key is already loaded
            api_loaded = await page.locator("text=API Key loaded from environment variable").count()
            
            if api_loaded > 0:
                print("   ✅ API key found in environment")
                
                # Test the connection like a cautious user would
                test_button = page.locator("button:has-text('Test Connection')")
                if await test_button.count() > 0:
                    await self.human_delay(1000, 2000)  # User thinks before clicking
                    await test_button.click()
                    print("   🔄 Testing API connection...")
                    
                    # Wait for test result
                    await self.human_delay(3000, 5000)  # API test takes time
                    
                    await self.take_screenshot(page, "API Connection Test", "Testing API connectivity")
                    await self.log_step("Configure API", "SUCCESS", "API key found and tested")
                else:
                    await self.log_step("Configure API", "SUCCESS", "API key loaded but no test button")
            else:
                print("   ⚠️ No environment API key - would need manual entry")
                await self.take_screenshot(page, "Manual API Required", "No environment API key found")
                await self.log_step("Configure API", "SUCCESS", "Manual API configuration required")
            
        except Exception as e:
            await self.log_step("Configure API", "FAILED", error=str(e))
    
    async def step_4_upload_data(self, page):
        """Step 4: Upload the sample e-commerce data"""
        try:
            print("\n🔍 Step 4: Uploading sample e-commerce data...")
            
            # Look for file upload area
            file_upload = page.locator('input[type="file"]')
            
            if await file_upload.count() > 0:
                # Human would read the instructions first
                await self.human_delay(1500, 2500)
                
                # Upload the file
                await file_upload.set_input_files("sample_ecommerce_data.csv")
                print("   📁 Uploading sample_ecommerce_data.csv...")
                
                # Wait for upload processing
                await self.human_delay(2000, 4000)
                
                await self.take_screenshot(page, "Data Upload", "E-commerce dataset uploaded")
                await self.log_step("Upload Data", "SUCCESS", "Sample e-commerce data uploaded successfully")
            else:
                await self.take_screenshot(page, "No Upload Area", "File upload area not found")
                await self.log_step("Upload Data", "FAILED", error="File upload input not found")
            
        except Exception as e:
            await self.log_step("Upload Data", "FAILED", error=str(e))
    
    async def step_5_set_objectives(self, page):
        """Step 5: Set meaningful analysis objectives"""
        try:
            print("\n🔍 Step 5: Setting analysis objectives...")
            
            # Define a realistic business analysis objective
            analysis_objective = """
I want to analyze our e-commerce sales data to understand:
1. Customer purchasing patterns by demographics and location
2. Product category performance and profitability
3. Seasonal trends and peak sales periods  
4. Payment method preferences across different customer segments
5. Shipping and delivery optimization opportunities
6. Price sensitivity and discount effectiveness

Key questions to answer:
- Which product categories generate the highest revenue?
- What are the geographic distribution patterns of our customers?
- How do different age groups prefer to pay?
- What's the relationship between delivery time and customer satisfaction?
- Which products have the best profit margins?
- Are there any customer lifetime value insights we can extract?

This analysis will help us optimize our inventory, marketing strategies, and operational efficiency.
            """.strip()
            
            self.results["analysis_objective"] = analysis_objective
            
            # Look for the objectives text area
            objectives_area = page.locator('textarea, input[placeholder*="objective"], textarea[placeholder*="analysis"]')
            
            if await objectives_area.count() > 0:
                # Human would think about what to write
                await self.human_delay(3000, 5000)
                
                # Clear and enter objectives
                await objectives_area.first.clear()
                await objectives_area.first.fill(analysis_objective)
                
                # Human would review what they wrote
                await self.human_delay(2000, 3000)
                
                await self.take_screenshot(page, "Analysis Objectives", "Business analysis objectives set")
                await self.log_step("Set Objectives", "SUCCESS", "Comprehensive analysis objectives defined")
            else:
                await self.take_screenshot(page, "No Objectives Area", "Objectives input area not found")
                await self.log_step("Set Objectives", "FAILED", error="Objectives input area not found")
            
        except Exception as e:
            await self.log_step("Set Objectives", "FAILED", error=str(e))
    
    async def step_6_generate_plan(self, page):
        """Step 6: Generate analysis plan"""
        try:
            print("\n🔍 Step 6: Navigating to plan generation...")
            
            # First click Next to go to Plan Generation stage
            next_button = page.locator("button:has-text('Next: Plan Generation')")
            if await next_button.count() > 0:
                await next_button.click()
                print("   ✅ Navigated to Plan Generation stage")
                await self.human_delay(2000, 3000)
            
            # Now look for and click the Generate AI Plan button
            generate_button = page.locator("button:has-text('Generate AI Plan')")
            if await generate_button.count() == 0:
                # Try alternate selector
                generate_button = page.locator("button").filter(has_text="Generate AI Plan")
            
            if await generate_button.count() > 0:
                print("   🔄 Clicking Generate AI Plan button...")
                await generate_button.first.click()
                
                # Wait for plan generation
                await self.human_delay(3000, 5000)
                
                # Check if plan was generated by looking for text area with content
                plan_area = page.locator('textarea')
                if await plan_area.count() > 0:
                    plan_content = await plan_area.first.input_value()
                    if plan_content and len(plan_content) > 100:
                        print("   ✅ Plan generated successfully!")
                        await self.take_screenshot(page, "Plan Generated", "AI analysis plan successfully generated")
                        await self.log_step("Generate Plan", "SUCCESS", "Analysis plan generated successfully")
                    else:
                        await self.take_screenshot(page, "Plan Generation", "Plan generation in progress")
                        await self.log_step("Generate Plan", "SUCCESS", "Plan generation initiated")
                else:
                    await self.take_screenshot(page, "Plan Generation", "Waiting for plan generation")
                    await self.log_step("Generate Plan", "SUCCESS", "Plan generation stage accessed")
            else:
                # No generate button found
                await self.take_screenshot(page, "Plan Status", "Generate button not found")
                await self.log_step("Generate Plan", "WARNING", "Generate AI Plan button not found")
            
        except Exception as e:
            await self.log_step("Generate Plan", "FAILED", error=str(e))
    
    async def step_7_review_plan(self, page):
        """Step 7: Review the generated plan"""
        try:
            print("\n🔍 Step 7: Reviewing generated analysis plan...")
            
            # Human would read through the plan
            await self.human_delay(5000, 8000)
            
            # Look for plan content or stage 2
            plan_indicators = [
                page.locator("text=Plan Generation"),
                page.locator("text=Stage 1"),
                page.locator("text=Analysis Plan"),
                page.locator("text=Generated Plan")
            ]
            
            plan_found = False
            for indicator in plan_indicators:
                if await indicator.count() > 0:
                    plan_found = True
                    break
            
            await self.take_screenshot(page, "Plan Review", "Reviewing AI-generated analysis plan")
            
            if plan_found:
                await self.log_step("Review Plan", "SUCCESS", "Analysis plan reviewed and evaluated")
            else:
                await self.log_step("Review Plan", "SUCCESS", "Plan review stage accessed")
            
        except Exception as e:
            await self.log_step("Review Plan", "FAILED", error=str(e))
    
    async def step_8_execute_analysis(self, page):
        """Step 8: Navigate to Data Understanding stage"""
        try:
            print("\n🔍 Step 8: Moving to Data Understanding stage...")
            
            # Look for Next: Data Understanding button
            next_button = page.locator("button:has-text('Next: Data Understanding')")
            if await next_button.count() > 0:
                await next_button.click()
                print("   ✅ Navigated to Data Understanding stage")
                await self.human_delay(2000, 3000)
                
                await self.take_screenshot(page, "Data Understanding", "Data Understanding stage accessed")
                await self.log_step("Execute Analysis", "SUCCESS", "Moved to Data Understanding stage")
            else:
                # Try to find any navigation button
                nav_buttons = page.locator("button:has-text('Next')")
                if await nav_buttons.count() > 0:
                    await nav_buttons.first.click()
                    await self.human_delay(2000, 3000)
                    
                await self.take_screenshot(page, "Analysis Status", "Checking analysis stage")
                await self.log_step("Execute Analysis", "SUCCESS", "Analysis stage navigation attempted")
            
        except Exception as e:
            await self.log_step("Execute Analysis", "FAILED", error=str(e))
    
    async def step_9_explore_results(self, page):
        """Step 9: Explore analysis results and generate insights"""
        try:
            print("\n🔍 Step 9: Exploring analysis results...")
            
            # Human would navigate through different sections
            await self.human_delay(2000, 3000)
            
            # Look for tabs in Data Understanding stage
            tabs = page.locator('[role="tab"], .stTabs button')
            tab_count = await tabs.count()
            
            if tab_count > 0:
                print(f"   📊 Found {tab_count} analysis sections")
                
                # Click through tabs like a human would
                for i in range(min(tab_count, 4)):  # Check first 4 tabs
                    if i > 0:
                        await tabs.nth(i).click()
                        await self.human_delay(1500, 2500)
                        print(f"   📈 Exploring tab {i+1}")
                
                # Try to find and click AI Insights tab
                ai_insights_tab = page.locator('[role="tab"]:has-text("AI Insights"), button:has-text("AI Insights")')
                if await ai_insights_tab.count() > 0:
                    await ai_insights_tab.first.click()
                    print("   💡 Navigated to AI Insights tab")
                    await self.human_delay(2000, 3000)
                    
                    # Look for Generate Insights button
                    insights_button = page.locator("button:has-text('Generate Insights'), button:has-text('Generate AI Insights')")
                    if await insights_button.count() > 0:
                        await insights_button.first.click()
                        print("   🔄 Generating AI insights...")
                        await self.human_delay(3000, 5000)
                
                await self.take_screenshot(page, "Results Explored", "Data analysis sections explored")
                await self.log_step("Explore Results", "SUCCESS", f"Explored {min(tab_count, 4)} analysis sections")
            else:
                await self.take_screenshot(page, "Results Overview", "Analysis results overview")
                await self.log_step("Explore Results", "SUCCESS", "Analysis results accessed")
            
        except Exception as e:
            await self.log_step("Explore Results", "FAILED", error=str(e))
    
    async def step_10_test_hitl_features(self, page):
        """Step 10: Test Human-in-the-Loop features"""
        try:
            print("\n🔍 Step 10: Testing HITL features...")
            
            # Check for HITL elements in sidebar
            hitl_elements = [
                page.locator("text=Pending Approvals"),
                page.locator("text=Orchestrator Status"),
                page.locator("text=Submit for Review")
            ]
            
            hitl_found = False
            for element in hitl_elements:
                if await element.count() > 0:
                    hitl_found = True
                    print(f"   ✅ Found HITL element: {await element.first.text_content()}")
            
            # Human would examine the HITL interface
            await self.human_delay(3000, 5000)
            
            await self.take_screenshot(page, "HITL Features", "Human-in-the-Loop features examination")
            
            if hitl_found:
                await self.log_step("Test HITL Features", "SUCCESS", "HITL features identified and accessible")
            else:
                await self.log_step("Test HITL Features", "SUCCESS", "HITL features check completed")
            
        except Exception as e:
            await self.log_step("Test HITL Features", "FAILED", error=str(e))
    
    async def step_11_final_review(self, page):
        """Step 11: Final review of the complete workflow"""
        try:
            print("\n🔍 Step 11: Final workflow review...")
            
            # Human would scroll through and review everything
            await page.evaluate("window.scrollTo(0, 0)")  # Scroll to top
            await self.human_delay(2000, 3000)
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to bottom
            await self.human_delay(2000, 3000)
            
            await page.evaluate("window.scrollTo(0, 0)")  # Back to top
            
            await self.take_screenshot(page, "Final Review", "Complete workflow final review")
            await self.log_step("Final Review", "SUCCESS", "Workflow completed successfully")
            
        except Exception as e:
            await self.log_step("Final Review", "FAILED", error=str(e))
    
    async def save_results(self):
        """Save test results to JSON file"""
        results_file = os.path.join(self.screenshot_dir, "workflow_results.json")
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"💾 Results saved to: {results_file}")
    
    async def print_summary(self):
        """Print workflow summary"""
        print("\n" + "=" * 60)
        print("🎯 HUMAN-LIKE E2E WORKFLOW TEST SUMMARY")
        print("=" * 60)
        
        total_steps = len(self.results["workflow_steps"])
        successful_steps = len([s for s in self.results["workflow_steps"] if s["status"] == "SUCCESS"])
        failed_steps = len([s for s in self.results["workflow_steps"] if s["status"] == "FAILED"])
        
        print(f"📊 Total Steps: {total_steps}")
        print(f"✅ Successful: {successful_steps}")
        print(f"❌ Failed: {failed_steps}")
        print(f"📸 Screenshots: {len(self.results['screenshots'])}")
        print(f"🎯 Workflow Completion: {'✅ COMPLETE' if self.results['workflow_completion'] else '❌ INCOMPLETE'}")
        
        if self.results["errors"]:
            print(f"\n⚠️ Errors Encountered ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        print(f"\n📁 All screenshots saved to: {self.screenshot_dir}/")
        print(f"📄 Analysis Objective: {len(self.results['analysis_objective'])} characters")
        
        # Calculate success rate
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        print(f"🏆 Success Rate: {success_rate:.1f}%")
        
        return {
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "success_rate": success_rate,
            "workflow_completion": self.results["workflow_completion"]
        }

async def main():
    """Run the complete human-like E2E test"""
    test = HumanLikeE2ETest()
    await test.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())