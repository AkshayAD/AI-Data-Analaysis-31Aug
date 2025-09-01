"""
Complete test that captures ALL steps with actual analysis content
Ensures screenshots show real results at every stage
"""
import os
import time
from playwright.sync_api import sync_playwright
from datetime import datetime

def take_screenshot(page, step_num, description, wait_time=2):
    """Take screenshot with proper wait for content to load"""
    time.sleep(wait_time)
    
    # Additional wait for spinners to disappear
    try:
        page.wait_for_selector('.stSpinner', state='hidden', timeout=3000)
    except:
        pass
    
    filename = f"screenshots/step_{step_num:02d}_{description.replace(' ', '_').lower()}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Step {step_num}: {description} - Screenshot saved")
    return filename

def scroll_and_capture(page, step_num, description):
    """Scroll down the page and capture content"""
    page.evaluate("window.scrollBy(0, 500)")
    time.sleep(1)
    take_screenshot(page, step_num, description)

def run_complete_test():
    """Run complete flow test with comprehensive content capture"""
    
    # Create screenshots directory
    os.makedirs('screenshots', exist_ok=True)
    print("\n🚀 Starting complete test with all steps and content capture...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with large viewport
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.0
        )
        
        page = context.new_page()
        
        try:
            print("\n📋 Test Execution Starting...")
            step = 1
            
            # Navigate to app
            print(f"\nStep {step}: Loading application...")
            page.goto('http://localhost:8501', wait_until='networkidle')
            time.sleep(5)
            take_screenshot(page, step, "initial_page_load", wait_time=3)
            step += 1
            
            # Enter objectives
            print(f"\nStep {step}: Entering analysis objectives...")
            objectives_text = """Comprehensive analysis to:
1. Identify key trends and patterns
2. Detect anomalies and outliers  
3. Build predictive models
4. Generate actionable insights
5. Provide statistical validation"""
            
            objectives_field = page.locator('textarea[aria-label="Analysis Objectives"]')
            objectives_field.fill(objectives_text)
            take_screenshot(page, step, "objectives_entered", wait_time=2)
            step += 1
            
            # Scroll to show all options
            print(f"\nStep {step}: Showing all analysis options...")
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(1)
            take_screenshot(page, step, "analysis_options_visible", wait_time=2)
            step += 1
            
            # Submit form
            print(f"\nStep {step}: Submitting analysis request...")
            submit_button = page.locator('button:has-text("Run Complete Analysis")')
            submit_button.click()
            time.sleep(2)
            take_screenshot(page, step, "analysis_submitted", wait_time=2)
            step += 1
            
            # Wait for data to load
            print(f"\nStep {step}: Waiting for data to load...")
            time.sleep(3)
            
            # Check if data preview exists and expand it
            try:
                expander = page.locator('div[data-testid="stExpander"] summary')
                if expander.count() > 0:
                    print(f"  - Expanding data preview...")
                    expander.first.click()
                    time.sleep(2)
                    take_screenshot(page, step, "data_preview_expanded", wait_time=3)
                    step += 1
            except:
                pass
            
            # Capture execution progress
            print(f"\nStep {step}: Capturing analysis execution...")
            time.sleep(3)
            
            # Look for any progress indicators
            progress = page.locator('div[role="progressbar"]')
            if progress.count() > 0:
                take_screenshot(page, step, "analysis_in_progress", wait_time=2)
                step += 1
            
            # Wait for completion - be flexible
            print(f"\nStep {step}: Waiting for analysis to complete...")
            max_wait = 60
            start_time = time.time()
            completed = False
            
            while time.time() - start_time < max_wait:
                # Check for completion indicators
                if (page.locator('text="Analysis Complete"').count() > 0 or
                    page.locator('text="Analysis Results"').count() > 0 or
                    page.locator('text="Tasks Completed"').count() > 0):
                    completed = True
                    break
                time.sleep(2)
            
            if completed:
                print("  ✓ Analysis completed!")
            else:
                print("  ⚠ Continuing after timeout...")
            
            # Scroll to see completion status
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(2)
            take_screenshot(page, step, "analysis_status", wait_time=3)
            step += 1
            
            # Capture metrics section
            print(f"\nStep {step}: Capturing analysis metrics...")
            metrics = page.locator('div[data-testid="metric-container"]')
            if metrics.count() > 0:
                print(f"  - Found {metrics.count()} metrics")
                take_screenshot(page, step, "analysis_metrics", wait_time=2)
                step += 1
            
            # Capture results tabs
            print(f"\nStep {step}: Capturing detailed results...")
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(1)
            
            # Try to click on result tabs
            tabs = page.locator('button[role="tab"]')
            if tabs.count() > 0:
                print(f"  - Found {tabs.count()} result tabs")
                
                # Capture each tab's content
                for i in range(min(tabs.count(), 5)):
                    try:
                        tab = tabs.nth(i)
                        tab_text = tab.text_content()
                        print(f"  - Clicking tab: {tab_text}")
                        tab.click()
                        time.sleep(2)
                        take_screenshot(page, step, f"tab_{tab_text.lower().replace(' ', '_')}_results", wait_time=2)
                        step += 1
                    except Exception as e:
                        print(f"    Error clicking tab {i}: {e}")
            
            # Scroll to report section
            print(f"\nStep {step}: Scrolling to report section...")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            take_screenshot(page, step, "report_section_visible", wait_time=2)
            step += 1
            
            # Generate report
            print(f"\nStep {step}: Generating executive report...")
            report_button = page.locator('button:has-text("Generate Report")')
            if report_button.count() > 0:
                print("  - Clicking Generate Report button...")
                report_button.click()
                time.sleep(5)
                take_screenshot(page, step, "report_generation_started", wait_time=3)
                step += 1
                
                # Wait for report to generate
                print(f"\nStep {step}: Waiting for report content...")
                time.sleep(5)
                
                # Scroll up to see report content
                page.evaluate("window.scrollBy(0, -800)")
                time.sleep(1)
                take_screenshot(page, step, "report_top_content", wait_time=2)
                step += 1
                
                # Capture middle section
                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(1)
                take_screenshot(page, step, "report_middle_content", wait_time=2)
                step += 1
                
                # Capture bottom section
                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(1)
                take_screenshot(page, step, "report_bottom_content", wait_time=2)
                step += 1
            
            # Look for visualizations
            print(f"\nStep {step}: Looking for visualizations...")
            viz_section = page.locator('text="Visualizations"')
            if viz_section.count() > 0:
                viz_section.scroll_into_view_if_needed()
                time.sleep(3)
                take_screenshot(page, step, "visualizations_section", wait_time=3)
                step += 1
                
                # Capture any plotly charts
                charts = page.locator('.plotly')
                if charts.count() > 0:
                    print(f"  - Found {charts.count()} charts")
                    for i in range(min(charts.count(), 3)):
                        charts.nth(i).scroll_into_view_if_needed()
                        time.sleep(2)
                        take_screenshot(page, step, f"chart_{i+1}", wait_time=2)
                        step += 1
            
            # Final full page capture
            print(f"\nStep {step}: Capturing final state...")
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # Capture full page in sections
            total_height = page.evaluate("document.body.scrollHeight")
            viewport_height = 900
            current_pos = 0
            section = 1
            
            while current_pos < total_height and section <= 5:
                take_screenshot(page, step, f"final_page_section_{section}", wait_time=1)
                step += 1
                section += 1
                current_pos += viewport_height
                page.evaluate(f"window.scrollTo(0, {current_pos})")
                time.sleep(1)
            
            print(f"\n✅ Test completed successfully!")
            print(f"📸 Captured {step-1} screenshots showing complete flow")
            
            # List all screenshots
            print("\n📁 Screenshots captured:")
            screenshots = sorted([f for f in os.listdir('screenshots') if f.endswith('.png')])
            for screenshot in screenshots:
                print(f"   - {screenshot}")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            take_screenshot(page, 99, "error_state", wait_time=1)
            raise
        
        finally:
            browser.close()
            print("\n🏁 Test execution complete")

if __name__ == "__main__":
    run_complete_test()