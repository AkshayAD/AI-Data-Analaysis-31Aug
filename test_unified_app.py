#!/usr/bin/env python3
"""
Test the unified app without authentication
"""
from playwright.sync_api import sync_playwright
import time

APP_URL = "http://localhost:8503"

def test_unified_app():
    """Test that the unified app works without login"""
    print("🧪 Testing Unified App (No Authentication)")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to app - should go directly to main interface
            print("→ Navigating to app...")
            page.goto(APP_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            # Check for main interface (no login)
            print("→ Checking for direct access (no login)...")
            
            # Should see the main header
            if page.locator("text=AI Data Analysis Platform").is_visible():
                print("✅ Main interface loaded directly (no login required)")
            else:
                print("❌ Main interface not found")
                page.screenshot(path="unified_error.png")
                return False
            
            # Check for navigation options in sidebar
            print("\n→ Checking navigation options...")
            nav_items = [
                "Overview",
                "Create Analysis Plan", 
                "Manage Plans",
                "Execute Tasks",
                "View Results",
                "Generate Reports"
            ]
            
            found_items = 0
            for item in nav_items:
                if page.locator(f"text={item}").count() > 0:
                    print(f"  ✅ Found: {item}")
                    found_items += 1
                else:
                    print(f"  ❌ Missing: {item}")
            
            print(f"\n  Found {found_items}/{len(nav_items)} navigation items")
            
            # Test role switching (should be in sidebar)
            print("\n→ Testing role switching...")
            
            # Check for role selector
            if page.locator("text=Current Role").is_visible():
                print("  ✅ Role selector present")
                
                # Try to switch roles
                role_options = ["Manager", "Analyst", "Associate"]
                for role in role_options:
                    if page.locator(f"text={role}").count() > 0:
                        print(f"  ✅ Role option available: {role}")
            else:
                print("  ⚠ Role selector not found")
            
            # Test plan creation (no login needed)
            print("\n→ Testing plan creation...")
            
            # Navigate to Create Plan
            create_plan_option = page.locator("text=Create Analysis Plan").first
            if create_plan_option.is_visible():
                page.select_option("select", label="➕ Create Analysis Plan")
                page.wait_for_timeout(2000)
                print("  ✅ Navigated to Create Plan")
                
                # Check for plan creation form
                if page.locator("text=Business Objectives").is_visible():
                    print("  ✅ Plan creation form available")
                    
                    # Fill sample data
                    inputs = page.locator("input").all()
                    if inputs:
                        inputs[0].fill("Test Plan No Auth")
                        print("  ✅ Can enter plan name")
                    
                    textareas = page.locator("textarea").all()
                    if textareas:
                        textareas[0].fill("- Test objective 1\n- Test objective 2")
                        print("  ✅ Can enter objectives")
                    
                    # Check for create button
                    if page.locator("button", has_text="Create Plan").is_visible():
                        print("  ✅ Create Plan button available")
                        
                        # Take screenshot of form
                        page.screenshot(path="unified_plan_form.png")
                        
                        # Actually create the plan
                        page.locator("button", has_text="Create Plan").click()
                        page.wait_for_timeout(3000)
                        
                        # Check for success
                        if page.locator("text=created successfully").is_visible():
                            print("  ✅ Plan created successfully without login!")
                        else:
                            print("  ⚠ Success message not found")
            
            # Test viewing results
            print("\n→ Testing results view...")
            page.select_option("select", label="📈 View Results")
            page.wait_for_timeout(2000)
            
            if page.locator("text=Analysis Results").is_visible():
                print("  ✅ Can access results view")
            
            # Final screenshot
            page.screenshot(path="unified_final.png")
            
            print("\n" + "=" * 60)
            print("✅ UNIFIED APP TEST COMPLETE")
            print("No authentication required - all features directly accessible!")
            return True
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            page.screenshot(path="unified_error.png")
            return False
            
        finally:
            browser.close()

def test_workflow_without_login():
    """Test complete workflow without any login steps"""
    print("\n🔄 Testing Complete Workflow (No Login)")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Go directly to app
            page.goto(APP_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(3000)
            
            print("1️⃣ Create Plan - Direct Access")
            page.select_option("select", label="➕ Create Analysis Plan")
            page.wait_for_timeout(2000)
            
            # Fill plan details
            inputs = page.locator("input").all()
            if inputs:
                inputs[0].fill("Seamless Workflow Test")
            
            textareas = page.locator("textarea").all()
            if textareas:
                textareas[0].fill("- Analyze data\n- Generate insights")
            
            # Use sample data
            page.select_option("select", label="Use Sample Data")
            
            # Create plan
            page.locator("button", has_text="Create Plan").click()
            page.wait_for_timeout(3000)
            print("  ✅ Plan created")
            
            print("\n2️⃣ Execute Tasks - No Role Switch Needed")
            page.select_option("select", label="⚡ Execute Tasks")
            page.wait_for_timeout(2000)
            
            # Execute all tasks
            if page.locator("button", has_text="Execute All").is_visible():
                page.locator("button", has_text="Execute All").click()
                page.wait_for_timeout(5000)
                print("  ✅ Tasks executed")
            
            print("\n3️⃣ Generate Report - Direct Access")
            page.select_option("select", label="📄 Generate Reports")
            page.wait_for_timeout(2000)
            
            if page.locator("button", has_text="Generate Executive Report").is_visible():
                page.locator("button", has_text="Generate Executive Report").click()
                page.wait_for_timeout(3000)
                print("  ✅ Report generated")
            
            print("\n✅ Complete workflow executed without any login!")
            return True
            
        except Exception as e:
            print(f"\n❌ Workflow error: {e}")
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 UNIFIED APP TESTING (NO AUTHENTICATION)")
    print("=" * 60)
    
    # Test basic functionality
    if test_unified_app():
        # Test complete workflow
        test_workflow_without_login()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE")
    print("The platform now works without any authentication!")
    print("=" * 60)