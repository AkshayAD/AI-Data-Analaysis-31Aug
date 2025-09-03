from playwright.sync_api import sync_playwright
import time

def test_simple_nav():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("http://localhost:8509")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Check initial state
        print("Initial content:", "Stage 0" in page.content())
        
        # Try form submission
        form_button = page.locator("button").filter(has_text="Submit and Go to Stage 1")
        if form_button.count() > 0:
            # Fill text area first
            textarea = page.locator("textarea").first
            textarea.fill("Test objective")
            time.sleep(1)
            
            print("Clicking submit...")
            form_button.first.click()
            time.sleep(3)
            
            # Check if we're on Stage 1
            if "Stage 1: Plan Generation" in page.content():
                print("✅ Navigation to Stage 1 WORKS in simple app!")
            else:
                print("❌ Navigation failed in simple app")
        
        browser.close()

test_simple_nav()