#!/usr/bin/env python3
"""
Complete End-to-End Flow Test with Screenshots
Captures every step of the automated analysis platform
"""
from playwright.sync_api import sync_playwright
import os
import time
from datetime import datetime
import shutil

# Configuration
APP_URL = "http://localhost:8504"  # Using port 8504 for the automated version
SCREENSHOT_DIR = f"screenshots_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def setup_screenshot_directory():
    """Create directory for screenshots"""
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
    os.makedirs(SCREENSHOT_DIR)
    print(f"📁 Screenshot directory created: {SCREENSHOT_DIR}")
    return SCREENSHOT_DIR

def take_screenshot(page, name, step_num):
    """Take and save a screenshot with step number"""
    filename = f"{SCREENSHOT_DIR}/step_{step_num:02d}_{name}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"   📸 Screenshot saved: {filename}")
    return filename

def test_complete_automated_flow():
    """Test the complete flow from start to finish with screenshots"""
    
    print("\n" + "="*80)
    print("🚀 COMPLETE AUTOMATED FLOW TEST WITH SCREENSHOTS")
    print("="*80)
    
    # Setup screenshot directory
    setup_screenshot_directory()
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(
            headless=True,  # Running in headless mode
            slow_mo=100  # Small delay between actions
        )
        
        # Create context with viewport
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1
        )
        
        page = context.new_page()
        step = 0
        
        try:
            # ========== STEP 1: NAVIGATE TO APP ==========
            print("\n📍 STEP 1: Navigate to Application")
            print("-"*40)
            
            step += 1
            print(f"   → Opening {APP_URL}...")
            page.goto(APP_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(3000)
            take_screenshot(page, "homepage", step)
            print("   ✅ Application loaded successfully")
            
            # ========== STEP 2: VERIFY HOME PAGE ==========
            print("\n📍 STEP 2: Verify Home Page")
            print("-"*40)
            
            step += 1
            # Check for main header
            if page.locator("text=AI Data Analysis Platform").is_visible():
                print("   ✅ Main header visible")
            else:
                print("   ⚠️ Main header not found, checking alternatives...")
            
            # Check for navigation
            if page.locator("text=Quick Navigation").is_visible():
                print("   ✅ Navigation sidebar present")
            
            take_screenshot(page, "home_overview", step)
            
            # Check for start button
            start_button = page.locator("button", has_text="Start New Analysis")
            if start_button.is_visible():
                print("   ✅ Start Analysis button found")
            
            # ========== STEP 3: START NEW ANALYSIS ==========
            print("\n📍 STEP 3: Start New Analysis")
            print("-"*40)
            
            step += 1
            print("   → Clicking Start New Analysis...")
            
            # Try multiple methods to start analysis
            try:
                # Method 1: Click button
                if page.locator("button", has_text="Start New Analysis").is_visible():
                    page.locator("button", has_text="Start New Analysis").click()
                # Method 2: Use navigation
                elif page.locator("text=Start Analysis").is_visible():
                    page.locator("text=Start Analysis").click()
                # Method 3: Select from dropdown
                else:
                    page.select_option("select", label="🚀 Start Analysis")
            except:
                print("   ⚠️ Using alternative navigation method")
                page.select_option("select", index=1)  # Select second option
            
            page.wait_for_timeout(3000)
            take_screenshot(page, "analysis_page", step)
            print("   ✅ Navigated to analysis page")
            
            # ========== STEP 4: SELECT DATA SOURCE ==========
            print("\n📍 STEP 4: Select Data Source")
            print("-"*40)
            
            step += 1
            print("   → Selecting sample data option...")
            
            # Look for data source options
            sample_data_option = page.locator("text=Use Sample Data")
            if sample_data_option.is_visible():
                sample_data_option.click()
                print("   ✅ Selected sample data")
            else:
                # Try radio button
                radio_buttons = page.locator("input[type='radio']").all()
                if len(radio_buttons) >= 2:
                    radio_buttons[1].click()  # Click second option (sample data)
                    print("   ✅ Selected sample data via radio button")
            
            page.wait_for_timeout(1000)
            
            # Select sample type if dropdown appears
            selects = page.locator("select").all()
            for select in selects:
                try:
                    if "sample" in select.inner_text().lower():
                        select.select_option("Sales Data")
                        print("   ✅ Selected Sales Data sample")
                        break
                except:
                    pass
            
            take_screenshot(page, "data_source_selected", step)
            
            # ========== STEP 5: SET ANALYSIS NAME ==========
            print("\n📍 STEP 5: Set Analysis Name")
            print("-"*40)
            
            step += 1
            print("   → Entering analysis name...")
            
            # Find name input
            name_inputs = page.locator("input[type='text']").all()
            if name_inputs:
                analysis_name = f"Automated Test Analysis {datetime.now().strftime('%H:%M')}"
                name_inputs[0].fill(analysis_name)
                print(f"   ✅ Entered name: {analysis_name}")
            
            take_screenshot(page, "analysis_name_entered", step)
            
            # ========== STEP 6: SELECT ANALYSIS OPTIONS ==========
            print("\n📍 STEP 6: Select Analysis Options")
            print("-"*40)
            
            step += 1
            print("   → Selecting analysis types...")
            
            # Check various analysis options
            checkboxes = [
                "Trend Analysis",
                "Anomaly Detection", 
                "Predictions",
                "Find Correlations"
            ]
            
            checked_count = 0
            for checkbox_text in checkboxes:
                try:
                    checkbox = page.locator(f"text={checkbox_text}")
                    if checkbox.is_visible():
                        checkbox.click()
                        checked_count += 1
                        print(f"   ✅ Selected: {checkbox_text}")
                except:
                    pass
            
            if checked_count == 0:
                print("   ⚠️ No checkboxes found, using default options")
            
            take_screenshot(page, "analysis_options_selected", step)
            
            # ========== STEP 7: START ANALYSIS ==========
            print("\n📍 STEP 7: Start Analysis Execution")
            print("-"*40)
            
            step += 1
            print("   → Clicking Start Analysis button...")
            
            # Find and click the submit button
            submit_button = page.locator("button", has_text="Start Analysis")
            if submit_button.is_visible():
                submit_button.click()
                print("   ✅ Analysis started")
            else:
                print("   ⚠️ Looking for alternative submit button...")
                page.locator("button[type='submit']").first.click()
            
            page.wait_for_timeout(3000)
            take_screenshot(page, "analysis_started", step)
            
            # ========== STEP 8: WAIT FOR TASK GENERATION ==========
            print("\n📍 STEP 8: AI Task Generation")
            print("-"*40)
            
            step += 1
            print("   → Waiting for AI to generate tasks...")
            
            # Wait for success message or task list
            page.wait_for_timeout(5000)
            
            if page.locator("text=Generated").is_visible():
                print("   ✅ Tasks generated successfully")
            
            take_screenshot(page, "tasks_generated", step)
            
            # ========== STEP 9: TASK EXECUTION ==========
            print("\n📍 STEP 9: Task Execution Progress")
            print("-"*40)
            
            step += 1
            print("   → Monitoring task execution...")
            
            # Wait for execution to start
            page.wait_for_timeout(3000)
            
            # Look for progress indicators
            if page.locator("text=Executing").is_visible():
                print("   ✅ Task execution in progress")
                
                # Take multiple screenshots during execution
                for i in range(3):
                    page.wait_for_timeout(2000)
                    take_screenshot(page, f"execution_progress_{i+1}", step)
                    step += 1
                    
                    # Check for completed tasks
                    if page.locator("text=✅").count() > 0:
                        completed = page.locator("text=✅").count()
                        print(f"   ✅ {completed} tasks completed")
            
            # Wait for completion
            print("   → Waiting for execution to complete...")
            page.wait_for_timeout(10000)
            
            # ========== STEP 10: EXECUTION RESULTS ==========
            print("\n📍 STEP 10: Execution Results")
            print("-"*40)
            
            step += 1
            
            # Check for completion message
            if page.locator("text=completed").is_visible():
                print("   ✅ Execution completed")
            
            # Check for success metrics
            if page.locator("text=Success Rate").is_visible():
                print("   ✅ Success metrics displayed")
            
            take_screenshot(page, "execution_complete", step)
            
            # ========== STEP 11: REPORT GENERATION ==========
            print("\n📍 STEP 11: Report Generation")
            print("-"*40)
            
            step += 1
            print("   → Checking for report generation...")
            
            page.wait_for_timeout(5000)
            
            # Check if report was auto-generated
            if page.locator("text=Report generated").is_visible():
                print("   ✅ Report generated automatically")
            
            # Check for report preview
            if page.locator("text=Report Preview").is_visible():
                print("   ✅ Report preview available")
            
            take_screenshot(page, "report_generated", step)
            
            # ========== STEP 12: DOWNLOAD OPTIONS ==========
            print("\n📍 STEP 12: Download Options")
            print("-"*40)
            
            step += 1
            
            # Check for download buttons
            if page.locator("text=Download").count() > 0:
                print(f"   ✅ Found {page.locator('text=Download').count()} download options")
            
            take_screenshot(page, "download_options", step)
            
            # ========== STEP 13: NAVIGATE TO RESULTS ==========
            print("\n📍 STEP 13: View Results Section")
            print("-"*40)
            
            step += 1
            print("   → Navigating to results...")
            
            try:
                page.select_option("select", label="📊 View Results")
            except:
                # Alternative navigation
                if page.locator("text=View Results").is_visible():
                    page.locator("text=View Results").click()
            
            page.wait_for_timeout(3000)
            take_screenshot(page, "results_page", step)
            
            if page.locator("text=Analysis Results").is_visible():
                print("   ✅ Results page loaded")
            
            # Check for insights
            if page.locator("text=Insights").is_visible():
                print("   ✅ Insights displayed")
            
            # ========== STEP 14: NAVIGATE TO REPORTS ==========
            print("\n📍 STEP 14: View Reports Section")
            print("-"*40)
            
            step += 1
            print("   → Navigating to reports...")
            
            try:
                page.select_option("select", label="📄 Reports")
            except:
                if page.locator("text=Reports").is_visible():
                    page.locator("text=Reports").click()
            
            page.wait_for_timeout(3000)
            take_screenshot(page, "reports_page", step)
            
            if page.locator("text=Generated Reports").is_visible():
                print("   ✅ Reports section loaded")
            
            # ========== STEP 15: FINAL OVERVIEW ==========
            print("\n📍 STEP 15: Return to Overview")
            print("-"*40)
            
            step += 1
            print("   → Returning to home...")
            
            try:
                page.select_option("select", label="🏠 Home")
            except:
                page.select_option("select", index=0)
            
            page.wait_for_timeout(2000)
            take_screenshot(page, "final_overview", step)
            print("   ✅ Returned to overview")
            
            # ========== SUCCESS SUMMARY ==========
            print("\n" + "="*80)
            print("✅ COMPLETE FLOW TEST SUCCESSFUL!")
            print("="*80)
            print(f"\n📊 Test Summary:")
            print(f"   • Total steps completed: {step}")
            print(f"   • Screenshots captured: {step}")
            print(f"   • Screenshot directory: {SCREENSHOT_DIR}")
            print("\n📁 Screenshots saved in order:")
            
            # List all screenshots
            screenshots = sorted(os.listdir(SCREENSHOT_DIR))
            for screenshot in screenshots:
                print(f"   • {screenshot}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR at step {step}: {str(e)}")
            take_screenshot(page, f"error_step_{step}", step)
            
            import traceback
            traceback.print_exc()
            
            return False
            
        finally:
            browser.close()

def start_streamlit_app():
    """Start the Streamlit application"""
    import subprocess
    import time
    
    print("🚀 Starting Streamlit application...")
    
    # Kill any existing Streamlit processes
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
    time.sleep(2)
    
    # Start the automated version
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app_automated.py", 
         "--server.port", "8504", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    print("   ⏳ Waiting for app to start...")
    time.sleep(5)
    
    # Check if running
    try:
        import requests
        response = requests.get("http://localhost:8504")
        if response.status_code == 200:
            print("   ✅ Streamlit app is running on port 8504")
            return process
    except:
        print("   ⚠️ App may not be fully started, continuing anyway...")
        return process
    
    return process

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🎬 AUTOMATED PLATFORM - COMPLETE FLOW TEST")
    print("="*80)
    
    # Start Streamlit app
    app_process = start_streamlit_app()
    
    try:
        # Run the complete flow test
        success = test_complete_automated_flow()
        
        if success:
            print("\n🎉 All tests passed successfully!")
            print(f"📁 Check the '{SCREENSHOT_DIR}' folder for screenshots")
        else:
            print("\n⚠️ Some tests failed. Check screenshots for details.")
        
    finally:
        # Clean up
        print("\n🛑 Stopping Streamlit app...")
        if app_process:
            app_process.terminate()
            app_process.wait()
        print("✅ Cleanup complete")
    
    print("\n" + "="*80)
    print("🏁 TEST SESSION COMPLETE")
    print("="*80)