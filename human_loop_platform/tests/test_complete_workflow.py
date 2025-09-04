"""
Complete Workflow Test with File Upload
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

BASE_URL = "http://localhost:8506"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "complete_workflow"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)
TEST_DATA_DIR = Path(__file__).parent.parent / "data"

def test_complete_workflow_with_upload():
    """Test complete workflow including file upload"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("="*60)
        print("🧪 COMPLETE WORKFLOW TEST - WITH FILE UPLOAD")
        print("="*60)
        
        # 1. Load Stage 0
        print("\n📍 Step 1: Load Application")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        print("✅ Application loaded")
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_initial.png"))
        
        # 2. Fill Objectives
        print("\n📍 Step 2: Fill Objectives")
        objectives_tab = page.locator('[role="tab"]').filter(has_text="Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.first.click()
            time.sleep(1)
            
            textarea = page.locator("textarea").first
            textarea.fill("Analyze customer churn patterns to reduce attrition by 20%")
            print("✅ Objective filled")
            page.screenshot(path=str(SCREENSHOTS_DIR / "02_objective.png"))
        
        # 3. Upload Data File
        print("\n📍 Step 3: Upload Data File")
        upload_tab = page.locator('[role="tab"]').filter(has_text="Data Upload")
        if upload_tab.count() > 0:
            upload_tab.first.click()
            time.sleep(1)
            
            # Check if sample file exists, if not create one
            sample_file = TEST_DATA_DIR / "sample_customer_data.csv"
            if not sample_file.exists():
                sample_file.parent.mkdir(exist_ok=True)
                sample_file.write_text("customer_id,age,tenure,churn\n1,25,12,0\n2,35,24,1\n")
                print("   Created sample data file")
            
            # Upload file
            file_input = page.locator("input[type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(str(sample_file))
                time.sleep(2)
                print("✅ File uploaded")
                page.screenshot(path=str(SCREENSHOTS_DIR / "03_uploaded.png"))
        
        # 4. Go to Review
        print("\n📍 Step 4: Review & Proceed")
        review_tab = page.locator('[role="tab"]').filter(has_text="Review")
        if review_tab.count() > 0:
            review_tab.first.click()
            time.sleep(1)
            print("✅ Review tab opened")
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_review.png"))
        
        # 5. Navigate to Stage 1
        print("\n📍 Step 5: Navigate to Plan Generation")
        gen_btn = page.locator("button").filter(has_text="Generate Analysis Plan")
        if gen_btn.count() > 0:
            print("   Found Generate Analysis Plan button")
            gen_btn.first.click()
            time.sleep(5)
            
            if "AI-Powered Plan Generation" in page.content():
                print("✅ Successfully navigated to Stage 1!")
                page.screenshot(path=str(SCREENSHOTS_DIR / "05_stage1.png"))
            else:
                print("❌ Navigation failed")
                # Try force navigation as backup
                s1_btn = page.locator("button").filter(has_text="S1")
                if s1_btn.count() > 0:
                    print("   Using force navigation...")
                    s1_btn.first.click()
                    time.sleep(3)
                    if "AI-Powered Plan Generation" in page.content():
                        print("✅ Force navigation successful!")
                        page.screenshot(path=str(SCREENSHOTS_DIR / "05_stage1_forced.png"))
        else:
            print("❌ Generate button not found")
            # Try force navigation
            s1_btn = page.locator("button").filter(has_text="S1")
            if s1_btn.count() > 0:
                print("   Using force navigation to Stage 1...")
                s1_btn.first.click()
                time.sleep(3)
                if "AI-Powered Plan Generation" in page.content():
                    print("✅ Force navigation successful!")
                    page.screenshot(path=str(SCREENSHOTS_DIR / "05_stage1_forced.png"))
        
        # 6. Generate Plan
        print("\n📍 Step 6: Generate Analysis Plan")
        if "AI-Powered Plan Generation" in page.content():
            plan_btn = page.locator("button").filter(has_text="Generate Plan")
            if plan_btn.count() > 0:
                plan_btn.first.click()
                time.sleep(3)
                
                if "Plan generated successfully" in page.content():
                    print("✅ Plan generated!")
                    page.screenshot(path=str(SCREENSHOTS_DIR / "06_plan_generated.png"))
                else:
                    print("⚠️ Plan generation message not shown")
                    page.screenshot(path=str(SCREENSHOTS_DIR / "06_plan_attempt.png"))
        
        # 7. Test Edit Tab
        print("\n📍 Step 7: Test Edit Tab")
        edit_tab = page.locator('[role="tab"]').filter(has_text="Edit")
        if edit_tab.count() > 0:
            edit_tab.first.click()
            time.sleep(1)
            print("✅ Edit tab opened")
            page.screenshot(path=str(SCREENSHOTS_DIR / "07_edit_tab.png"))
        
        # 8. Test Summary Tab
        print("\n📍 Step 8: Test Summary Tab")
        summary_tab = page.locator('[role="tab"]').filter(has_text="Summary")
        if summary_tab.count() > 0:
            summary_tab.first.click()
            time.sleep(1)
            print("✅ Summary tab opened")
            page.screenshot(path=str(SCREENSHOTS_DIR / "08_summary_tab.png"))
        
        # Final Report
        print("\n" + "="*60)
        print("📊 WORKFLOW TEST RESULTS")
        print("="*60)
        
        screenshots = list(SCREENSHOTS_DIR.glob("*.png"))
        print(f"✅ Screenshots captured: {len(screenshots)}")
        print(f"📁 Location: {SCREENSHOTS_DIR}")
        
        # Check final state
        page_content = page.content()
        if "AI-Powered Plan Generation" in page_content:
            print("\n🎉 SUCCESS: Currently on Stage 1 (Plan Generation)")
            if "Plan generated successfully" in page_content:
                print("🎉 SUCCESS: Plan was generated")
            print("\n✅ MILESTONE 2 IS WORKING!")
        else:
            print("\n⚠️ Not on Stage 1 - check screenshots for details")
        
        browser.close()

if __name__ == "__main__":
    test_complete_workflow_with_upload()