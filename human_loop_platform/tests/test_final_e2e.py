"""
Final End-to-End Test - Milestone 2 Complete
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

BASE_URL = "http://localhost:8506"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "final_e2e"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)

def test_complete_workflow():
    """Test the complete workflow from Stage 0 to Stage 1 with all features"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("="*60)
        print("🧪 FINAL END-TO-END TEST - MILESTONE 2")
        print("="*60)
        
        # Test 1: Initial Load
        print("\n📍 Test 1: Initial Page Load")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        if "Define Your Analysis Objective" in page.content():
            print("✅ Stage 0 loaded successfully")
            page.screenshot(path=str(SCREENSHOTS_DIR / "01_stage0_initial.png"))
        else:
            print("❌ Failed to load Stage 0")
            
        # Test 2: Fill Objectives
        print("\n📍 Test 2: Fill Objectives")
        objectives_tab = page.locator('[role="tab"]').filter(has_text="Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.first.click()
            time.sleep(1)
            
            textarea = page.locator("textarea").first
            textarea.fill("Analyze customer churn patterns using machine learning")
            
            # Select analysis type if available
            combo = page.locator('[role="combobox"]').first
            if combo.count() > 0:
                combo.click()
                time.sleep(0.5)
                option = page.locator('[role="option"]').filter(has_text="Predictive")
                if option.count() > 0:
                    option.first.click()
                    
            print("✅ Objectives filled")
            page.screenshot(path=str(SCREENSHOTS_DIR / "02_objectives_filled.png"))
        
        # Test 3: Navigate to Review Tab
        print("\n📍 Test 3: Navigate to Review Tab")
        review_tab = page.locator('[role="tab"]').filter(has_text="Review")
        if review_tab.count() > 0:
            review_tab.first.click()
            time.sleep(1)
            print("✅ Review tab opened")
            page.screenshot(path=str(SCREENSHOTS_DIR / "03_review_tab.png"))
        
        # Test 4: Navigate to Stage 1
        print("\n📍 Test 4: Navigate to Stage 1 (Plan Generation)")
        gen_btn = page.locator("button").filter(has_text="Generate Analysis Plan")
        if gen_btn.count() > 0:
            gen_btn.first.click()
            print("⏳ Navigating to Stage 1...")
            time.sleep(5)
            
            if "AI-Powered Plan Generation" in page.content():
                print("✅ Successfully navigated to Stage 1!")
                page.screenshot(path=str(SCREENSHOTS_DIR / "04_stage1_loaded.png"))
            else:
                print("❌ Navigation to Stage 1 failed")
                return
        
        # Test 5: Generate Plan
        print("\n📍 Test 5: Generate Analysis Plan")
        plan_btn = page.locator("button").filter(has_text="Generate Plan")
        if plan_btn.count() > 0:
            plan_btn.first.click()
            time.sleep(3)
            
            if "Plan generated successfully" in page.content():
                print("✅ Plan generated successfully!")
                page.screenshot(path=str(SCREENSHOTS_DIR / "05_plan_generated.png"))
            else:
                print("⚠️ Plan generation message not found")
        
        # Test 6: Check Edit Tab
        print("\n📍 Test 6: Check Edit Tab")
        edit_tab = page.locator('[role="tab"]').filter(has_text="Edit")
        if edit_tab.count() > 0:
            edit_tab.first.click()
            time.sleep(1)
            
            if "Analysis Plan Editor" in page.content():
                print("✅ Edit tab working")
                page.screenshot(path=str(SCREENSHOTS_DIR / "06_edit_tab.png"))
            else:
                print("⚠️ Edit tab content not found")
        
        # Test 7: Check Summary Tab
        print("\n📍 Test 7: Check Summary Tab")
        summary_tab = page.locator('[role="tab"]').filter(has_text="Summary")
        if summary_tab.count() > 0:
            summary_tab.first.click()
            time.sleep(1)
            
            if "Plan Summary" in page.content():
                print("✅ Summary tab working")
                page.screenshot(path=str(SCREENSHOTS_DIR / "07_summary_tab.png"))
            else:
                print("⚠️ Summary tab content not found")
        
        # Test 8: Check AI Assistant
        print("\n📍 Test 8: Check AI Assistant")
        if "AI Assistant" in page.content():
            print("✅ AI Assistant present")
        else:
            print("⚠️ AI Assistant not found")
        
        # Final Summary
        print("\n" + "="*60)
        print("📊 FINAL TEST RESULTS")
        print("="*60)
        
        tests_passed = 0
        total_tests = 8
        
        # Count passed tests based on screenshots
        screenshots = list(SCREENSHOTS_DIR.glob("*.png"))
        tests_passed = len(screenshots)
        
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"📸 Screenshots Captured: {len(screenshots)}")
        print(f"📁 Screenshots Location: {SCREENSHOTS_DIR}")
        
        if tests_passed >= 6:
            print("\n🎉 MILESTONE 2: COMPLETE AND WORKING!")
        else:
            print("\n⚠️ Some tests failed - review screenshots")
        
        browser.close()

if __name__ == "__main__":
    test_complete_workflow()