"""
Reality Check: What's Actually Working vs Mock UI
"""

from playwright.sync_api import sync_playwright
import time
from pathlib import Path

BASE_URL = "http://localhost:8506"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots" / "reality_check"
SCREENSHOTS_DIR.mkdir(exist_ok=True, parents=True)
TEST_DATA_DIR = Path(__file__).parent.parent / "data"

def test_what_actually_works():
    """Test what's real functionality vs pretty UI mockups"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("="*60)
        print("🔍 REALITY CHECK - WHAT'S ACTUALLY WORKING")
        print("="*60)
        
        # Start at Stage 0
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Test 1: File Upload - Does it actually process files?
        print("\n📍 TEST 1: File Upload Reality Check")
        
        # Go through Stage 0 workflow
        objectives_tab = page.locator('[role="tab"]').filter(has_text="Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.first.click()
            time.sleep(1)
            textarea = page.locator("textarea").first
            textarea.fill("Test data processing")
        
        # Upload a real file
        upload_tab = page.locator('[role="tab"]').filter(has_text="Data Upload")
        if upload_tab.count() > 0:
            upload_tab.first.click()
            time.sleep(1)
            
            # Create a CSV with specific content we can track
            test_file = TEST_DATA_DIR / "test_reality.csv"
            test_file.parent.mkdir(exist_ok=True)
            test_content = """name,age,salary,department
John Doe,25,50000,Engineering
Jane Smith,30,65000,Marketing  
Bob Johnson,35,75000,Sales
Alice Brown,28,55000,HR
Charlie Wilson,45,85000,Finance"""
            test_file.write_text(test_content)
            
            # Upload it
            file_input = page.locator("input[type='file']")
            if file_input.count() > 0:
                file_input.first.set_input_files(str(test_file))
                time.sleep(2)
                print("✅ File uploaded to UI")
                page.screenshot(path=str(SCREENSHOTS_DIR / "01_file_uploaded.png"))
        
        # Navigate to Stage 1
        review_tab = page.locator('[role="tab"]').filter(has_text="Review")
        if review_tab.count() > 0:
            review_tab.first.click()
            time.sleep(1)
        
        gen_btn = page.locator("button").filter(has_text="Generate Analysis Plan")
        if gen_btn.count() > 0:
            gen_btn.first.click()
            time.sleep(5)
        
        # Test 2: Go to Stage 2 and check data processing
        print("\n📍 TEST 2: Stage 2 Data Processing Reality Check")
        
        s2_btn = page.locator("button").filter(has_text="S2")
        if s2_btn.count() > 0:
            s2_btn.first.click()
            time.sleep(3)
            
            if "Data Understanding" in page.content():
                print("✅ Stage 2 loads")
                page.screenshot(path=str(SCREENSHOTS_DIR / "02_stage2_loaded.png"))
                
                # Check if our uploaded data appears
                if "test_reality.csv" in page.content():
                    print("✅ REAL: Uploaded file name appears in Stage 2")
                else:
                    print("❌ MOCK: Uploaded file not reflected in Stage 2")
                
                if "John Doe" in page.content() or "Jane Smith" in page.content():
                    print("✅ REAL: Actual file content is processed")
                else:
                    print("❌ MOCK: File content not processed, using sample data")
                
                # Check data metrics
                if "10,542" in page.content():
                    print("❌ MOCK: Hard-coded sample metrics (10,542 records)")
                else:
                    print("✅ REAL: Dynamic metrics from uploaded data")
                
                # Test profiling tab
                profiling_tab = page.locator('[role="tab"]').filter(has_text="Profiling")
                if profiling_tab.count() > 0:
                    profiling_tab.first.click()
                    time.sleep(2)
                    page.screenshot(path=str(SCREENSHOTS_DIR / "03_profiling_tab.png"))
                    
                    if "salary" in page.content() or "department" in page.content():
                        print("✅ REAL: Profiling shows actual uploaded columns")
                    else:
                        print("❌ MOCK: Profiling shows hard-coded sample columns")
        
        # Test 3: AI Integration Reality Check  
        print("\n📍 TEST 3: AI Integration Reality Check")
        
        # Go back to Stage 1 and test plan generation
        s1_btn = page.locator("button").filter(has_text="S1")
        if s1_btn.count() > 0:
            s1_btn.first.click()
            time.sleep(2)
            
            # Look at plan content
            if "Fallback Generator" in page.content():
                print("❌ MOCK: Using fallback AI generator")
            elif "confidence: 0.5" in page.content():
                print("❌ MOCK: Hard-coded plan confidence")
            else:
                print("✅ REAL: Using actual AI API")
        
        # Test 4: Chat Interface Reality Check
        print("\n📍 TEST 4: Chat Interface Reality Check")
        
        chat_input = page.locator("textarea").filter(has_text="Ask a question")
        send_btn = page.locator("button").filter(has_text="Send")
        
        if chat_input.count() > 0 and send_btn.count() > 0:
            chat_input.first.fill("What are the key findings from my data?")
            send_btn.first.click()
            time.sleep(3)
            
            page.screenshot(path=str(SCREENSHOTS_DIR / "04_chat_test.png"))
            
            if "No messages yet" in page.content():
                print("❌ MOCK: Chat interface not connected")
            else:
                print("✅ REAL: Chat interface responds")
        
        # Test 5: Export Functions Reality Check
        print("\n📍 TEST 5: Export Functions Reality Check")
        
        export_btn = page.locator("button").filter(has_text="Export")
        if export_btn.count() > 0:
            export_btn.first.click()
            time.sleep(1)
            
            # Check if actual file is created or just success message
            if "Report exported" in page.content():
                export_files = list(Path.cwd().glob("*report*"))
                if export_files:
                    print("✅ REAL: Export creates actual files")
                else:
                    print("❌ MOCK: Export shows message but no file created")
        
        # Final Summary
        print("\n" + "="*60)
        print("📊 REALITY CHECK SUMMARY")
        print("="*60)
        
        browser.close()

if __name__ == "__main__":
    test_what_actually_works()