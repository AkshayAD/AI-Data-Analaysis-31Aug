"""
End-to-End Tests for User Journeys using Playwright
"""
import pytest
from playwright.sync_api import Page, expect
import time
import os

# Test configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:8501")

class TestUserJourneys:
    """Test complete user journeys through the application"""
    
    def test_manager_login_and_dashboard(self, page: Page):
        """Test manager can login and access dashboard"""
        # Navigate to app
        page.goto(BASE_URL)
        
        # Wait for login form
        page.wait_for_selector("text=Sign In", timeout=10000)
        
        # Enter manager credentials
        page.fill('input[placeholder="user@company.com"]', "manager@company.com")
        page.fill('input[placeholder="Enter password"]', "manager123")
        
        # Submit login
        page.click('button:has-text("Sign In")')
        
        # Wait for dashboard to load
        page.wait_for_selector("text=Manager Dashboard", timeout=10000)
        
        # Verify manager elements are present
        expect(page.locator("text=Manager Dashboard")).to_be_visible()
        expect(page.locator("text=Create Plan")).to_be_visible()
        expect(page.locator("text=Active Plans")).to_be_visible()
        expect(page.locator("text=Team")).to_be_visible()
        
        # Verify role badge
        expect(page.locator("text=MANAGER")).to_be_visible()
    
    def test_associate_login_and_dashboard(self, page: Page):
        """Test associate can login and access dashboard"""
        # Navigate to app
        page.goto(BASE_URL)
        
        # Wait for login form
        page.wait_for_selector("text=Sign In", timeout=10000)
        
        # Enter associate credentials
        page.fill('input[placeholder="user@company.com"]', "associate@company.com")
        page.fill('input[placeholder="Enter password"]', "associate123")
        
        # Submit login
        page.click('button:has-text("Sign In")')
        
        # Wait for dashboard to load
        page.wait_for_selector("text=Analyst Dashboard", timeout=10000)
        
        # Verify associate elements are present
        expect(page.locator("text=My Tasks")).to_be_visible()
        expect(page.locator("text=Execute Task")).to_be_visible()
        expect(page.locator("text=Performance")).to_be_visible()
        
        # Verify role badge
        expect(page.locator("text=ASSOCIATE")).to_be_visible()
    
    def test_manager_create_plan_workflow(self, page: Page):
        """Test manager can create an analysis plan"""
        # Login as manager
        page.goto(BASE_URL)
        page.fill('input[placeholder="user@company.com"]', "manager@company.com")
        page.fill('input[placeholder="Enter password"]', "manager123")
        page.click('button:has-text("Sign In")')
        
        # Wait for dashboard
        page.wait_for_selector("text=Manager Dashboard", timeout=10000)
        
        # Navigate to Create Plan tab
        page.click("text=Create Plan")
        
        # Fill in plan details
        page.fill('input[placeholder="Q4 Sales Analysis"]', "Test Analysis Plan")
        page.fill('textarea[placeholder*="Identify revenue trends"]', 
                  "- Analyze sales data\n- Identify trends\n- Predict next quarter")
        
        # Select priority
        page.select_option('select:has-text("Priority")', "High")
        
        # Create plan
        page.click('button:has-text("Create Plan")')
        
        # Wait for success message
        page.wait_for_selector("text=Plan 'Test Analysis Plan' created successfully", timeout=10000)
        
        # Verify tasks were generated
        expect(page.locator("text=Generated Tasks")).to_be_visible()
    
    def test_complete_analysis_workflow(self, page: Page):
        """Test complete workflow from plan creation to report generation"""
        # Step 1: Manager creates plan
        page.goto(BASE_URL)
        page.fill('input[placeholder="user@company.com"]', "manager@company.com")
        page.fill('input[placeholder="Enter password"]', "manager123")
        page.click('button:has-text("Sign In")')
        
        page.wait_for_selector("text=Manager Dashboard", timeout=10000)
        page.click("text=Create Plan")
        
        # Create a plan with specific objectives
        plan_name = f"E2E Test Plan {time.time()}"
        page.fill('input[placeholder="Q4 Sales Analysis"]', plan_name)
        page.fill('textarea[placeholder*="Identify revenue trends"]', 
                  "- Increase revenue by 20%\n- Identify customer segments\n- Predict sales trends")
        page.select_option('select:has-text("Priority")', "High")
        
        # Upload test data (if file upload is available)
        # page.set_input_files('input[type="file"]', 'test_data.csv')
        
        page.click('button:has-text("Create Plan")')
        page.wait_for_selector(f"text=Plan '{plan_name}' created successfully", timeout=10000)
        
        # Step 2: Approve the plan
        page.click("text=Active Plans")
        page.click(f"text={plan_name}")
        
        # Look for approve button
        approve_button = page.locator('button:has-text("Approve")')
        if approve_button.is_visible():
            approve_button.click()
            page.wait_for_selector("text=Plan approved and tasks assigned", timeout=10000)
        
        # Step 3: Logout and login as associate
        page.click('button:has-text("Logout")')
        page.wait_for_selector("text=Sign In", timeout=10000)
        
        page.fill('input[placeholder="user@company.com"]', "associate@company.com")
        page.fill('input[placeholder="Enter password"]', "associate123")
        page.click('button:has-text("Sign In")')
        
        # Step 4: Associate executes task
        page.wait_for_selector("text=Analyst Dashboard", timeout=10000)
        page.click("text=My Tasks")
        
        # Check if tasks are available
        task_elements = page.locator('button:has-text("Start")')
        if task_elements.count() > 0:
            # Start first task
            task_elements.first.click()
            
            # Navigate to execute task
            page.click("text=Execute Task")
            page.click('button:has-text("Execute Analysis")')
            
            # Wait for completion
            page.wait_for_selector("text=Task completed successfully", timeout=30000)
        
        # Step 5: Manager generates report
        page.click('button:has-text("Logout")')
        page.fill('input[placeholder="user@company.com"]', "manager@company.com")
        page.fill('input[placeholder="Enter password"]', "manager123")
        page.click('button:has-text("Sign In")')
        
        page.wait_for_selector("text=Manager Dashboard", timeout=10000)
        page.click("text=Active Plans")
        page.click(f"text={plan_name}")
        
        # Generate report
        report_button = page.locator('button:has-text("Generate Report")')
        if report_button.is_visible():
            report_button.click()
            page.wait_for_selector("text=Report generated successfully", timeout=30000)
            
            # Verify report sections
            expect(page.locator("text=Executive Summary")).to_be_visible()
            expect(page.locator("text=Key Findings")).to_be_visible()
            expect(page.locator("text=Recommendations")).to_be_visible()
    
    def test_logout_functionality(self, page: Page):
        """Test logout works correctly"""
        # Login first
        page.goto(BASE_URL)
        page.fill('input[placeholder="user@company.com"]', "manager@company.com")
        page.fill('input[placeholder="Enter password"]', "manager123")
        page.click('button:has-text("Sign In")')
        
        # Wait for dashboard
        page.wait_for_selector("text=Manager Dashboard", timeout=10000)
        
        # Logout
        page.click('button:has-text("Logout")')
        
        # Should return to login page
        page.wait_for_selector("text=Sign In", timeout=10000)
        expect(page.locator("text=AI Data Analysis Platform")).to_be_visible()
    
    def test_invalid_login(self, page: Page):
        """Test invalid login shows error"""
        page.goto(BASE_URL)
        
        # Enter invalid credentials
        page.fill('input[placeholder="user@company.com"]', "invalid@company.com")
        page.fill('input[placeholder="Enter password"]', "wrongpassword")
        page.click('button:has-text("Sign In")')
        
        # Should show error
        page.wait_for_selector("text=Invalid email or password", timeout=10000)
    
    def test_responsive_design(self, page: Page):
        """Test app works on different screen sizes"""
        # Test desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(BASE_URL)
        expect(page.locator("text=AI Data Analysis Platform")).to_be_visible()
        
        # Test tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(BASE_URL)
        expect(page.locator("text=AI Data Analysis Platform")).to_be_visible()
        
        # Test mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(BASE_URL)
        expect(page.locator("text=AI Data Analysis Platform")).to_be_visible()


# Pytest configuration
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1920, "height": 1080}
    }


if __name__ == "__main__":
    # Run tests with: pytest tests/e2e/test_user_journeys.py --headed --slowmo 500
    pytest.main([__file__, "--headed", "--slowmo", "500"])