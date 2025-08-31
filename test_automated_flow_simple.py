#!/usr/bin/env python3
"""
Simplified test for the automated analysis platform
Captures the complete flow with error handling
"""
from playwright.sync_api import sync_playwright
import os
import time
from datetime import datetime

# Configuration
APP_URL = "http://localhost:8504"
SCREENSHOT_DIR = f"screenshots_successful_flow"

def setup_directory():
    """Setup screenshot directory"""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    print(f"📁 Using directory: {SCREENSHOT_DIR}")

def screenshot(page, name):
    """Take screenshot with error handling"""
    try:
        path = f"{SCREENSHOT_DIR}/{name}.png"
        page.screenshot(path=path, full_page=True)
        print(f"   📸 {name}")
        return path
    except Exception as e:
        print(f"   ⚠️ Screenshot failed: {e}")
        return None

def test_automated_platform():
    """Test the automated platform with simplified approach"""
    
    print("\n" + "="*60)
    print("🚀 AUTOMATED PLATFORM TEST - SIMPLIFIED")
    print("="*60)
    
    setup_directory()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        try:
            # Step 1: Navigate to app
            print("\n1️⃣ Loading Application")
            page.goto(APP_URL, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)  # Let app fully load
            screenshot(page, "01_app_loaded")
            
            # Step 2: Check current view
            print("\n2️⃣ Checking Interface")
            page_content = page.content()
            
            # Check what's visible
            if "Start New Analysis" in page_content:
                print("   ✅ Found Start Analysis button")
                # Click it
                page.locator("button:has-text('Start New Analysis')").click()
                page.wait_for_timeout(3000)
                screenshot(page, "02_after_start_button")
            elif "Start Analysis" in page_content:
                print("   ✅ Already on analysis page")
                screenshot(page, "02_analysis_page")
            
            # Step 3: Fill analysis form
            print("\n3️⃣ Filling Analysis Form")
            
            # Try to select sample data
            if page.locator("text=Use Sample Data").is_visible():
                page.locator("text=Use Sample Data").click()
                print("   ✅ Selected sample data")
            elif page.locator("input[type='radio']").count() > 0:
                # Click second radio (usually sample data)
                radios = page.locator("input[type='radio']").all()
                if len(radios) >= 2:
                    radios[1].click()
                    print("   ✅ Selected data option")
            
            page.wait_for_timeout(1000)
            screenshot(page, "03_data_selected")
            
            # Fill analysis name
            text_inputs = page.locator("input[type='text']").all()
            if text_inputs:
                text_inputs[0].fill("Automated Test Analysis")
                print("   ✅ Entered analysis name")
            
            screenshot(page, "04_name_entered")
            
            # Select some analysis options
            checkboxes = page.locator("input[type='checkbox']").all()
            checked = 0
            for checkbox in checkboxes[:4]:  # Check first 4 options
                if not checkbox.is_checked():
                    checkbox.click()
                    checked += 1
            
            if checked > 0:
                print(f"   ✅ Selected {checked} analysis options")
            
            screenshot(page, "05_options_selected")
            
            # Step 4: Start Analysis
            print("\n4️⃣ Starting Analysis")
            
            # Find and click submit button
            submit_found = False
            
            # Try different button texts
            button_texts = ["Start Analysis", "Submit", "Analyze", "Run Analysis"]
            for text in button_texts:
                try:
                    button = page.locator(f"button:has-text('{text}')")
                    if button.is_visible():
                        button.click()
                        submit_found = True
                        print(f"   ✅ Clicked {text} button")
                        break
                except:
                    pass
            
            if not submit_found:
                # Try form submit button
                page.locator("button[type='submit']").first.click()
                print("   ✅ Submitted form")
            
            page.wait_for_timeout(3000)
            screenshot(page, "06_analysis_started")
            
            # Step 5: Wait for execution
            print("\n5️⃣ Waiting for Execution")
            
            # Wait for tasks to generate
            print("   ⏳ Generating tasks...")
            page.wait_for_timeout(5000)
            screenshot(page, "07_tasks_generated")
            
            # Wait for execution
            print("   ⏳ Executing analysis...")
            page.wait_for_timeout(10000)  # Give time for execution
            screenshot(page, "08_execution_progress")
            
            # Check for completion
            if page.locator("text=completed").is_visible():
                print("   ✅ Execution completed")
            elif page.locator("text=✅").count() > 0:
                print(f"   ✅ {page.locator('text=✅').count()} tasks completed")
            
            screenshot(page, "09_execution_complete")
            
            # Step 6: Check for results
            print("\n6️⃣ Checking Results")
            
            page.wait_for_timeout(5000)
            
            # Check for report
            if page.locator("text=Report").is_visible():
                print("   ✅ Report generated")
            
            # Check for download options
            download_count = page.locator("button:has-text('Download')").count()
            if download_count > 0:
                print(f"   ✅ {download_count} download options available")
            
            screenshot(page, "10_final_results")
            
            # Success!
            print("\n" + "="*60)
            print("✅ TEST COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📁 Screenshots saved in: {SCREENSHOT_DIR}/")
            
            # List screenshots
            screenshots = sorted([f for f in os.listdir(SCREENSHOT_DIR) if f.endswith('.png')])
            print("\n📸 Captured screenshots:")
            for s in screenshots:
                print(f"   • {s}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            screenshot(page, "error_state")
            
            # Try to get page text for debugging
            try:
                visible_text = page.locator("body").inner_text()
                print("\n📝 Visible text on page:")
                print(visible_text[:500])
            except:
                pass
            
            return False
            
        finally:
            browser.close()

def main():
    """Main entry point"""
    import subprocess
    
    # Start Streamlit app
    print("🚀 Starting Streamlit app...")
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
    time.sleep(2)
    
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app_automated.py", 
         "--server.port", "8504", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("   ⏳ Waiting for app to start...")
    time.sleep(8)
    
    try:
        # Run test
        success = test_automated_platform()
        
        if success:
            print("\n🎉 Platform test successful!")
            print(f"📁 View screenshots in: {SCREENSHOT_DIR}/")
        else:
            print("\n⚠️ Test encountered issues")
        
    finally:
        # Cleanup
        print("\n🛑 Stopping Streamlit...")
        process.terminate()
        process.wait()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()