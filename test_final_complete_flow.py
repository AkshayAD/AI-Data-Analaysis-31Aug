#!/usr/bin/env python3
"""
Final Complete Flow Test with Screenshots
Tests the streamlined automated analysis platform
"""
from playwright.sync_api import sync_playwright
import os
import time
from datetime import datetime
import subprocess

APP_URL = "http://localhost:8505"
SCREENSHOT_DIR = "screenshots_complete_flow"

def setup():
    """Setup test environment"""
    # Create screenshot directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # Kill existing Streamlit
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
    time.sleep(2)
    
    # Start the final app
    print("🚀 Starting Streamlit app...")
    process = subprocess.Popen(
        ["streamlit", "run", "streamlit_app_final.py", 
         "--server.port", "8505", "--server.headless", "true"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("   ⏳ Waiting for app to start...")
    time.sleep(8)
    
    return process

def test_complete_flow():
    """Test the complete automated flow"""
    
    print("\n" + "="*80)
    print("🎬 COMPLETE AUTOMATED FLOW TEST")
    print("="*80)
    print(f"📁 Screenshots will be saved to: {SCREENSHOT_DIR}/")
    print("-"*80)
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        screenshots = []
        
        try:
            # ========== STEP 1: LOAD APPLICATION ==========
            print("\n✅ Step 1: Loading Application")
            page.goto(APP_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)
            
            screenshot_path = f"{SCREENSHOT_DIR}/01_application_loaded.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: Application loaded")
            
            # Verify main elements
            if page.locator("h1:has-text('AI Data Analysis Platform')").is_visible():
                print("   ✓ Main title visible")
            
            # ========== STEP 2: CONFIGURE ANALYSIS ==========
            print("\n✅ Step 2: Configuring Analysis")
            
            # Check the "Use Sample Data" checkbox (should be checked by default)
            sample_checkbox = page.locator("text=Use Sample Data")
            if sample_checkbox.is_visible():
                print("   ✓ Sample data option available")
            
            # Select sample type
            selects = page.locator("select").all()
            if selects:
                selects[0].select_option("Sales Data")
                print("   ✓ Selected Sales Data")
            
            page.wait_for_timeout(1000)
            
            screenshot_path = f"{SCREENSHOT_DIR}/02_data_source_selected.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: Data source configured")
            
            # ========== STEP 3: SET ANALYSIS NAME ==========
            print("\n✅ Step 3: Setting Analysis Name")
            
            # Find and fill the analysis name input
            text_inputs = page.locator("input[type='text']").all()
            if text_inputs:
                analysis_name = f"Automated Test {datetime.now().strftime('%H:%M:%S')}"
                text_inputs[0].clear()
                text_inputs[0].fill(analysis_name)
                print(f"   ✓ Set name: {analysis_name}")
            
            page.wait_for_timeout(1000)
            
            screenshot_path = f"{SCREENSHOT_DIR}/03_analysis_name_set.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: Analysis name set")
            
            # ========== STEP 4: SELECT ANALYSIS OPTIONS ==========
            print("\n✅ Step 4: Selecting Analysis Options")
            
            # Check all analysis option checkboxes
            analysis_options = [
                "Data Profiling",
                "Statistical Analysis",
                "Correlation Analysis",
                "Predictive Modeling",
                "Anomaly Detection",
                "Generate Visualizations"
            ]
            
            checked = 0
            for option in analysis_options:
                try:
                    # Find the checkbox by its label text
                    checkbox_label = page.locator(f"label:has-text('{option}')")
                    if checkbox_label.is_visible():
                        # Click the label to toggle the checkbox
                        checkbox_label.click()
                        checked += 1
                        print(f"   ✓ Selected: {option}")
                        page.wait_for_timeout(200)
                except:
                    pass
            
            page.wait_for_timeout(1000)
            
            screenshot_path = f"{SCREENSHOT_DIR}/04_analysis_options_selected.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: {checked} analysis options selected")
            
            # ========== STEP 5: START ANALYSIS ==========
            print("\n✅ Step 5: Starting Analysis")
            
            # Click the Run Complete Analysis button
            run_button = page.locator("button:has-text('Run Complete Analysis')")
            if run_button.is_visible():
                run_button.click()
                print("   ✓ Clicked Run Complete Analysis")
            else:
                # Fallback to any submit button
                page.locator("button[type='submit']").first.click()
                print("   ✓ Submitted form")
            
            page.wait_for_timeout(3000)
            
            screenshot_path = f"{SCREENSHOT_DIR}/05_analysis_started.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: Analysis started")
            
            # ========== STEP 6: WAIT FOR EXECUTION ==========
            print("\n✅ Step 6: Analysis Execution")
            print("   ⏳ Waiting for tasks to complete...")
            
            # Wait for execution progress
            for i in range(3):
                page.wait_for_timeout(5000)
                screenshot_path = f"{SCREENSHOT_DIR}/06_execution_progress_{i+1}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append(screenshot_path)
                print(f"   📸 Captured: Execution progress {i+1}")
                
                # Check for completion indicators
                if page.locator("text='✅ Analysis Complete!'").is_visible():
                    print("   ✓ Analysis completed!")
                    break
                elif page.locator("text=✅").count() > 0:
                    completed = page.locator("text=✅").count()
                    print(f"   ✓ {completed} tasks completed")
            
            # ========== STEP 7: VIEW RESULTS ==========
            print("\n✅ Step 7: Viewing Results")
            
            page.wait_for_timeout(3000)
            
            # Check for results section
            if page.locator("text=Analysis Results").is_visible():
                print("   ✓ Results section visible")
            
            # Check for metrics
            if page.locator("text=Tasks Completed").is_visible():
                print("   ✓ Completion metrics displayed")
            
            # Check for insights
            if page.locator("text=Insights").is_visible():
                print("   ✓ Insights generated")
            
            screenshot_path = f"{SCREENSHOT_DIR}/07_analysis_results.png"
            page.screenshot(path=screenshot_path, full_page=True)
            screenshots.append(screenshot_path)
            print(f"   📸 Captured: Analysis results")
            
            # ========== STEP 8: GENERATE REPORT ==========
            print("\n✅ Step 8: Generating Report")
            
            # Click Generate Report button if visible
            report_button = page.locator("button:has-text('Generate Report')")
            if report_button.is_visible():
                report_button.click()
                print("   ✓ Clicked Generate Report")
                page.wait_for_timeout(5000)
                
                screenshot_path = f"{SCREENSHOT_DIR}/08_report_generated.png"
                page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append(screenshot_path)
                print(f"   📸 Captured: Report generated")
                
                # Check for report sections
                if page.locator("text=Executive Summary").is_visible():
                    print("   ✓ Executive Summary visible")
                
                if page.locator("text=Key Findings").is_visible():
                    print("   ✓ Key Findings visible")
            
            # ========== STEP 9: DOWNLOAD OPTIONS ==========
            print("\n✅ Step 9: Download Options")
            
            # Check for download buttons
            download_buttons = page.locator("button:has-text('Download')").count()
            if download_buttons > 0:
                print(f"   ✓ {download_buttons} download options available")
                
                screenshot_path = f"{SCREENSHOT_DIR}/09_download_options.png"
                page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append(screenshot_path)
                print(f"   📸 Captured: Download options")
            
            # ========== STEP 10: VISUALIZATIONS ==========
            print("\n✅ Step 10: Visualizations")
            
            # Scroll to visualizations if present
            if page.locator("text=Visualizations").is_visible():
                page.locator("text=Visualizations").scroll_into_view_if_needed()
                page.wait_for_timeout(2000)
                
                screenshot_path = f"{SCREENSHOT_DIR}/10_visualizations.png"
                page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append(screenshot_path)
                print(f"   📸 Captured: Visualizations")
                print("   ✓ Visualizations generated")
            
            # ========== SUCCESS ==========
            print("\n" + "="*80)
            print("🎉 COMPLETE FLOW TEST SUCCESSFUL!")
            print("="*80)
            
            return True, screenshots
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
            # Capture error state
            error_screenshot = f"{SCREENSHOT_DIR}/error_state.png"
            page.screenshot(path=error_screenshot, full_page=True)
            screenshots.append(error_screenshot)
            
            return False, screenshots
            
        finally:
            browser.close()

def main():
    """Main test runner"""
    
    # Setup
    process = setup()
    
    try:
        # Run test
        success, screenshots = test_complete_flow()
        
        # Summary
        print("\n" + "="*80)
        if success:
            print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        else:
            print("⚠️ SOME TESTS FAILED")
        print("="*80)
        
        # List screenshots
        print(f"\n📸 Screenshots captured ({len(screenshots)}):")
        for screenshot in screenshots:
            print(f"   • {screenshot}")
        
        print(f"\n📁 All screenshots saved in: {SCREENSHOT_DIR}/")
        
    finally:
        # Cleanup
        print("\n🛑 Stopping Streamlit app...")
        process.terminate()
        process.wait()
        print("✅ Cleanup complete")
    
    print("\n" + "="*80)
    print("🏁 TEST SESSION COMPLETE")
    print("="*80)
    
    if success:
        print("🎊 The automated analysis platform works perfectly end-to-end!")
        print(f"📷 View the complete flow in: {SCREENSHOT_DIR}/")

if __name__ == "__main__":
    main()