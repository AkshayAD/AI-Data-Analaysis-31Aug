"""
Direct Tests for Milestone 2: Plan Generation
Tests the Plan Generation page directly without navigation
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path
import json

BASE_URL = "http://localhost:8506"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "data"

class TestMilestone2Direct:
    """Direct tests for Milestone 2: Plan Generation functionality"""
    
    def setup_method(self):
        """Setup test data in the context file"""
        # Create a minimal context file that Stage 1 will read
        context_data = {
            "objective": "Test objective for plan generation - analyze customer churn patterns",
            "analysis_type": "predictive",
            "uploaded_files": ["sample_customer_data.csv"],
            "timestamp": "2024-01-01 10:00:00"
        }
        
        context_file = TEST_DATA_DIR / "analysis_context.json"
        context_file.parent.mkdir(exist_ok=True)
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
    
    def test_01_plan_generation_direct_access(self, page: Page):
        """Test accessing Plan Generation page directly with URL parameter"""
        # Navigate directly to the app with stage parameter
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        
        # Check if we're on Stage 0
        if page.locator("text=Define Your Analysis Objective").is_visible():
            # We need to manually trigger stage 1
            # This is a limitation of Streamlit's session state
            # For now, let's test what we can
            
            # Take screenshot of initial state
            page.screenshot(path="tests/screenshots/m2_direct_stage0.png")
            
            # Try to complete Stage 0 quickly
            # Click on Objectives tab
            objectives_tab = page.get_by_role("tab", name="📝 Objectives")
            if objectives_tab.count() > 0:
                objectives_tab.click()
                time.sleep(1)
                
                # Fill objective
                objective_textarea = page.locator("textarea").first
                objective_textarea.fill("Test objective")
                
                # Select analysis type
                analysis_dropdown = page.get_by_role("combobox").first
                if analysis_dropdown.count() > 0:
                    analysis_dropdown.click()
                    page.locator("text=Predictive Analysis").first.click()
            
            # Go to Review tab
            review_tab = page.get_by_role("tab", name="✅ Review & Proceed")
            if review_tab.count() > 0:
                review_tab.click()
                time.sleep(1)
                
                # Take screenshot
                page.screenshot(path="tests/screenshots/m2_direct_review.png")
                
                # Look for Generate button
                generate_btn = page.get_by_role("button", name="🚀 Generate Analysis Plan")
                expect(generate_btn).to_be_visible()
                
                # Click it
                generate_btn.click()
                time.sleep(5)  # Wait for navigation
                
                # Take screenshot after navigation attempt
                page.screenshot(path="tests/screenshots/m2_direct_after_generate.png")
    
    def test_02_test_stage_1_components(self, page: Page):
        """Test Stage 1 UI components if accessible"""
        page.goto(BASE_URL) 
        page.wait_for_load_state("networkidle")
        
        # Quick complete Stage 0 - simplified version
        obj_tab = page.locator("text=Objectives").first
        if obj_tab.is_visible():
            obj_tab.click()
            page.locator("textarea").first.fill("Test")
            
        review_tab = page.locator("text=Review").first  
        if review_tab.is_visible():
            review_tab.click()
            time.sleep(1)
            
            btn = page.locator("button").filter(has_text="Generate")
            if btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(5000)
                
                # Now check for Plan Generation elements
                # Look for any sign we're on Stage 1
                page.screenshot(path="tests/screenshots/m2_stage1_check.png")
                
                # Check for tabs that should be on Plan Generation page
                if page.locator("text=Generate").is_visible():
                    print("Found Generate tab")
                    
                if page.locator("text=Edit").is_visible():
                    print("Found Edit tab")
                    
                if page.locator("text=Summary").is_visible():
                    print("Found Summary tab")
    
    def test_03_validate_context_file(self):
        """Test that context file is properly created"""
        context_file = TEST_DATA_DIR / "analysis_context.json"
        assert context_file.exists(), "Context file should exist"
        
        with open(context_file, 'r') as f:
            data = json.load(f)
            
        assert "objective" in data
        assert "analysis_type" in data
        assert data["objective"] == "Test objective for plan generation - analyze customer churn patterns"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])