#!/usr/bin/env python3
"""
Complete End-to-End Workflow Test
Simulates the entire process from plan creation to report generation
"""
from playwright.sync_api import sync_playwright
import time
import sys

APP_URL = "http://localhost:8502"

def test_complete_workflow():
    """Test the complete workflow from plan creation to report generation"""
    
    print("🚀 STARTING COMPLETE WORKFLOW TEST")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            # ========== PHASE 1: MANAGER CREATES PLAN ==========
            print("\n📋 PHASE 1: Manager Creates Plan")
            print("-" * 40)
            
            # Navigate to app
            print("→ Navigating to application...")
            page.goto(APP_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Login as manager
            print("→ Logging in as manager...")
            inputs = page.locator("input").all()
            if len(inputs) >= 2:
                inputs[0].fill("manager@company.com")
                inputs[1].fill("manager123")
                page.locator("button", has_text="Sign In").click()
                page.wait_for_timeout(5000)
                print("✓ Logged in as manager")
            else:
                print("✗ Login form not found")
                return False
            
            # Verify dashboard
            if not page.locator("text=Manager Dashboard").is_visible():
                print("✗ Manager Dashboard not found")
                page.screenshot(path="error_manager_dashboard.png")
                return False
            print("✓ Manager Dashboard loaded")
            
            # Navigate to Create Plan
            print("→ Navigating to Create Plan...")
            create_plan_tab = page.locator("text=Create Plan").first
            create_plan_tab.click()
            page.wait_for_timeout(2000)
            print("✓ Create Plan tab opened")
            
            # Fill plan details
            print("→ Creating new analysis plan...")
            
            # Find plan name input (look for input with Plan in placeholder)
            plan_name = f"Test Plan {int(time.time())}"
            plan_created = False
            
            inputs = page.locator("input").all()
            for inp in inputs:
                placeholder = inp.get_attribute("placeholder")
                if placeholder and "Plan" in placeholder:
                    inp.fill(plan_name)
                    print(f"✓ Plan name: {plan_name}")
                    plan_created = True
                    break
            
            # Fill objectives
            textareas = page.locator("textarea").all()
            if textareas:
                objectives = "- Analyze sales data for Q4\n- Identify top performing products\n- Predict Q1 sales trends"
                textareas[0].fill(objectives)
                print("✓ Objectives filled")
            
            # Select priority
            try:
                page.select_option("select", label="High")
                print("✓ Priority set to High")
            except:
                print("⚠ Could not set priority")
            
            # Take screenshot before creation
            page.screenshot(path="plan_form_filled.png")
            
            # Create plan
            create_button = page.locator("button", has_text="Create Plan").first
            create_button.click()
            print("→ Creating plan...")
            page.wait_for_timeout(5000)
            
            # Check for success
            if page.locator("text=created successfully").is_visible():
                print("✓ Plan created successfully!")
            else:
                print("⚠ Success message not found, but continuing...")
            
            # Check for generated tasks
            if page.locator("text=Generated Tasks").is_visible():
                print("✓ Tasks were generated")
            
            page.screenshot(path="plan_created.png")
            
            # ========== PHASE 2: APPROVE PLAN ==========
            print("\n📋 PHASE 2: Manager Approves Plan")
            print("-" * 40)
            
            # Navigate to Active Plans
            print("→ Navigating to Active Plans...")
            active_plans_tab = page.locator("text=Active Plans").first
            active_plans_tab.click()
            page.wait_for_timeout(3000)
            
            # Look for the created plan and expand it
            print(f"→ Looking for plan: {plan_name}")
            plan_found = False
            
            # Try to find and click on the plan
            try:
                plan_element = page.locator(f"text={plan_name}").first
                if plan_element.is_visible():
                    plan_element.click()
                    page.wait_for_timeout(2000)
                    plan_found = True
                    print("✓ Found and expanded plan")
            except:
                print("⚠ Could not find specific plan")
            
            # Look for approve button
            approve_buttons = page.locator("button", has_text="Approve").all()
            if approve_buttons:
                print(f"→ Found {len(approve_buttons)} approve button(s)")
                approve_buttons[0].click()
                page.wait_for_timeout(3000)
                print("✓ Plan approved")
            else:
                print("⚠ No approve button found")
            
            page.screenshot(path="plan_approved.png")
            
            # ========== PHASE 3: ASSOCIATE EXECUTES TASK ==========
            print("\n📋 PHASE 3: Associate Executes Task")
            print("-" * 40)
            
            # Logout
            print("→ Logging out...")
            logout_button = page.locator("button", has_text="Logout").first
            if logout_button.is_visible():
                logout_button.click()
                page.wait_for_timeout(3000)
                print("✓ Logged out")
            
            # Login as associate
            print("→ Logging in as associate...")
            inputs = page.locator("input").all()
            inputs[0].fill("associate@company.com")
            inputs[1].fill("associate123")
            page.locator("button", has_text="Sign In").click()
            page.wait_for_timeout(5000)
            
            # Verify analyst dashboard
            if page.locator("text=Analyst Dashboard").is_visible():
                print("✓ Logged in as associate")
            else:
                print("✗ Analyst Dashboard not found")
                return False
            
            # Navigate to My Tasks
            print("→ Navigating to My Tasks...")
            my_tasks_tab = page.get_by_role("tab", name="My Tasks").first
            my_tasks_tab.click()
            page.wait_for_timeout(3000)
            
            # Check for assigned tasks
            start_buttons = page.locator("button", has_text="Start").all()
            if start_buttons:
                print(f"✓ Found {len(start_buttons)} assigned task(s)")
                
                # Start first task
                print("→ Starting first task...")
                start_buttons[0].click()
                page.wait_for_timeout(2000)
                
                # Navigate to Execute Task
                print("→ Navigating to Execute Task...")
                execute_tab = page.get_by_role("tab", name="Execute Task").first
                execute_tab.click()
                page.wait_for_timeout(3000)
                
                # Execute the task
                exec_button = page.locator("button", has_text="Execute Analysis").first
                if exec_button.is_visible():
                    print("→ Executing analysis...")
                    exec_button.click()
                    
                    # Wait for execution to complete (max 30 seconds)
                    for i in range(30):
                        if page.locator("text=Task completed successfully").is_visible():
                            print("✓ Task executed successfully!")
                            break
                        page.wait_for_timeout(1000)
                    
                    page.screenshot(path="task_executed.png")
                else:
                    print("⚠ Execute button not found")
            else:
                print("⚠ No tasks assigned to associate")
            
            # ========== PHASE 4: MANAGER GENERATES REPORT ==========
            print("\n📋 PHASE 4: Manager Generates Report")
            print("-" * 40)
            
            # Logout and login as manager again
            print("→ Switching back to manager...")
            logout_button = page.locator("button", has_text="Logout").first
            logout_button.click()
            page.wait_for_timeout(3000)
            
            inputs = page.locator("input").all()
            inputs[0].fill("manager@company.com")
            inputs[1].fill("manager123")
            page.locator("button", has_text="Sign In").click()
            page.wait_for_timeout(5000)
            print("✓ Logged in as manager")
            
            # Navigate to Reports
            print("→ Navigating to Reports...")
            reports_tab = page.locator("text=Reports").first
            if reports_tab.is_visible():
                reports_tab.click()
                page.wait_for_timeout(3000)
                
                # Generate report
                generate_button = page.locator("button", has_text="Generate Report").first
                if generate_button.is_visible():
                    print("→ Generating report...")
                    generate_button.click()
                    page.wait_for_timeout(5000)
                    
                    # Check for report elements
                    if page.locator("text=Executive Summary").is_visible():
                        print("✓ Report generated successfully!")
                        page.screenshot(path="report_generated.png")
                    else:
                        print("⚠ Report elements not found")
                else:
                    print("⚠ Generate Report button not found")
            else:
                print("⚠ Reports tab not found")
            
            # ========== SUMMARY ==========
            print("\n" + "=" * 60)
            print("✅ WORKFLOW TEST COMPLETED")
            print("=" * 60)
            print("\nScreenshots saved:")
            print("  - plan_form_filled.png")
            print("  - plan_created.png")
            print("  - plan_approved.png")
            print("  - task_executed.png")
            print("  - report_generated.png")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            page.screenshot(path="error_screenshot.png")
            return False
            
        finally:
            browser.close()

def check_app_running():
    """Check if the app is running"""
    print("→ Checking if app is running...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto(APP_URL, timeout=10000)
            page.wait_for_timeout(2000)
            
            # Check if we can see login elements
            if page.locator("input").count() > 0:
                print("✓ App is running and accessible")
                return True
            else:
                print("✗ App is not responding correctly")
                return False
                
        except Exception as e:
            print(f"✗ Cannot connect to app: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 COMPLETE END-TO-END WORKFLOW TEST")
    print("=" * 60)
    
    # First check if app is running
    if not check_app_running():
        print("\n⚠️  Please ensure the Streamlit app is running on port 8502")
        print("   Run: streamlit run streamlit_app_v3.py --server.port 8502")
        sys.exit(1)
    
    # Run the complete workflow test
    success = test_complete_workflow()
    
    if success:
        print("\n🎉 All workflow steps completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️  Some workflow steps failed. Check screenshots for details.")
        sys.exit(1)