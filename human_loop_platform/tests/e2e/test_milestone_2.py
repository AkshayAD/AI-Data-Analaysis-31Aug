"""
End-to-End Tests for Milestone 2: Plan Generation with AI Manager
Tests the AI-powered plan generation, editing, and chat features
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path
import json

BASE_URL = "http://localhost:8506"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "data"

class TestMilestone2:
    """Comprehensive tests for Milestone 2: Plan Generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test - complete Stage 0 first"""
        # Store page for use in tests
        self.page = page
        
        # Navigate to the application
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Complete Stage 0 to set up context
        self._complete_stage_0(page)
    
    def _complete_stage_0(self, page: Page):
        """Complete Stage 0 to set up context for testing"""
        # Click on Objectives tab
        objectives_tab = page.get_by_role("tab", name="📝 Objectives")
        if objectives_tab.count() > 0:
            objectives_tab.click()
            time.sleep(1)
            
            # Fill objective
            objective_textarea = page.locator("textarea").first
            objective_textarea.fill("Test objective for plan generation - analyze customer churn patterns")
            
            # Select analysis type
            analysis_dropdown = page.get_by_role("combobox").first
            analysis_dropdown.click()
            page.locator("text=🔮 Predictive Analysis").last.click()
            
            # Go to Data Upload tab
            page.get_by_role("tab", name="📁 Data Upload").click()
            time.sleep(1)
            
            # Upload sample file
            sample_csv = TEST_DATA_DIR / "sample_customer_data.csv"
            if sample_csv.exists():
                file_input = page.locator("input[type='file']")
                file_input.set_input_files(str(sample_csv))
                time.sleep(2)
            
            # Go to Review tab
            page.get_by_role("tab", name="✅ Review & Proceed").click()
            time.sleep(1)
            
            # Click proceed button if available
            proceed_btn = page.get_by_role("button", name="🚀 Generate Analysis Plan")
            if proceed_btn.count() > 0:
                # Wait for button to be enabled
                expect(proceed_btn).to_be_enabled()
                proceed_btn.click()
                
                # Wait for navigation to complete - check for Plan Generation page
                page.wait_for_timeout(3000)
                # Alternatively, wait for specific element on the next page
                page.wait_for_selector("text=Plan Generation", timeout=10000)
    
    def test_01_plan_generation_page_loads(self):
        """Test that Plan Generation page loads successfully"""
        # Take a screenshot for debugging
        self.page.screenshot(path="tests/screenshots/m2_test01_before.png")
        
        # Check page title indicates we're on Plan Generation stage
        # The h1 is rendered as HTML so we look for the text content
        expect(self.page.locator("text=AI-Powered Plan Generation")).to_be_visible()
        
        # Check progress indicator shows Stage 2 as active
        expect(self.page.locator("text=Plan Generation")).to_be_visible()
    
    def test_02_context_is_loaded(self):
        """Test that context from Stage 0 is loaded"""
        # Check for context display
        context_expander = self.page.locator("text=📌 Analysis Context")
        expect(context_expander).to_be_visible()
        
        # Click to expand if needed
        context_expander.click()
        
        # Check objective is displayed
        expect(self.page.locator("text=Test objective for plan generation")).to_be_visible()
        
        # Check analysis type is shown
        expect(self.page.locator("text=predictive")).to_be_visible()
    
    def test_03_generate_plan_button_works(self):
        """Test that Generate Plan button triggers plan generation"""
        # Find and click Generate Plan button
        generate_btn = self.page.get_by_role("button", name="🎯 Generate Plan")
        expect(generate_btn).to_be_visible()
        
        generate_btn.click()
        
        # Wait for plan generation (with spinner)
        time.sleep(5)
        
        # Check success message
        expect(self.page.locator("text=✅ Plan generated successfully")).to_be_visible()
        
        # Check plan preview is shown
        expect(self.page.locator("text=Plan Preview")).to_be_visible()
    
    def test_04_tabs_are_present(self):
        """Test that all tabs are present"""
        tabs = ["🚀 Generate", "✏️ Edit", "📋 Summary"]
        
        for tab_name in tabs:
            tab = self.page.get_by_role("tab", name=tab_name)
            expect(tab).to_be_visible()
    
    def test_05_edit_tab_shows_editor(self):
        """Test that Edit tab shows plan editor"""
        # First generate a plan
        generate_btn = self.page.get_by_role("button", name="🎯 Generate Plan")
        if generate_btn.count() > 0:
            generate_btn.click()
            time.sleep(3)
        
        # Click Edit tab
        edit_tab = self.page.get_by_role("tab", name="✏️ Edit")
        edit_tab.click()
        
        # Check editor is visible
        expect(self.page.locator("text=Edit Analysis Plan")).to_be_visible()
        
        # Check format selector is present
        expect(self.page.locator("text=Format")).to_be_visible()
    
    def test_06_chat_interface_is_present(self):
        """Test that AI chat interface is available"""
        # Check chat header
        expect(self.page.locator("text=💬 AI Assistant")).to_be_visible()
        
        # Check teammate selector
        expect(self.page.locator("text=Chat with:")).to_be_visible()
        
        # Check chat input - using text input or textarea
        chat_input = self.page.locator("textarea").or_(self.page.locator("input[type='text']"))
        expect(chat_input.first).to_be_visible()
    
    def test_07_quick_actions_available(self):
        """Test that quick actions are available"""
        # Expand quick actions if needed
        quick_actions = self.page.locator("text=Quick Actions")
        if quick_actions.count() > 0:
            quick_actions.click()
            time.sleep(1)
        
        # Check action buttons
        actions = ["📋 Send to Reviewer", "📊 Send to Associate", 
                  "🧮 Send to Analyst", "👔 Regenerate"]
        
        for action in actions:
            btn = self.page.get_by_role("button", name=action)
            expect(btn).to_be_visible()
    
    def test_08_summary_tab_shows_plan_details(self):
        """Test that Summary tab displays plan details"""
        # Generate a plan first
        generate_btn = self.page.get_by_role("button", name="🎯 Generate Plan")
        if generate_btn.count() > 0:
            generate_btn.click()
            time.sleep(3)
        
        # Click Summary tab
        summary_tab = self.page.get_by_role("tab", name="📋 Summary")
        summary_tab.click()
        
        # Check summary elements
        expect(self.page.locator("text=Plan Summary")).to_be_visible()
        
        # Check metrics are shown
        expect(self.page.locator("text=Phases")).to_be_visible()
        expect(self.page.locator("text=Total Tasks")).to_be_visible()
    
    def test_09_navigation_buttons_work(self):
        """Test navigation buttons"""
        # Check Previous button
        prev_btn = self.page.get_by_role("button", name="← Previous")
        expect(prev_btn).to_be_visible()
        
        # Check Save button
        save_btn = self.page.get_by_role("button", name="💾 Save Plan")
        expect(save_btn).to_be_visible()
        
        # Check Export button
        export_btn = self.page.get_by_role("button", name="📥 Export")
        expect(export_btn).to_be_visible()
    
    def test_10_approve_and_continue_button(self):
        """Test Approve & Continue button appears after plan generation"""
        # Generate a plan
        generate_btn = self.page.get_by_role("button", name="🎯 Generate Plan")
        if generate_btn.count() > 0:
            generate_btn.click()
            time.sleep(3)
        
        # Check Approve & Continue button
        approve_btn = self.page.get_by_role("button", name="✅ Approve & Continue →")
        expect(approve_btn).to_be_visible()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", 
        "milestone2: marks tests for Milestone 2"
    )

# Run configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])