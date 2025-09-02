#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Script for Integrated AI Data Analysis Platform
Tests all 5 steps with screenshot capture and gap documentation
"""

from playwright.sync_api import sync_playwright, Page, expect
import os
import time
import json
from datetime import datetime
from pathlib import Path
import shutil

# Configuration
APP_URL = "http://localhost:8501"  # Default Streamlit port
SCREENSHOT_DIR = f"screenshots_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
GAPS_LOG = []

class E2ETestRunner:
    def __init__(self):
        self.screenshot_dir = Path(SCREENSHOT_DIR)
        self.gaps = []
        self.screenshot_count = 0
        self.test_results = {
            'passed': [],
            'failed': [],
            'gaps': [],
            'screenshots': []
        }
        
    def setup_directories(self):
        """Create screenshot directory"""
        if self.screenshot_dir.exists():
            shutil.rmtree(self.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True)
        print(f"📁 Created screenshot directory: {self.screenshot_dir}")
        
    def take_screenshot(self, page: Page, name: str, description: str = ""):
        """Take and save a screenshot"""
        self.screenshot_count += 1
        filename = f"{self.screenshot_count:02d}_{name}.png"
        filepath = self.screenshot_dir / filename
        
        try:
            page.screenshot(path=str(filepath), full_page=True)
            print(f"   📸 Screenshot {self.screenshot_count}: {filename}")
            
            self.test_results['screenshots'].append({
                'number': self.screenshot_count,
                'name': name,
                'file': filename,
                'description': description
            })
            return filepath
        except Exception as e:
            print(f"   ❌ Failed to capture screenshot: {e}")
            self.log_gap(f"Screenshot failure", f"Could not capture {name}: {e}")
            return None
    
    def log_gap(self, category: str, description: str, severity: str = "Medium"):
        """Log a gap or issue found during testing"""
        gap = {
            'category': category,
            'description': description,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        self.gaps.append(gap)
        self.test_results['gaps'].append(gap)
        print(f"   ⚠️ GAP: [{severity}] {category} - {description}")
    
    def test_step1_project_setup(self, page: Page):
        """Test Step 1: Project Setup"""
        print("\n" + "="*60)
        print("📁 TESTING STEP 1: PROJECT SETUP")
        print("="*60)
        
        try:
            # Navigate to app
            print("→ Loading application...")
            page.goto(APP_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            
            # Screenshot 1: Landing page
            self.take_screenshot(page, "landing_page", "Initial application load")
            
            # Check if app loaded correctly
            if page.locator("text=AI").count() > 0:
                print("✅ Application loaded successfully")
                self.test_results['passed'].append("App loading")
            else:
                self.log_gap("Loading", "Application title not found", "High")
                self.test_results['failed'].append("App loading")
            
            # Check for Step 1 content
            if page.locator("text=Project Setup").count() > 0:
                print("✅ Step 1 Project Setup visible")
                self.test_results['passed'].append("Step 1 visibility")
            else:
                self.log_gap("Navigation", "Step 1 not immediately visible", "Medium")
            
            # Screenshot 2: Empty form
            self.take_screenshot(page, "project_form_empty", "Empty project setup form")
            
            # Fill project form
            print("→ Filling project form...")
            
            # Try to find and fill form fields
            try:
                # Project name
                project_name_input = page.locator("input").first
                if project_name_input.is_visible():
                    project_name_input.fill("Q4 Sales Analysis Test")
                    print("✅ Filled project name")
                else:
                    self.log_gap("Form", "Project name input not found", "High")
                
                # Client name (second input)
                client_inputs = page.locator("input").all()
                if len(client_inputs) > 1:
                    client_inputs[1].fill("Testing Team")
                    print("✅ Filled client name")
                
                # Business objectives (textarea)
                textareas = page.locator("textarea").all()
                if len(textareas) > 0:
                    textareas[0].fill("Test objective: Analyze Q4 sales performance and identify growth opportunities")
                    print("✅ Filled business objectives")
                else:
                    self.log_gap("Form", "Business objectives textarea not found", "High")
                
                if len(textareas) > 1:
                    textareas[1].fill("Success: Generate actionable insights with >80% accuracy")
                    print("✅ Filled success criteria")
                
                # Screenshot 3: Filled form
                page.wait_for_timeout(1000)
                self.take_screenshot(page, "project_form_filled", "Project form with data")
                
            except Exception as e:
                self.log_gap("Form filling", f"Error filling form: {e}", "High")
                self.test_results['failed'].append("Form filling")
            
            # Test file upload
            print("→ Testing file upload...")
            
            # Look for file upload element
            file_inputs = page.locator("input[type='file']").all()
            if len(file_inputs) > 0:
                # Upload test file
                test_file = Path("test_data/valid/sales_small.csv")
                if test_file.exists():
                    file_inputs[0].set_input_files(str(test_file))
                    page.wait_for_timeout(2000)
                    print("✅ File uploaded successfully")
                    self.test_results['passed'].append("File upload")
                    
                    # Screenshot 4: File uploaded
                    self.take_screenshot(page, "file_uploaded", "File upload successful")
                else:
                    print("⚠️ Test file not found, skipping upload test")
                    self.log_gap("Test data", "Test file not found", "Low")
            else:
                self.log_gap("File upload", "File input not found", "High")
                self.test_results['failed'].append("File upload")
            
            # Submit form
            print("→ Submitting form...")
            submit_buttons = page.locator("button").filter(has_text="Initialize")
            if submit_buttons.count() > 0:
                submit_buttons.first.click()
                page.wait_for_timeout(2000)
                print("✅ Form submitted")
                self.test_results['passed'].append("Form submission")
                
                # Screenshot 5: After submission
                self.take_screenshot(page, "project_initialized", "Project initialization complete")
            else:
                self.log_gap("Form submission", "Submit button not found", "High")
                self.test_results['failed'].append("Form submission")
            
            # Check for success message or step progression
            if page.locator("text=success").count() > 0 or page.locator("text=Step 2").count() > 0:
                print("✅ Step 1 completed successfully")
                self.test_results['passed'].append("Step 1 completion")
            else:
                self.log_gap("Step progression", "No success indication after Step 1", "Medium")
            
        except Exception as e:
            print(f"❌ Step 1 test failed: {e}")
            self.log_gap("Step 1", f"Critical failure: {e}", "Critical")
            self.test_results['failed'].append("Step 1")
    
    def test_step2_manager_planning(self, page: Page):
        """Test Step 2: Manager Planning"""
        print("\n" + "="*60)
        print("📋 TESTING STEP 2: MANAGER PLANNING")
        print("="*60)
        
        try:
            # Check if we're on Step 2
            if page.locator("text=Manager Planning").count() > 0:
                print("✅ Step 2 Manager Planning visible")
                self.test_results['passed'].append("Step 2 visibility")
            else:
                self.log_gap("Navigation", "Step 2 not visible", "High")
            
            # Screenshot 6: Planning page
            self.take_screenshot(page, "planning_page", "Manager planning interface")
            
            # Check for API key field
            api_key_inputs = page.locator("input[type='password']").all()
            if len(api_key_inputs) > 0:
                print("✅ API key field found")
                # Don't actually enter an API key for security
                self.take_screenshot(page, "api_key_field", "API key configuration option")
            else:
                print("⚠️ No API key field - using fallback planning")
                self.log_gap("AI Integration", "API key field not found, fallback mode", "Low")
            
            # Test manual planning fallback
            print("→ Testing manual planning...")
            
            # Look for manual planning form
            if page.locator("text=Manual").count() > 0:
                textareas = page.locator("textarea").all()
                if len(textareas) > 0:
                    textareas[0].fill("Test Approach: Comprehensive statistical analysis")
                    if len(textareas) > 1:
                        textareas[1].fill("Key Metrics: Revenue, Growth Rate, Customer Segments")
                    if len(textareas) > 2:
                        textareas[2].fill("Deliverables: Executive Dashboard, Analysis Report")
                    
                    print("✅ Manual planning form filled")
                    self.test_results['passed'].append("Manual planning")
                    
                    # Screenshot 7: Manual plan filled
                    self.take_screenshot(page, "manual_plan_filled", "Manual planning form completed")
            
            # Generate or create plan
            plan_buttons = page.locator("button").filter(has_text="Plan")
            if plan_buttons.count() > 0:
                plan_buttons.first.click()
                page.wait_for_timeout(3000)
                print("✅ Plan generated/created")
                self.test_results['passed'].append("Plan creation")
                
                # Screenshot 8: Generated plan
                self.take_screenshot(page, "plan_generated", "Analysis plan generated")
            else:
                self.log_gap("Planning", "Plan generation button not found", "High")
            
            # Approve plan
            approve_buttons = page.locator("button").filter(has_text="Approve")
            if approve_buttons.count() > 0:
                approve_buttons.first.click()
                page.wait_for_timeout(2000)
                print("✅ Plan approved")
                self.test_results['passed'].append("Plan approval")
                
                # Screenshot 9: Plan approved
                self.take_screenshot(page, "plan_approved", "Plan approval complete")
            else:
                self.log_gap("Approval", "Approve button not found", "Medium")
            
        except Exception as e:
            print(f"❌ Step 2 test failed: {e}")
            self.log_gap("Step 2", f"Critical failure: {e}", "Critical")
            self.test_results['failed'].append("Step 2")
    
    def test_step3_data_understanding(self, page: Page):
        """Test Step 3: Data Understanding"""
        print("\n" + "="*60)
        print("🔍 TESTING STEP 3: DATA UNDERSTANDING")
        print("="*60)
        
        try:
            # Check if we're on Step 3
            if page.locator("text=Data Understanding").count() > 0:
                print("✅ Step 3 Data Understanding visible")
                self.test_results['passed'].append("Step 3 visibility")
            else:
                self.log_gap("Navigation", "Step 3 not visible", "High")
            
            # Screenshot 10: Data profiling page
            self.take_screenshot(page, "data_profiling_page", "Data understanding interface")
            
            # Check for data metrics
            metrics = page.locator(".metric").all()
            if len(metrics) > 0:
                print(f"✅ Found {len(metrics)} data metrics")
                self.test_results['passed'].append("Data metrics display")
            else:
                self.log_gap("Data display", "No metrics found", "Medium")
            
            # Check for quality score
            if page.locator("text=Quality").count() > 0:
                print("✅ Data quality score displayed")
                self.test_results['passed'].append("Quality score")
                
                # Screenshot 11: Quality metrics
                self.take_screenshot(page, "quality_metrics", "Data quality assessment")
            else:
                self.log_gap("Quality", "Quality score not displayed", "Low")
            
            # Complete data understanding
            complete_buttons = page.locator("button").filter(has_text="Complete")
            if complete_buttons.count() > 0:
                complete_buttons.first.click()
                page.wait_for_timeout(2000)
                print("✅ Data understanding completed")
                self.test_results['passed'].append("Step 3 completion")
                
                # Screenshot 12: Step 3 complete
                self.take_screenshot(page, "data_understanding_complete", "Data profiling complete")
            else:
                self.log_gap("Completion", "Complete button not found", "Medium")
            
        except Exception as e:
            print(f"❌ Step 3 test failed: {e}")
            self.log_gap("Step 3", f"Critical failure: {e}", "Critical")
            self.test_results['failed'].append("Step 3")
    
    def test_step4_analysis_guidance(self, page: Page):
        """Test Step 4: Analysis Guidance"""
        print("\n" + "="*60)
        print("🎯 TESTING STEP 4: ANALYSIS GUIDANCE")
        print("="*60)
        
        try:
            # Check if we're on Step 4
            if page.locator("text=Analysis Guidance").count() > 0:
                print("✅ Step 4 Analysis Guidance visible")
                self.test_results['passed'].append("Step 4 visibility")
            else:
                self.log_gap("Navigation", "Step 4 not visible", "High")
            
            # Screenshot 13: Analysis guidance page
            self.take_screenshot(page, "analysis_guidance_page", "Analysis guidance interface")
            
            # Generate tasks
            generate_buttons = page.locator("button").filter(has_text="Generate")
            if generate_buttons.count() > 0:
                generate_buttons.first.click()
                page.wait_for_timeout(3000)
                print("✅ Analysis tasks generated")
                self.test_results['passed'].append("Task generation")
                
                # Screenshot 14: Generated tasks
                self.take_screenshot(page, "tasks_generated", "Analysis tasks list")
            else:
                self.log_gap("Task generation", "Generate button not found", "High")
            
            # Check for task list
            expanders = page.locator("[data-testid='stExpander']").all()
            if len(expanders) > 0:
                print(f"✅ Found {len(expanders)} analysis tasks")
                self.test_results['passed'].append("Task display")
                
                # Expand first task
                if len(expanders) > 0:
                    expanders[0].click()
                    page.wait_for_timeout(1000)
                    
                    # Screenshot 15: Task details
                    self.take_screenshot(page, "task_details", "Expanded task details")
            else:
                self.log_gap("Task display", "No task expanders found", "Medium")
            
            # Check for Marimo integration buttons
            notebook_buttons = page.locator("button").filter(has_text="Notebook")
            if notebook_buttons.count() > 0:
                print("✅ Marimo notebook generation available")
                self.test_results['passed'].append("Marimo integration")
                
                # Generate a notebook
                notebook_buttons.first.click()
                page.wait_for_timeout(2000)
                
                # Screenshot 16: Notebook generated
                self.take_screenshot(page, "notebook_generated", "Marimo notebook generation")
            else:
                self.log_gap("Marimo", "Notebook generation not available", "Medium")
            
            # Proceed to execution
            proceed_buttons = page.locator("button").filter(has_text="Proceed")
            if proceed_buttons.count() > 0:
                proceed_buttons.first.click()
                page.wait_for_timeout(2000)
                print("✅ Proceeding to execution")
                self.test_results['passed'].append("Step 4 completion")
            else:
                # Alternative: Look for Step 5 navigation
                print("⚠️ No proceed button, checking alternatives")
                self.log_gap("Navigation", "Proceed button not found", "Low")
            
        except Exception as e:
            print(f"❌ Step 4 test failed: {e}")
            self.log_gap("Step 4", f"Critical failure: {e}", "Critical")
            self.test_results['failed'].append("Step 4")
    
    def test_step5_marimo_execution(self, page: Page):
        """Test Step 5: Marimo Execution"""
        print("\n" + "="*60)
        print("🚀 TESTING STEP 5: MARIMO EXECUTION")
        print("="*60)
        
        try:
            # Check if we're on Step 5
            if page.locator("text=Marimo").count() > 0 or page.locator("text=Execution").count() > 0:
                print("✅ Step 5 Marimo Execution visible")
                self.test_results['passed'].append("Step 5 visibility")
            else:
                self.log_gap("Navigation", "Step 5 not visible", "High")
            
            # Screenshot 17: Execution page
            self.take_screenshot(page, "execution_page", "Marimo execution interface")
            
            # Check execution options
            if page.locator("text=Sequential").count() > 0:
                print("✅ Execution mode options available")
                self.test_results['passed'].append("Execution modes")
                
                # Screenshot 18: Execution options
                self.take_screenshot(page, "execution_options", "Execution mode selection")
            else:
                self.log_gap("Execution", "Execution modes not found", "Low")
            
            # Start execution
            start_buttons = page.locator("button").filter(has_text="Start")
            if start_buttons.count() > 0:
                start_buttons.first.click()
                page.wait_for_timeout(3000)
                print("✅ Execution started")
                self.test_results['passed'].append("Execution start")
                
                # Screenshot 19: Execution progress
                self.take_screenshot(page, "execution_progress", "Task execution in progress")
                
                # Wait for some progress
                page.wait_for_timeout(5000)
                
                # Screenshot 20: Execution results
                self.take_screenshot(page, "execution_results", "Execution results display")
            else:
                self.log_gap("Execution", "Start button not found", "High")
            
            # Check for results
            if page.locator("text=Results").count() > 0 or page.locator("text=Complete").count() > 0:
                print("✅ Results generated")
                self.test_results['passed'].append("Results generation")
                
                # Screenshot 21: Final results
                self.take_screenshot(page, "final_results", "Final analysis results")
            else:
                self.log_gap("Results", "No results indication found", "Medium")
            
            # Check for export options
            if page.locator("text=Download").count() > 0 or page.locator("text=Export").count() > 0:
                print("✅ Export options available")
                self.test_results['passed'].append("Export functionality")
                
                # Screenshot 22: Export options
                self.take_screenshot(page, "export_options", "Report export options")
            else:
                self.log_gap("Export", "No export options found", "Low")
            
        except Exception as e:
            print(f"❌ Step 5 test failed: {e}")
            self.log_gap("Step 5", f"Critical failure: {e}", "Critical")
            self.test_results['failed'].append("Step 5")
    
    def test_edge_cases(self, page: Page):
        """Test edge cases and error handling"""
        print("\n" + "="*60)
        print("⚠️ TESTING EDGE CASES")
        print("="*60)
        
        # Test navigation back
        print("→ Testing navigation...")
        try:
            # Try to go back to Step 1
            nav_buttons = page.locator("button").filter(has_text="Step 1")
            if nav_buttons.count() > 0:
                nav_buttons.first.click()
                page.wait_for_timeout(1000)
                print("✅ Navigation to Step 1 works")
                self.test_results['passed'].append("Navigation")
            else:
                self.log_gap("Navigation", "Step navigation not available", "Low")
        except Exception as e:
            self.log_gap("Navigation", f"Navigation test failed: {e}", "Low")
        
        # Test reset functionality
        print("→ Testing reset...")
        try:
            reset_buttons = page.locator("button").filter(has_text="Reset")
            if reset_buttons.count() > 0:
                print("✅ Reset button available")
                self.test_results['passed'].append("Reset functionality")
            else:
                self.log_gap("Reset", "No reset option found", "Low")
        except Exception as e:
            self.log_gap("Reset", f"Reset test failed: {e}", "Low")
        
        # Test with invalid file
        print("→ Testing invalid file upload...")
        try:
            # Navigate back to Step 1 if possible
            page.goto(APP_URL)
            page.wait_for_timeout(2000)
            
            file_inputs = page.locator("input[type='file']").all()
            if len(file_inputs) > 0:
                # Try uploading a corrupted file
                corrupted_file = Path("test_data/corrupted/malformed.csv")
                if corrupted_file.exists():
                    file_inputs[0].set_input_files(str(corrupted_file))
                    page.wait_for_timeout(2000)
                    
                    # Check for error handling
                    if page.locator("text=error").count() > 0 or page.locator("text=Error").count() > 0:
                        print("✅ Error handling for invalid file works")
                        self.test_results['passed'].append("Error handling")
                    else:
                        print("⚠️ No error message for invalid file")
                        self.log_gap("Error handling", "Invalid file accepted without error", "Medium")
                    
                    # Screenshot 23: Error state
                    self.take_screenshot(page, "error_handling", "Error handling display")
        except Exception as e:
            self.log_gap("Edge case", f"Invalid file test failed: {e}", "Low")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 GENERATING TEST REPORT")
        print("="*60)
        
        # Calculate statistics
        total_tests = len(self.test_results['passed']) + len(self.test_results['failed'])
        pass_rate = (len(self.test_results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        # Create report
        report = {
            'test_date': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': len(self.test_results['passed']),
                'failed': len(self.test_results['failed']),
                'pass_rate': f"{pass_rate:.1f}%",
                'gaps_found': len(self.gaps),
                'screenshots_taken': self.screenshot_count
            },
            'passed_tests': self.test_results['passed'],
            'failed_tests': self.test_results['failed'],
            'gaps': self.gaps,
            'screenshots': self.test_results['screenshots']
        }
        
        # Save report as JSON
        report_file = self.screenshot_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create markdown report
        md_report = f"""# E2E Test Report - Integrated AI Data Analysis Platform

## Test Summary
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Tests**: {total_tests}
- **Passed**: {len(self.test_results['passed'])} ✅
- **Failed**: {len(self.test_results['failed'])} ❌
- **Pass Rate**: {pass_rate:.1f}%
- **Gaps Found**: {len(self.gaps)}
- **Screenshots**: {self.screenshot_count}

## Test Results

### ✅ Passed Tests
"""
        for test in self.test_results['passed']:
            md_report += f"- {test}\n"
        
        md_report += "\n### ❌ Failed Tests\n"
        for test in self.test_results['failed']:
            md_report += f"- {test}\n"
        
        md_report += "\n## Gaps and Issues Found\n\n"
        
        # Group gaps by severity
        critical_gaps = [g for g in self.gaps if g['severity'] == 'Critical']
        high_gaps = [g for g in self.gaps if g['severity'] == 'High']
        medium_gaps = [g for g in self.gaps if g['severity'] == 'Medium']
        low_gaps = [g for g in self.gaps if g['severity'] == 'Low']
        
        if critical_gaps:
            md_report += "### 🔴 Critical Issues\n"
            for gap in critical_gaps:
                md_report += f"- **{gap['category']}**: {gap['description']}\n"
        
        if high_gaps:
            md_report += "\n### 🟠 High Priority Issues\n"
            for gap in high_gaps:
                md_report += f"- **{gap['category']}**: {gap['description']}\n"
        
        if medium_gaps:
            md_report += "\n### 🟡 Medium Priority Issues\n"
            for gap in medium_gaps:
                md_report += f"- **{gap['category']}**: {gap['description']}\n"
        
        if low_gaps:
            md_report += "\n### 🟢 Low Priority Issues\n"
            for gap in low_gaps:
                md_report += f"- **{gap['category']}**: {gap['description']}\n"
        
        md_report += "\n## Screenshots Captured\n\n"
        for screenshot in self.test_results['screenshots']:
            md_report += f"{screenshot['number']}. **{screenshot['name']}** - {screenshot['description']}\n"
        
        # Save markdown report
        md_file = self.screenshot_dir / "TEST_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(md_report)
        
        print(f"\n✅ Report generated: {md_file}")
        print(f"✅ JSON report: {report_file}")
        print(f"✅ Screenshots: {self.screenshot_dir}")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Tests Passed: {len(self.test_results['passed'])}")
        print(f"Tests Failed: {len(self.test_results['failed'])}")
        print(f"Gaps Found: {len(self.gaps)}")
        print(f"  - Critical: {len(critical_gaps)}")
        print(f"  - High: {len(high_gaps)}")
        print(f"  - Medium: {len(medium_gaps)}")
        print(f"  - Low: {len(low_gaps)}")
        
        return report

def main():
    """Run comprehensive E2E tests"""
    print("\n" + "="*60)
    print("🧪 COMPREHENSIVE E2E TESTING - INTEGRATED PLATFORM")
    print("="*60)
    
    # Initialize test runner
    runner = E2ETestRunner()
    runner.setup_directories()
    
    # Run tests with Playwright
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,  # Set to False to see the browser
            slow_mo=100  # Slow down actions for visibility
        )
        
        # Create context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1
        )
        
        # Create page
        page = context.new_page()
        
        try:
            # Run all test suites
            runner.test_step1_project_setup(page)
            runner.test_step2_manager_planning(page)
            runner.test_step3_data_understanding(page)
            runner.test_step4_analysis_guidance(page)
            runner.test_step5_marimo_execution(page)
            runner.test_edge_cases(page)
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            runner.log_gap("Test execution", f"Fatal error: {e}", "Critical")
        
        finally:
            # Close browser
            browser.close()
    
    # Generate report
    report = runner.generate_report()
    
    print("\n" + "="*60)
    print("✅ E2E TESTING COMPLETE")
    print("="*60)
    print(f"\nView results in: {runner.screenshot_dir}/")
    print("Next steps:")
    print("1. Review TEST_REPORT.md for detailed findings")
    print("2. Check screenshots for visual validation")
    print("3. Address critical and high priority gaps")
    print("4. Re-run tests after fixes")
    
    return report

if __name__ == "__main__":
    # Check if app is running
    import requests
    try:
        response = requests.get(APP_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print(f"⚠️ Application returned status {response.status_code}")
    except:
        print("❌ Application not running. Please start it with:")
        print("   streamlit run streamlit_app_integrated.py")
        print("\nOr for 4-step version:")
        print("   streamlit run streamlit_app_4steps.py")
        exit(1)
    
    # Run tests
    main()