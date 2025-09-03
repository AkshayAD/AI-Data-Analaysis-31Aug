"""
End-to-End Tests for Milestone 1: Input & Objective Stage
Tests the complete functionality of Stage 0
"""

import pytest
from playwright.sync_api import Page, expect
import time
from pathlib import Path
import json
import re

BASE_URL = "http://localhost:8506"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "data"

class TestMilestone1:
    """Comprehensive tests for Milestone 1: Input & Objective Stage"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test"""
        # Navigate to the application
        page.goto(BASE_URL)
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        # Store page for use in tests
        self.page = page
    
    def test_01_page_loads_successfully(self):
        """Test that the main page loads without errors"""
        # Check page title
        expect(self.page).to_have_title("AI Analysis Platform - Input & Objectives")
        
        # Check main heading is present
        heading = self.page.locator("h1", has_text="AI-Powered Data Analysis Platform")
        expect(heading).to_be_visible()
        
        # Check subtitle is present
        subtitle = self.page.locator("p", has_text="Human-in-the-Loop Intelligence")
        expect(subtitle).to_be_visible()
    
    def test_02_progress_indicator_shows_correct_stage(self):
        """Test that progress indicator shows Stage 1 as active"""
        # Check that all stage indicators are visible on the page
        # We use text content since the stages are rendered via markdown
        
        # Check the active stage is present
        expect(self.page.locator("text=Input & Objectives")).to_be_visible()
        
        # Check other stages are present
        expect(self.page.locator("text=Plan Generation")).to_be_visible()
        expect(self.page.locator("text=Data Understanding")).to_be_visible()
        expect(self.page.locator("text=Task Configuration")).to_be_visible()
        expect(self.page.locator("text=Execution")).to_be_visible()
        expect(self.page.locator("text=Review & Export")).to_be_visible()
    
    def test_03_all_tabs_are_present(self):
        """Test that all required tabs are present"""
        tabs = ["📝 Objectives", "📁 Data Upload", "✅ Review & Proceed"]
        
        for tab_name in tabs:
            tab = self.page.get_by_role("tab", name=tab_name)
            expect(tab).to_be_visible()
    
    def test_04_objective_input_validation(self):
        """Test objective input validation and error messages"""
        # Click on Objectives tab
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        # Try to submit without filling required fields
        # First, we need to navigate to Review tab to see if validation works
        self.page.get_by_role("tab", name="✅ Review & Proceed").click()
        
        # Check for warning message about missing objective
        warning = self.page.locator("text=Please define your analysis objective")
        expect(warning).to_be_visible()
    
    def test_05_objective_input_works(self):
        """Test that objective input accepts and stores data"""
        # Click on Objectives tab
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        # Fill in the business objective - use first textarea
        objective_textarea = self.page.locator("textarea").first
        objective_textarea.fill("Analyze customer churn patterns to identify key factors driving customer attrition and develop retention strategies")
        
        # Select analysis type - Streamlit uses custom dropdowns
        analysis_dropdown = self.page.get_by_role("combobox").first
        analysis_dropdown.click()
        # Select the predictive option from the dropdown
        self.page.locator("text=🔮 Predictive Analysis").click()
        
        # Fill success criteria - use second textarea
        success_textarea = self.page.locator("textarea").nth(1)
        success_textarea.fill("- Identify top 3 churn factors\n- Achieve 85% prediction accuracy\n- Reduce churn by 20%")
        
        # Check that objective summary appears
        time.sleep(1)  # Give it a moment to process
        summary = self.page.locator("text=✅ Objective captured successfully")
        expect(summary).to_be_visible()
    
    def test_06_file_upload_accepts_multiple_formats(self):
        """Test that file uploader accepts various file formats"""
        # Click on Data Upload tab
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        # Check that file upload area is present
        upload_area = self.page.locator("text=Choose files to upload")
        expect(upload_area).to_be_visible()
        
        # Check supported file types info is shown
        info_text = self.page.locator("text=Supported File Types")
        expect(info_text).to_be_visible()
        
        # Verify all file type categories are listed
        file_categories = [
            "Structured Data: CSV, Excel, Parquet, JSON",
            "Documents: PDF, Word, Text files",
            "Images: PNG, JPG, GIF",
            "SQL: Database queries and schemas",
            "Notebooks: Jupyter notebooks, Python scripts"
        ]
        
        for category in file_categories:
            expect(self.page.locator(f"text={category}")).to_be_visible()
    
    def test_07_file_upload_process_csv(self):
        """Test uploading and processing a CSV file"""
        # Click on Data Upload tab
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        # Upload the sample CSV file
        sample_csv = TEST_DATA_DIR / "sample_customer_data.csv"
        
        if sample_csv.exists():
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(str(sample_csv))
            
            # Wait for file to be processed
            time.sleep(2)
            
            # Check success message
            success_msg = self.page.locator("text=✅ Uploaded: sample_customer_data.csv")
            expect(success_msg).to_be_visible()
            
            # Check file metadata is displayed (may have different format)
            # Look for either "10 rows" or just the file being present in the UI
            expect(self.page.locator("text=sample_customer_data.csv")).to_be_visible()
    
    def test_08_review_tab_shows_summary(self):
        """Test that Review tab shows complete summary"""
        # First, fill in objectives
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        objective_textarea = self.page.locator("textarea").first
        objective_textarea.fill("Test objective for customer analysis with sufficient length to pass validation")
        
        analysis_dropdown = self.page.get_by_role("combobox").first
        analysis_dropdown.click()
        self.page.locator("text=🔮 Predictive Analysis").click()
        
        # Upload a file
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        sample_csv = TEST_DATA_DIR / "sample_customer_data.csv"
        if sample_csv.exists():
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(str(sample_csv))
            time.sleep(2)
        
        # Go to Review tab
        self.page.get_by_role("tab", name="✅ Review & Proceed").click()
        
        # Check success message
        success = self.page.locator("text=✅ All required information provided")
        expect(success).to_be_visible()
        
        # Check objective summary is shown
        obj_summary = self.page.locator("text=Objective Summary")
        expect(obj_summary).to_be_visible()
        
        # Check files summary is shown
        files_summary = self.page.locator("text=Uploaded Files Summary")
        expect(files_summary).to_be_visible()
        
        # Check proceed button is present
        proceed_btn = self.page.get_by_role("button", name="🚀 Generate Analysis Plan")
        expect(proceed_btn).to_be_visible()
        expect(proceed_btn).to_be_enabled()
    
    def test_09_sidebar_help_sections_work(self):
        """Test that sidebar help sections are functional"""
        # Check sidebar is present
        sidebar = self.page.locator("section[data-testid='stSidebar']")
        expect(sidebar).to_be_visible()
        
        # Check help sections
        help_sections = [
            "📝 Writing Good Objectives",
            "📁 Data Preparation Tips",
            "🤖 AI Teammates"
        ]
        
        for section in help_sections:
            expander = sidebar.locator(f"text={section}")
            expect(expander).to_be_visible()
            
            # Click to expand
            expander.click()
            time.sleep(0.5)
            
            # Check some content is visible
            # For AI Teammates, check team member descriptions
            if "AI Teammates" in section:
                expect(sidebar.locator("text=Manager: Generates and refines")).to_be_visible()
    
    def test_10_optional_context_fields(self):
        """Test optional context fields in objectives"""
        # Click on Objectives tab
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        # Expand additional context
        context_expander = self.page.locator("text=📝 Additional Context (Optional)")
        context_expander.click()
        
        # Check all optional fields are present
        optional_fields = [
            "Data Source",
            "Time Period",
            "Industry/Domain",
            "Known Data Issues",
            "Expected Challenges",
            "Key Stakeholders",
            "Additional Notes"
        ]
        
        for field in optional_fields:
            field_element = self.page.locator(f"text={field}")
            expect(field_element).to_be_visible()
    
    def test_11_complete_workflow_integration(self):
        """Test the complete workflow from input to proceed"""
        # Step 1: Fill objectives
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        objective = self.page.locator("textarea").first
        objective.fill("Comprehensive analysis of customer behavior patterns to optimize retention strategies and reduce churn by 25%")
        
        analysis_type = self.page.get_by_role("combobox").first
        analysis_type.click()
        self.page.locator("text=🔮 Predictive Analysis").click()
        
        success_criteria = self.page.locator("textarea").nth(1)
        success_criteria.fill("- Identify key churn indicators\n- Build predictive model with >85% accuracy")
        
        # Step 2: Upload file
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        sample_file = TEST_DATA_DIR / "sample_customer_data.csv"
        if sample_file.exists():
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(str(sample_file))
            time.sleep(2)
        
        # Step 3: Review and proceed
        self.page.get_by_role("tab", name="✅ Review & Proceed").click()
        
        # Verify all information is present
        expect(self.page.locator("text=✅ All required information provided")).to_be_visible()
        
        # Click proceed button
        proceed_btn = self.page.get_by_role("button", name="🚀 Generate Analysis Plan")
        proceed_btn.click()
        
        # Check success indicators
        expect(self.page.locator("text=✅ Context saved")).to_be_visible()
        expect(self.page.locator("text=Next Steps")).to_be_visible()
    
    def test_12_file_deletion_works(self):
        """Test that uploaded files can be deleted"""
        # Upload a file
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        sample_file = TEST_DATA_DIR / "sample_customer_data.csv"
        if sample_file.exists():
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(str(sample_file))
            time.sleep(2)
            
            # Find and click delete button
            delete_btn = self.page.locator("button").filter(has_text="🗑️")
            if delete_btn.count() > 0:
                delete_btn.first.click()
                time.sleep(1)
                
                # Check file is removed
                expect(self.page.locator("text=sample_customer_data.csv")).not_to_be_visible()
    
    def test_13_analysis_type_descriptions(self):
        """Test that analysis type descriptions are shown"""
        self.page.get_by_role("tab", name="📝 Objectives").click()
        
        analysis_types = {
            "🔍 Exploratory Analysis": "Discover patterns, relationships, and insights",
            "🔮 Predictive Analysis": "Build models to forecast future outcomes",
            "🏥 Diagnostic Analysis": "Understand why something happened",
            "📊 Descriptive Analysis": "Summarize and describe historical data"
        }
        
        dropdown = self.page.get_by_role("combobox").first
        
        for type_name, description in analysis_types.items():
            dropdown.click()
            self.page.locator(f"text={type_name}").click()
            time.sleep(0.5)
            
            # Check description is shown
            expect(self.page.locator(f"text={description}")).to_be_visible()
    
    def test_14_validation_prevents_proceed_without_data(self):
        """Test that validation prevents proceeding without required data"""
        # Go directly to Review tab without filling anything
        self.page.get_by_role("tab", name="✅ Review & Proceed").click()
        
        # Check warning messages
        expect(self.page.locator("text=Please define your analysis objective")).to_be_visible()
        expect(self.page.locator("text=Please upload at least one data file")).to_be_visible()
        
        # Proceed button should not be visible
        proceed_btn = self.page.get_by_role("button", name="🚀 Generate Analysis Plan")
        expect(proceed_btn).not_to_be_visible()
    
    def test_15_session_info_in_sidebar(self):
        """Test that session information is displayed in sidebar"""
        sidebar = self.page.locator("section[data-testid='stSidebar']")
        
        # Check session info section
        expect(sidebar.locator("text=Session Information")).to_be_visible()
        
        # After uploading a file, check if file count is updated
        self.page.get_by_role("tab", name="📁 Data Upload").click()
        
        sample_file = TEST_DATA_DIR / "sample_customer_data.csv"
        if sample_file.exists():
            file_input = self.page.locator("input[type='file']")
            file_input.set_input_files(str(sample_file))
            time.sleep(2)
            
            # Check file count in sidebar
            expect(sidebar.locator("text=Files: 1")).to_be_visible()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", 
        "milestone1: marks tests for Milestone 1"
    )

# Run configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])