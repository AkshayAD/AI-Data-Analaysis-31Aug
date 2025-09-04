from playwright.sync_api import sync_playwright
import time

def test_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test debug app
        page.goto("http://localhost:8508")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Get initial state
        print("Initial page state:")
        print(f"- Current stage visible: {page.locator('text=Current Stage:').is_visible()}")
        
        # Try clicking Go to Stage 1
        stage1_btn = page.locator("button").filter(has_text="Go to Stage 1")
        if stage1_btn.count() > 0:
            print("Found 'Go to Stage 1' button, clicking...")
            stage1_btn.first.click()
            time.sleep(3)
            
            # Check if we're on Stage 1
            page_content = page.content()
            if "Stage 1: Plan Generation" in page_content:
                print("✅ Navigation to Stage 1 WORKS!")
            else:
                print("❌ Navigation FAILED")
        
        browser.close()

test_navigation()