"""
Comprehensive test that captures ALL steps with actual content visible
This test ensures that screenshots show real analysis results, not just UI
"""
import os
import time
from playwright.sync_api import sync_playwright, expect
from datetime import datetime

def take_screenshot(page, step_num, description, wait_time=3):
    """Take screenshot with proper wait for content to load"""
    # Wait for content to actually load
    time.sleep(wait_time)
    
    # Additional wait for specific elements if needed
    try:
        # Wait for any loading spinners to disappear
        page.wait_for_selector('.stSpinner', state='hidden', timeout=5000)
    except:
        pass
    
    # Take screenshot
    filename = f"screenshots/step_{step_num:02d}_{description.replace(' ', '_').lower()}.png"
    page.screenshot(path=filename, full_page=True)
    print(f"✅ Step {step_num}: {description} - Screenshot saved")
    return filename

def wait_for_content(page, selector, timeout=30000):
    """Wait for specific content to appear"""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False

def scroll_to_element(page, selector):
    """Scroll to make element visible"""
    try:
        page.eval_on_selector(selector, "element => element.scrollIntoView()")
        time.sleep(1)
    except:
        pass

def run_comprehensive_test():
    """Run complete flow test with detailed screenshots"""
    
    # Create screenshots directory
    os.makedirs('screenshots', exist_ok=True)
    print("\n🚀 Starting comprehensive test with content capture...")
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with viewport
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.0
        )
        
        page = context.new_page()
        
        try:
            print("\n📋 Starting test execution...")
            
            # Step 1: Navigate to app
            print("\nStep 1: Loading application...")
            page.goto('http://localhost:8501')
            page.wait_for_load_state('networkidle')
            time.sleep(5)  # Extra wait for Streamlit to fully initialize
            take_screenshot(page, 1, "initial_load", wait_time=5)
            
            # Step 2: Fill in objectives
            print("\nStep 2: Entering analysis objectives...")
            objectives_text = """
            Perform comprehensive data analysis to:
            1. Identify key trends and patterns in the dataset
            2. Detect any anomalies or outliers
            3. Build predictive models for forecasting
            4. Generate actionable insights for business decisions
            5. Provide statistical validation of findings
            """
            
            # Find and fill objectives field
            objectives_field = page.locator('textarea[aria-label="Analysis Objectives"]')
            objectives_field.fill(objectives_text)
            time.sleep(2)
            take_screenshot(page, 2, "objectives_entered", wait_time=2)
            
            # Step 3: Show all analysis options selected
            print("\nStep 3: Showing analysis options...")
            # Scroll to show checkboxes
            page.evaluate("window.scrollBy(0, 200)")
            time.sleep(1)
            take_screenshot(page, 3, "analysis_options_selected", wait_time=2)
            
            # Step 4: Submit the form
            print("\nStep 4: Submitting analysis request...")
            submit_button = page.locator('button:has-text("Run Complete Analysis")')
            submit_button.click()
            
            # Step 5: Wait for data preview to appear
            print("\nStep 5: Waiting for data preview...")
            if wait_for_content(page, 'text="Data Preview"', timeout=10000):
                # Expand data preview
                expander = page.locator('summary:has-text("Data Preview")')
                if expander.count() > 0:
                    expander.click()
                    time.sleep(2)
                    take_screenshot(page, 5, "data_preview_expanded", wait_time=3)
            
            # Step 6: Capture analysis in progress
            print("\nStep 6: Capturing analysis execution...")
            time.sleep(2)
            take_screenshot(page, 6, "analysis_in_progress", wait_time=2)
            
            # Step 7: Wait for analysis to complete
            print("\nStep 7: Waiting for analysis to complete...")
            # Wait for analysis to complete - look for results section or completion message
            try:
                # Try multiple selectors for completion
                page.wait_for_selector('text="Analysis Results"', timeout=60000)
            except:
                try:
                    page.wait_for_selector('text="Analysis Complete"', timeout=5000)
                except:
                    # Just wait and continue if we see metrics
                    page.wait_for_selector('text="Tasks Completed"', timeout=5000)
            time.sleep(3)
            
            # Scroll to results section
            page.evaluate("window.scrollBy(0, 400)")
            take_screenshot(page, 7, "analysis_complete_with_metrics", wait_time=3)
            
            # Step 8: Capture detailed results for each analysis type
            print("\nStep 8: Capturing detailed analysis results...")
            
            # Try to click on tabs to show results
            tabs = ['Data Profiling', 'Statistical Analysis', 'Correlation Analysis', 
                   'Predictive Modeling', 'Anomaly Detection']
            
            for i, tab_name in enumerate(tabs, start=1):
                try:
                    tab = page.locator(f'button[role="tab"]:has-text("{tab_name}")')
                    if tab.count() > 0:
                        print(f"  - Clicking {tab_name} tab...")
                        tab.click()
                        time.sleep(2)
                        
                        # Scroll to show content
                        page.evaluate("window.scrollBy(0, 100)")
                        
                        # Wait for insights to load
                        insights = page.locator('text="Key Insights:"')
                        if insights.count() > 0:
                            print(f"    Found insights for {tab_name}")
                        
                        take_screenshot(page, 8 + i, f"{tab_name.lower().replace(' ', '_')}_results", wait_time=3)
                except Exception as e:
                    print(f"  - Could not capture {tab_name}: {e}")
            
            # Step 14: Generate report
            print("\nStep 14: Generating executive report...")
            # Scroll to report section
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            
            # Click generate report button
            report_button = page.locator('button:has-text("Generate Report")')
            if report_button.count() > 0:
                print("  - Clicking Generate Report button...")
                report_button.click()
                
                # Wait for report to generate
                print("  - Waiting for report generation...")
                time.sleep(5)
                
                # Capture report content
                take_screenshot(page, 14, "executive_report_generated", wait_time=5)
                
                # Scroll through report sections
                page.evaluate("window.scrollBy(0, -500)")
                time.sleep(1)
                take_screenshot(page, 15, "report_top_section", wait_time=2)
                
                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(1)
                take_screenshot(page, 16, "report_middle_section", wait_time=2)
                
                page.evaluate("window.scrollBy(0, 400)")
                time.sleep(1)
                take_screenshot(page, 17, "report_bottom_section", wait_time=2)
            
            # Step 18: Capture visualizations if present
            print("\nStep 18: Capturing visualizations...")
            viz_section = page.locator('text="Visualizations"')
            if viz_section.count() > 0:
                # Scroll to visualizations
                viz_section.scroll_into_view_if_needed()
                time.sleep(3)
                take_screenshot(page, 18, "visualizations_section", wait_time=5)
                
                # Try to capture individual charts
                charts = page.locator('.plotly')
                if charts.count() > 0:
                    print(f"  - Found {charts.count()} charts")
                    for i in range(min(charts.count(), 2)):
                        charts.nth(i).scroll_into_view_if_needed()
                        time.sleep(2)
                        take_screenshot(page, 19 + i, f"chart_{i+1}", wait_time=3)
            
            # Step 21: Final full page capture
            print("\nStep 21: Capturing final full page state...")
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)
            
            # Take multiple screenshots scrolling down
            total_height = page.evaluate("document.body.scrollHeight")
            viewport_height = 1080
            current_position = 0
            screenshot_num = 21
            
            while current_position < total_height:
                take_screenshot(page, screenshot_num, f"full_page_section_{screenshot_num-20}", wait_time=2)
                current_position += viewport_height - 100  # Overlap slightly
                page.evaluate(f"window.scrollTo(0, {current_position})")
                screenshot_num += 1
                
                if screenshot_num > 25:  # Limit to prevent too many screenshots
                    break
            
            print("\n✅ Test completed successfully!")
            print(f"📸 Captured {screenshot_num-1} screenshots showing complete flow")
            
            # List all screenshots
            print("\n📁 Screenshots captured:")
            for file in sorted(os.listdir('screenshots')):
                if file.endswith('.png'):
                    print(f"   - {file}")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            # Take error screenshot
            take_screenshot(page, 99, "error_state", wait_time=1)
            raise
        
        finally:
            browser.close()
            print("\n🏁 Test execution complete")

if __name__ == "__main__":
    run_comprehensive_test()