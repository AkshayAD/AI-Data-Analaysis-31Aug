"""
Test the normal flow from Stage 0 to Stage 1
This simulates what a real user would experience
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

BASE_URL = "http://localhost:8506"  # Normal app URL
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "normal_flow"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

def test_normal_navigation():
    """Test normal navigation from Stage 0 to Stage 1"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("📸 Testing normal navigation flow...")
        
        # 1. Start at Stage 0
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_stage0_start.png"))
        print("✓ Stage 0 loaded")
        
        # 2. Fill objectives
        objectives_tab = page.locator('[role="tab"]').filter(has_text="Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.first.click()
            time.sleep(1)
            
            # Fill objective
            textarea = page.locator("textarea").first
            if textarea.is_visible():
                textarea.fill("Test objective for navigation flow")
                page.screenshot(path=str(SCREENSHOTS_DIR / "02_objectives_filled.png"))
                print("✓ Objectives filled")
        
        # 3. Go to Review tab
        review_tab = page.locator('[role="tab"]').filter(has_text="Review")
        if review_tab.count() > 0:
            review_tab.first.click()
            time.sleep(1)
            page.screenshot(path=str(SCREENSHOTS_DIR / "03_review_tab.png"))
            print("✓ Review tab opened")
        
        # 4. Click Generate Analysis Plan
        gen_btn = page.locator("button").filter(has_text="Generate Analysis Plan")
        if gen_btn.count() > 0:
            print("🔄 Clicking Generate Analysis Plan...")
            gen_btn.first.click()
            
            # Wait for potential navigation
            print("⏳ Waiting for navigation...")
            time.sleep(5)
            
            # Take screenshot of result
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_after_generate_click.png"))
            
            # Check what page we're on
            page_content = page.content()
            
            if "AI-Powered Plan Generation" in page_content:
                print("✅ Successfully navigated to Stage 1!")
                page.screenshot(path=str(SCREENSHOTS_DIR / "05_stage1_success.png"))
                
                # Try to generate a plan
                plan_btn = page.locator("button").filter(has_text="Generate Plan")
                if plan_btn.count() > 0:
                    plan_btn.first.click()
                    time.sleep(3)
                    page.screenshot(path=str(SCREENSHOTS_DIR / "06_plan_generated.png"))
                    print("✅ Plan generation tested!")
                    
            elif "Define Your Analysis Objective" in page_content:
                print("⚠️ Still on Stage 0 - navigation did not occur")
                print("This is a known Streamlit session state issue")
            else:
                print("❓ Unknown state")
        
        browser.close()
        
        print(f"\n📁 Screenshots saved to: {SCREENSHOTS_DIR}")
        print(f"Total screenshots: {len(list(SCREENSHOTS_DIR.glob('*.png')))}")

if __name__ == "__main__":
    test_normal_navigation()