"""
Capture screenshots of Stage 1 (Plan Generation)
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

STAGE1_URL = "http://localhost:8507"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "stage1"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

def capture_stage1_screenshots():
    """Capture comprehensive screenshots of Stage 1"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("📸 Starting Stage 1 screenshot capture...")
        
        # Navigate to Stage 1
        page.goto(STAGE1_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 1. Initial Stage 1 view
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_stage1_initial.png"))
        print("✓ Captured initial Stage 1 view")
        
        # 2. Try to find and click Generate Plan button
        try:
            # Look for Generate Plan button
            gen_btn = page.locator("button").filter(has_text="Generate Plan")
            if gen_btn.count() > 0:
                # Screenshot before clicking
                page.screenshot(path=str(SCREENSHOTS_DIR / "02_before_generate.png"))
                print("✓ Captured before generate")
                
                # Click Generate Plan
                gen_btn.first.click()
                time.sleep(5)  # Wait for plan generation
                
                # Screenshot after generation
                page.screenshot(path=str(SCREENSHOTS_DIR / "03_after_generate.png"))
                print("✓ Captured after plan generation")
        except Exception as e:
            print(f"Could not click Generate Plan: {e}")
        
        # 3. Check for tabs
        try:
            # Look for Edit tab
            edit_tab = page.locator('[role="tab"]').filter(has_text="Edit")
            if edit_tab.count() > 0:
                edit_tab.first.click()
                time.sleep(1)
                page.screenshot(path=str(SCREENSHOTS_DIR / "04_edit_tab.png"))
                print("✓ Captured Edit tab")
            
            # Look for Summary tab
            summary_tab = page.locator('[role="tab"]').filter(has_text="Summary")
            if summary_tab.count() > 0:
                summary_tab.first.click()
                time.sleep(1)
                page.screenshot(path=str(SCREENSHOTS_DIR / "05_summary_tab.png"))
                print("✓ Captured Summary tab")
        except Exception as e:
            print(f"Could not navigate tabs: {e}")
        
        # 4. Check for AI Assistant
        try:
            # Scroll to find AI Assistant section
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            page.screenshot(path=str(SCREENSHOTS_DIR / "06_ai_assistant.png"))
            print("✓ Captured AI Assistant section")
        except Exception as e:
            print(f"Could not capture AI Assistant: {e}")
        
        # 5. Full page screenshot
        page.screenshot(path=str(SCREENSHOTS_DIR / "07_full_page.png"), full_page=True)
        print("✓ Captured full page")
        
        # 6. Check page content
        page_content = page.content()
        if "AI-Powered Plan Generation" in page_content:
            print("✅ Found 'AI-Powered Plan Generation' - Stage 1 is loaded!")
        elif "Plan Generation" in page_content:
            print("✅ Found 'Plan Generation' - Stage 1 is loaded!")
        else:
            print("⚠️ Stage 1 markers not found in page")
        
        # Save page HTML for debugging
        with open(SCREENSHOTS_DIR / "page_content.html", "w") as f:
            f.write(page_content)
        print("✓ Saved page HTML for analysis")
        
        browser.close()
        
        print(f"\n📁 Screenshots saved to: {SCREENSHOTS_DIR}")
        print(f"Total screenshots: {len(list(SCREENSHOTS_DIR.glob('*.png')))}")

if __name__ == "__main__":
    capture_stage1_screenshots()