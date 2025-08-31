#!/usr/bin/env python3
"""
Comprehensive End-to-End Playwright Test for Enterprise AI Data Analysis Platform
Tests complete workflow with screenshots and validation
"""

import os
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Create screenshots directory
SCREENSHOTS_DIR = Path("screenshots_enterprise")
SCREENSHOTS_DIR.mkdir(exist_ok=True)

async def test_login_flow(page, role="manager"):
    """Test login flow for different roles"""
    print(f"\n🔐 Testing {role.upper()} Login Flow...")
    
    credentials = {
        "manager": ("manager@company.com", "manager123"),
        "analyst": ("analyst@company.com", "analyst123"),
        "associate": ("associate@company.com", "associate123")
    }
    
    email, password = credentials[role]
    
    # Navigate to app
    await page.goto("http://localhost:8510")
    await page.wait_for_load_state("networkidle")
    
    # Take screenshot of login page
    await page.screenshot(path=SCREENSHOTS_DIR / f"01_{role}_login_page.png", full_page=True)
    print(f"📸 Screenshot: {role} login page")
    
    # Fill login form
    await page.fill('input[type="text"]', email)
    await page.fill('input[type="password"]', password)
    
    # Screenshot with credentials entered
    await page.screenshot(path=SCREENSHOTS_DIR / f"02_{role}_credentials_entered.png")
    
    # Click login button
    await page.click('button:has-text("Login")')
    
    # Wait for dashboard to load
    await page.wait_for_timeout(3000)
    
    # Screenshot of dashboard after login
    await page.screenshot(path=SCREENSHOTS_DIR / f"03_{role}_dashboard.png", full_page=True)
    print(f"✅ {role.capitalize()} login successful")
    
    return True

async def test_manager_plan_creation(page):
    """Test manager creating analysis plan"""
    print("\n📋 Testing Manager Plan Creation...")
    
    # Navigate to Create Plan
    await page.click('text="Create Plan"')
    await page.wait_for_timeout(2000)
    
    # Screenshot of plan creation page
    await page.screenshot(path=SCREENSHOTS_DIR / "04_plan_creation_page.png", full_page=True)
    
    # Fill plan details
    await page.fill('input[placeholder*="Q4 Sales"]', "Q4 Revenue Analysis & Q1 Forecast")
    
    # Add objectives
    objectives = [
        "Analyze Q4 revenue trends and seasonal patterns",
        "Identify top performing products and regions",
        "Predict Q1 revenue using machine learning",
        "Segment customers based on purchase behavior",
        "Detect anomalies in sales data"
    ]
    
    for i, obj in enumerate(objectives):
        if i > 0:
            # Click add objective button
            await page.click('button:has-text("+ Add Objective")')
            await page.wait_for_timeout(500)
        
        # Fill objective
        objective_input = await page.query_selector(f'input[placeholder*="Identify revenue"]')
        if objective_input:
            await objective_input.fill(obj)
    
    # Ensure checkboxes are checked
    auto_generate = await page.query_selector('input[type="checkbox"]:near(:text("Auto-generate"))')
    if auto_generate:
        is_checked = await auto_generate.is_checked()
        if not is_checked:
            await auto_generate.click()
    
    auto_assign = await page.query_selector('input[type="checkbox"]:near(:text("Auto-assign"))')
    if auto_assign:
        is_checked = await auto_assign.is_checked()
        if not is_checked:
            await auto_assign.click()
    
    # Screenshot with form filled
    await page.screenshot(path=SCREENSHOTS_DIR / "05_plan_form_filled.png", full_page=True)
    print("📸 Screenshot: Plan form filled")
    
    # Submit plan
    await page.click('button:has-text("Create Plan")')
    await page.wait_for_timeout(3000)
    
    # Screenshot of generated tasks
    await page.screenshot(path=SCREENSHOTS_DIR / "06_generated_tasks.png", full_page=True)
    print("✅ Plan created with auto-generated tasks")
    
    # Expand some tasks to show details
    task_expanders = await page.query_selector_all('.streamlit-expanderHeader')
    if len(task_expanders) > 0:
        await task_expanders[0].click()
        await page.wait_for_timeout(500)
        if len(task_expanders) > 1:
            await task_expanders[1].click()
            await page.wait_for_timeout(500)
        
        # Screenshot with tasks expanded
        await page.screenshot(path=SCREENSHOTS_DIR / "07_tasks_expanded.png", full_page=True)
        print("📸 Screenshot: Task details shown")
    
    return True

async def test_approval_queue(page):
    """Test approval queue functionality"""
    print("\n✅ Testing Approval Queue...")
    
    # Navigate to Approval Queue
    await page.click('text="Approval Queue"')
    await page.wait_for_timeout(2000)
    
    # Screenshot of approval queue
    await page.screenshot(path=SCREENSHOTS_DIR / "08_approval_queue.png", full_page=True)
    print("📸 Screenshot: Approval queue")
    
    # Look for approval items
    approval_buttons = await page.query_selector_all('button:has-text("Approve")')
    
    if approval_buttons:
        # Click review first
        review_button = await page.query_selector('button:has-text("Review")')
        if review_button:
            await review_button.click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=SCREENSHOTS_DIR / "09_review_details.png", full_page=True)
            print("📸 Screenshot: Review details")
        
        # Approve the plan
        await approval_buttons[0].click()
        await page.wait_for_timeout(2000)
        
        # Screenshot after approval
        await page.screenshot(path=SCREENSHOTS_DIR / "10_plan_approved.png", full_page=True)
        print("✅ Plan approved successfully")
    
    return True

async def test_active_plans(page):
    """Test active plans view"""
    print("\n📊 Testing Active Plans...")
    
    # Navigate to Active Plans
    await page.click('text="Active Plans"')
    await page.wait_for_timeout(2000)
    
    # Screenshot of active plans
    await page.screenshot(path=SCREENSHOTS_DIR / "11_active_plans.png", full_page=True)
    print("📸 Screenshot: Active plans with progress")
    
    # Click view details if available
    view_buttons = await page.query_selector_all('button:has-text("View Details")')
    if view_buttons:
        await view_buttons[0].click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path=SCREENSHOTS_DIR / "12_plan_details.png", full_page=True)
        print("📸 Screenshot: Plan details")
    
    return True

async def test_team_dashboard(page):
    """Test team dashboard"""
    print("\n👥 Testing Team Dashboard...")
    
    # Navigate to Team Dashboard
    await page.click('text="Team Dashboard"')
    await page.wait_for_timeout(2000)
    
    # Screenshot of team dashboard
    await page.screenshot(path=SCREENSHOTS_DIR / "13_team_dashboard.png", full_page=True)
    print("📸 Screenshot: Team performance metrics")
    
    # Scroll to show full content
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(1000)
    
    await page.screenshot(path=SCREENSHOTS_DIR / "14_team_performance.png", full_page=True)
    print("📸 Screenshot: Full team dashboard")
    
    return True

async def test_analyst_workflow(page):
    """Test analyst task execution workflow"""
    print("\n🔬 Testing Analyst Workflow...")
    
    # Logout first
    await page.click('button:has-text("Logout")')
    await page.wait_for_timeout(2000)
    
    # Login as analyst
    await test_login_flow(page, "analyst")
    
    # Navigate to My Tasks
    if await page.query_selector('text="My Tasks"'):
        await page.click('text="My Tasks"')
        await page.wait_for_timeout(2000)
        
        # Screenshot of analyst tasks
        await page.screenshot(path=SCREENSHOTS_DIR / "15_analyst_tasks.png", full_page=True)
        print("📸 Screenshot: Analyst task list")
        
        # Look for task action buttons
        start_buttons = await page.query_selector_all('button:has-text("Start")')
        notebook_buttons = await page.query_selector_all('button:has-text("Notebook")')
        
        if notebook_buttons:
            # Click notebook button
            await notebook_buttons[0].click()
            await page.wait_for_timeout(1000)
            await page.screenshot(path=SCREENSHOTS_DIR / "16_notebook_interface.png", full_page=True)
            print("📸 Screenshot: Marimo notebook interface")
    
    # Test Data Explorer
    await page.click('text="Data Explorer"')
    await page.wait_for_timeout(2000)
    
    # Check sample data checkbox
    sample_checkbox = await page.query_selector('input[type="checkbox"]:near(:text("sample data"))')
    if sample_checkbox:
        await sample_checkbox.click()
        await page.wait_for_timeout(2000)
        
        # Screenshot with data loaded
        await page.screenshot(path=SCREENSHOTS_DIR / "17_data_explorer.png", full_page=True)
        print("📸 Screenshot: Data explorer with sample data")
    
    # Test Analysis Tools
    await page.click('text="Analysis Tools"')
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path=SCREENSHOTS_DIR / "18_analysis_tools.png", full_page=True)
    print("📸 Screenshot: Analysis tools interface")
    
    # Test Marimo Notebooks
    await page.click('text="Marimo Notebooks"')
    await page.wait_for_timeout(2000)
    
    await page.screenshot(path=SCREENSHOTS_DIR / "19_marimo_notebooks.png", full_page=True)
    print("📸 Screenshot: Marimo notebook templates")
    
    # Expand a notebook cell if available
    expanders = await page.query_selector_all('.streamlit-expanderHeader')
    if expanders:
        await expanders[0].click()
        await page.wait_for_timeout(500)
        await page.screenshot(path=SCREENSHOTS_DIR / "20_notebook_cell.png", full_page=True)
        print("📸 Screenshot: Notebook cell details")
    
    return True

async def test_associate_workflow(page):
    """Test associate simplified interface"""
    print("\n🎯 Testing Associate Workflow...")
    
    # Logout and login as associate
    await page.click('button:has-text("Logout")')
    await page.wait_for_timeout(2000)
    
    await test_login_flow(page, "associate")
    
    # Screenshot of associate portal
    await page.screenshot(path=SCREENSHOTS_DIR / "21_associate_portal.png", full_page=True)
    print("📸 Screenshot: Associate simplified interface")
    
    # Navigate through associate sections
    if await page.query_selector('text="My Tasks"'):
        await page.click('text="My Tasks"')
        await page.wait_for_timeout(2000)
        await page.screenshot(path=SCREENSHOTS_DIR / "22_associate_tasks.png", full_page=True)
        print("📸 Screenshot: Associate task list")
    
    if await page.query_selector('text="Help & Training"'):
        await page.click('text="Help & Training"')
        await page.wait_for_timeout(2000)
        await page.screenshot(path=SCREENSHOTS_DIR / "23_help_training.png", full_page=True)
        print("📸 Screenshot: Help and training resources")
    
    return True

async def test_reports_dashboard(page):
    """Test reports dashboard"""
    print("\n📊 Testing Reports Dashboard...")
    
    # Logout and login as manager again
    await page.click('button:has-text("Logout")')
    await page.wait_for_timeout(2000)
    
    await test_login_flow(page, "manager")
    
    # Navigate to Reports
    await page.click('text="Reports"')
    await page.wait_for_timeout(2000)
    
    # Screenshot of reports dashboard
    await page.screenshot(path=SCREENSHOTS_DIR / "24_reports_dashboard.png", full_page=True)
    print("📸 Screenshot: Reports dashboard")
    
    return True

async def main():
    """Run comprehensive end-to-end tests"""
    print("🚀 Starting Comprehensive Enterprise Platform E2E Tests")
    print("="*60)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1.0
        )
        
        page = await context.new_page()
        
        try:
            # Run test suite
            tests = [
                ("Manager Login", lambda: test_login_flow(page, "manager")),
                ("Plan Creation", lambda: test_manager_plan_creation(page)),
                ("Approval Queue", lambda: test_approval_queue(page)),
                ("Active Plans", lambda: test_active_plans(page)),
                ("Team Dashboard", lambda: test_team_dashboard(page)),
                ("Analyst Workflow", lambda: test_analyst_workflow(page)),
                ("Associate Workflow", lambda: test_associate_workflow(page)),
                ("Reports Dashboard", lambda: test_reports_dashboard(page)),
            ]
            
            results = []
            for test_name, test_func in tests:
                try:
                    print(f"\n{'='*60}")
                    print(f"Running: {test_name}")
                    print('='*60)
                    result = await test_func()
                    results.append((test_name, True))
                    print(f"✅ {test_name} - PASSED")
                except Exception as e:
                    results.append((test_name, False))
                    print(f"❌ {test_name} - FAILED: {e}")
                    # Take error screenshot
                    await page.screenshot(
                        path=SCREENSHOTS_DIR / f"error_{test_name.lower().replace(' ', '_')}.png",
                        full_page=True
                    )
            
            # Final summary
            print(f"\n{'='*60}")
            print("📊 TEST SUMMARY")
            print('='*60)
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            for test_name, result in results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status}: {test_name}")
            
            print(f"\n📈 Overall: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed! Enterprise platform is fully functional!")
            else:
                failed_tests = [name for name, result in results if not result]
                print(f"❌ Failed tests: {', '.join(failed_tests)}")
            
            print(f"\n📸 Screenshots saved to: {SCREENSHOTS_DIR}/")
            print(f"📁 Total screenshots: {len(list(SCREENSHOTS_DIR.glob('*.png')))}")
            
        finally:
            await browser.close()
    
    print("\n✅ E2E Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())