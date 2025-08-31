#!/usr/bin/env python3
"""
Simple step-by-step test of the application
"""
from playwright.sync_api import sync_playwright
import time

def test_login_page():
    """Test that the login page loads correctly"""
    print("🔍 Testing Login Page...")
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to app
            print("  → Navigating to http://localhost:8501")
            page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
            
            # Wait for page to fully load
            page.wait_for_timeout(3000)
            
            # Check for login elements
            print("  → Checking for login form...")
            
            # Look for Sign In text
            sign_in = page.locator("text=Sign In").first
            if sign_in.is_visible():
                print("  ✓ Found 'Sign In' text")
            else:
                print("  ✗ 'Sign In' text not found")
                
            # Check for email input
            email_input = page.locator("input").first
            if email_input.is_visible():
                print("  ✓ Found email input field")
            else:
                print("  ✗ Email input not found")
            
            # Take screenshot for debugging
            page.screenshot(path="login_page.png")
            print("  ✓ Screenshot saved as login_page.png")
            
            print("✅ Login page test completed!")
            
        except Exception as e:
            print(f"❌ Error testing login page: {e}")
            page.screenshot(path="error_screenshot.png")
            print("  → Error screenshot saved as error_screenshot.png")
            
        finally:
            browser.close()

def test_manager_login():
    """Test manager login process"""
    print("\n🔍 Testing Manager Login...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to app
            print("  → Navigating to app...")
            page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Find and fill login form
            print("  → Filling login form...")
            
            # Find input fields - Streamlit uses specific structure
            inputs = page.locator("input").all()
            if len(inputs) >= 2:
                # First input is email
                inputs[0].fill("manager@company.com")
                print("  ✓ Filled email")
                
                # Second input is password
                inputs[1].fill("manager123")
                print("  ✓ Filled password")
            else:
                print(f"  ✗ Expected 2 inputs, found {len(inputs)}")
            
            # Click Sign In button
            print("  → Clicking Sign In button...")
            sign_in_button = page.locator("button", has_text="Sign In").first
            sign_in_button.click()
            
            # Wait for navigation
            page.wait_for_timeout(5000)
            
            # Check if we're logged in
            print("  → Checking for dashboard...")
            
            # Look for manager dashboard elements
            if page.locator("text=Manager Dashboard").is_visible():
                print("  ✓ Successfully logged in as Manager!")
                page.screenshot(path="manager_dashboard.png")
                print("  ✓ Dashboard screenshot saved")
            else:
                print("  ✗ Manager Dashboard not found")
                page.screenshot(path="login_failed.png")
                
        except Exception as e:
            print(f"❌ Error during manager login: {e}")
            page.screenshot(path="manager_login_error.png")
            
        finally:
            browser.close()

def test_create_plan():
    """Test creating a plan as manager"""
    print("\n🔍 Testing Plan Creation...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Login first
            print("  → Logging in as manager...")
            page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            inputs = page.locator("input").all()
            inputs[0].fill("manager@company.com")
            inputs[1].fill("manager123")
            page.locator("button", has_text="Sign In").click()
            page.wait_for_timeout(5000)
            
            # Navigate to Create Plan tab
            print("  → Navigating to Create Plan...")
            create_plan_tab = page.locator("text=Create Plan").first
            if create_plan_tab.is_visible():
                create_plan_tab.click()
                page.wait_for_timeout(2000)
                print("  ✓ Clicked Create Plan tab")
            
            # Fill plan details
            print("  → Filling plan details...")
            
            # Find plan name input
            plan_inputs = page.locator("input").all()
            if plan_inputs:
                # Usually the first input after navigation
                for inp in plan_inputs:
                    placeholder = inp.get_attribute("placeholder")
                    if placeholder and "Plan" in placeholder:
                        inp.fill("Test Analysis Plan")
                        print("  ✓ Filled plan name")
                        break
            
            # Find objectives textarea
            textareas = page.locator("textarea").all()
            if textareas:
                textareas[0].fill("- Analyze test data\n- Generate insights\n- Create report")
                print("  ✓ Filled objectives")
            
            # Take screenshot
            page.screenshot(path="create_plan_form.png")
            print("  ✓ Form screenshot saved")
            
            # Try to create plan
            create_button = page.locator("button", has_text="Create Plan").first
            if create_button.is_visible():
                print("  → Clicking Create Plan button...")
                create_button.click()
                page.wait_for_timeout(3000)
                
                # Check for success message
                if page.locator("text=created successfully").is_visible():
                    print("  ✓ Plan created successfully!")
                else:
                    print("  ⚠ Success message not found")
                    
        except Exception as e:
            print(f"❌ Error creating plan: {e}")
            page.screenshot(path="create_plan_error.png")
            
        finally:
            browser.close()

def test_associate_login():
    """Test associate login and task view"""
    print("\n🔍 Testing Associate Login...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate and login as associate
            print("  → Logging in as associate...")
            page.goto("http://localhost:8502", wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            inputs = page.locator("input").all()
            inputs[0].fill("associate@company.com")
            inputs[1].fill("associate123")
            page.locator("button", has_text="Sign In").click()
            page.wait_for_timeout(5000)
            
            # Check for analyst dashboard
            print("  → Checking for dashboard...")
            if page.locator("text=Analyst Dashboard").is_visible():
                print("  ✓ Successfully logged in as Associate!")
                
                # Check for My Tasks tab
                if page.locator("text=My Tasks").is_visible():
                    print("  ✓ Found My Tasks tab")
                    page.locator("text=My Tasks").click()
                    page.wait_for_timeout(2000)
                    
                    page.screenshot(path="associate_tasks.png")
                    print("  ✓ Tasks view screenshot saved")
                    
        except Exception as e:
            print(f"❌ Error during associate login: {e}")
            page.screenshot(path="associate_error.png")
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 STEP-BY-STEP APPLICATION TEST")
    print("=" * 60)
    
    # Run tests in sequence
    test_login_page()
    test_manager_login()
    test_create_plan()
    test_associate_login()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)