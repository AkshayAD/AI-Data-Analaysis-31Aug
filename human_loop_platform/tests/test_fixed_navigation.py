"""
Test navigation after fixing the app
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

BASE_URL = "http://localhost:8506"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "fixed_navigation"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

def test_fixed_navigation():
    """Test the fixed navigation from Stage 0 to Stage 1"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("🧪 Testing Fixed Navigation...")
        
        # 1. Navigate to the app
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Check initial state
        page_content = page.content()
        if "Define Your Analysis Objective" in page_content:
            print("✅ Stage 0 loaded correctly")
        
        # Take screenshot of initial state
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_stage0_initial.png"))
        
        # 2. Test Force Navigation buttons first
        print("\n🔍 Testing Force Navigation Buttons...")
        
        # Try Force Stage 1 button
        s1_btn = page.locator("button").filter(has_text="S1")
        if s1_btn.count() > 0:
            print("Found S1 button, clicking...")
            s1_btn.first.click()
            time.sleep(3)
            
            page_content = page.content()
            if "AI-Powered Plan Generation" in page_content:
                print("✅ Force navigation to Stage 1 WORKS!")
                page.screenshot(path=str(SCREENSHOTS_DIR / "02_stage1_forced.png"))
            else:
                print("❌ Force navigation FAILED")
                
            # Go back to Stage 0
            s0_btn = page.locator("button").filter(has_text="S0")
            if s0_btn.count() > 0:
                s0_btn.first.click()
                time.sleep(2)
        
        # 3. Test normal navigation flow
        print("\n🚀 Testing Normal Navigation Flow...")
        
        # Fill objectives tab
        objectives_tab = page.locator('[role="tab"]').filter(has_text="Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.first.click()
            time.sleep(1)
            
            # Fill objective
            textarea = page.locator("textarea").first
            if textarea.is_visible():
                textarea.fill("Test objective for automated testing")
                print("✅ Filled objective")
                page.screenshot(path=str(SCREENSHOTS_DIR / "03_objectives_filled.png"))
        
        # Go to Review tab
        review_tab = page.locator('[role="tab"]').filter(has_text="Review")
        if review_tab.count() > 0:
            review_tab.first.click()
            time.sleep(1)
            print("✅ Navigated to Review tab")
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_review_tab.png"))
        
        # Click Generate Analysis Plan button
        gen_btn = page.locator("button").filter(has_text="Generate Analysis Plan")
        if gen_btn.count() > 0:
            print("🎯 Found 'Generate Analysis Plan' button")
            print("   Clicking button...")
            gen_btn.first.click()
            
            # Wait for navigation
            time.sleep(5)
            
            # Check if we navigated to Stage 1
            page_content = page.content()
            page.screenshot(path=str(SCREENSHOTS_DIR / "05_after_generate.png"))
            
            if "AI-Powered Plan Generation" in page_content:
                print("✅ SUCCESS! Navigated to Stage 1!")
                print("   Navigation is WORKING!")
                
                # Try to generate a plan in Stage 1
                plan_btn = page.locator("button").filter(has_text="Generate Plan")
                if plan_btn.count() > 0:
                    print("\n🎯 Testing Plan Generation...")
                    plan_btn.first.click()
                    time.sleep(3)
                    
                    # Check for success message
                    if "Plan generated successfully" in page.content():
                        print("✅ Plan generation WORKS!")
                        page.screenshot(path=str(SCREENSHOTS_DIR / "06_plan_generated.png"))
                    else:
                        print("⚠️ Plan generation didn't show success message")
                        
            elif "Define Your Analysis Objective" in page_content:
                print("❌ FAILED! Still on Stage 0")
                print("   Navigation is NOT working")
            else:
                print("❓ Unknown state after clicking Generate")
        else:
            print("❌ Generate Analysis Plan button not found")
        
        # Final summary
        print("\n" + "="*50)
        print("📊 Navigation Test Summary:")
        print("="*50)
        
        if "AI-Powered Plan Generation" in page.content():
            print("✅ Navigation Status: WORKING")
            print("✅ Current Stage: Stage 1 (Plan Generation)")
        else:
            print("❌ Navigation Status: BROKEN")
            print("❌ Current Stage: Stage 0 (Still on Input)")
            
        print(f"\n📸 Screenshots saved to: {SCREENSHOTS_DIR}")
        print(f"   Total screenshots: {len(list(SCREENSHOTS_DIR.glob('*.png')))}")
        
        browser.close()

if __name__ == "__main__":
    test_fixed_navigation()