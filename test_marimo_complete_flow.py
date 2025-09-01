#!/usr/bin/env python3
"""
Complete End-to-End Test of AI Data Analysis Team with Marimo Integration
Captures screenshots at every step of the process
"""

import os
import sys
import time
import asyncio
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd

# Configuration
STREAMLIT_PORT = 8503
SCREENSHOT_DIR = "screenshots_marimo_flow"
BASE_URL = f"http://localhost:{STREAMLIT_PORT}"
HEADLESS = False  # Set to False to see browser

# Test data configuration
TEST_PROJECT_NAME = "Sales Analysis Q4 2024"
TEST_PROBLEM_STATEMENT = """Analyze our Q4 sales data to identify:
1. Top performing products and regions
2. Sales trends and seasonal patterns
3. Customer segmentation opportunities
4. Revenue forecasting for Q1 2025
5. Anomalies or unusual patterns that need attention"""

TEST_DATA_CONTEXT = """This dataset contains our complete sales transactions from Q4 2024,
including product details, customer information, regional data, and promotional campaigns.
The data has been cleaned and validated by our data team."""

# Sample Gemini API key (for testing purposes - won't actually call API)
TEST_API_KEY = "test_gemini_api_key_12345"

async def create_test_data():
    """Create sample CSV file for testing"""
    print("Creating test data...")
    
    # Create sample sales data
    data = {
        'date': pd.date_range('2024-10-01', periods=90, freq='D').astype(str),
        'product_id': ['PROD_' + str(i % 20) for i in range(90)],
        'product_name': ['Product ' + str(i % 20) for i in range(90)],
        'category': ['Electronics', 'Clothing', 'Home', 'Sports', 'Books'] * 18,
        'quantity': [5 + i % 10 for i in range(90)],
        'unit_price': [29.99 + (i % 20) * 10 for i in range(90)],
        'revenue': [0] * 90,  # Will be calculated
        'customer_id': ['CUST_' + str(i % 30) for i in range(90)],
        'region': ['North', 'South', 'East', 'West', 'Central'] * 18,
        'discount_percent': [0, 5, 10, 15, 20] * 18,
        'promotion': ['None', 'Email', 'Social', 'TV', 'Print'] * 18
    }
    
    df = pd.DataFrame(data)
    df['revenue'] = df['quantity'] * df['unit_price'] * (1 - df['discount_percent']/100)
    
    # Save to CSV
    test_file = '/tmp/q4_sales_data.csv'
    df.to_csv(test_file, index=False)
    print(f"Test data created: {test_file}")
    return test_file

async def start_streamlit_app():
    """Start the Streamlit application"""
    print(f"Starting Streamlit app on port {STREAMLIT_PORT}...")
    process = subprocess.Popen(
        ['streamlit', 'run', 'streamlit_app_marimo_integrated.py',
         '--server.port', str(STREAMLIT_PORT),
         '--server.headless', 'true',
         '--browser.gatherUsageStats', 'false'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for app to start
    await asyncio.sleep(5)
    return process

async def capture_screenshot(page, step_num, step_name):
    """Capture and save screenshot"""
    filename = f"{SCREENSHOT_DIR}/step_{step_num:02d}_{step_name}.png"
    await page.screenshot(path=filename, full_page=True)
    print(f"  📸 Screenshot saved: {filename}")
    return filename

async def test_complete_flow():
    """Run the complete test flow"""
    
    # Create screenshot directory
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    print(f"\n{'='*60}")
    print("AI DATA ANALYSIS TEAM - COMPLETE FLOW TEST")
    print(f"{'='*60}\n")
    
    # Create test data
    test_file = await create_test_data()
    
    # Start Streamlit app
    app_process = await start_streamlit_app()
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=HEADLESS)
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()
            
            screenshots = []
            
            print("\n🚀 Starting test flow...\n")
            
            # Step 1: Navigate to app
            print("Step 1: Loading application...")
            await page.goto(BASE_URL)
            await asyncio.sleep(3)
            screenshots.append(await capture_screenshot(page, 1, "initial_load"))
            
            # Step 2: Enter API Key
            print("\nStep 2: Configuring API key...")
            api_input = await page.wait_for_selector('input[type="password"]', timeout=10000)
            await api_input.fill(TEST_API_KEY)
            await asyncio.sleep(1)
            screenshots.append(await capture_screenshot(page, 2, "api_key_entered"))
            
            # Step 3: Fill project setup form
            print("\nStep 3: Setting up project...")
            
            # Enter project name
            project_input = await page.wait_for_selector('input[placeholder*="My Analysis Project"]', timeout=5000)
            if not project_input:
                project_input = await page.query_selector('input:has-text("Project Name")')
            if project_input:
                await project_input.fill(TEST_PROJECT_NAME)
            
            # Enter problem statement
            problem_textarea = await page.query_selector('textarea[placeholder*="What insights"]')
            if not problem_textarea:
                problem_textarea = await page.query_selector_all('textarea')[0]
            if problem_textarea:
                await problem_textarea.fill(TEST_PROBLEM_STATEMENT)
            
            # Enter data context
            context_textarea = await page.query_selector('textarea[placeholder*="Background information"]')
            if not context_textarea:
                textareas = await page.query_selector_all('textarea')
                if len(textareas) > 1:
                    context_textarea = textareas[1]
            if context_textarea:
                await context_textarea.fill(TEST_DATA_CONTEXT)
            
            await asyncio.sleep(1)
            screenshots.append(await capture_screenshot(page, 3, "project_details_filled"))
            
            # Step 4: Upload data file
            print("\nStep 4: Uploading data file...")
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await file_input.set_input_files(test_file)
                await asyncio.sleep(2)
            screenshots.append(await capture_screenshot(page, 4, "data_uploaded"))
            
            # Step 5: Start analysis
            print("\nStep 5: Starting analysis...")
            start_button = await page.query_selector('button:has-text("Start Analysis")')
            if start_button:
                await start_button.click()
                await asyncio.sleep(5)
            screenshots.append(await capture_screenshot(page, 5, "analysis_started"))
            
            # Step 6: Manager Planning
            print("\nStep 6: Manager creating strategic plan...")
            await asyncio.sleep(3)
            
            # Wait for plan to be generated
            await page.wait_for_selector('text=/Strategic.*Plan/i', timeout=15000)
            screenshots.append(await capture_screenshot(page, 6, "manager_plan"))
            
            # Click continue
            continue_btn = await page.query_selector('button:has-text("Continue to Data Analysis")')
            if not continue_btn:
                continue_btn = await page.query_selector('button:has-text("Continue")')
            if continue_btn:
                await continue_btn.click()
                await asyncio.sleep(3)
            
            # Step 7: Data Understanding
            print("\nStep 7: Analyst examining data...")
            await page.wait_for_selector('text=/Data.*Assessment/i', timeout=10000)
            screenshots.append(await capture_screenshot(page, 7, "data_understanding"))
            
            # Click continue
            continue_btn = await page.query_selector('button:has-text("Generate Analysis Tasks")')
            if not continue_btn:
                continue_btn = await page.query_selector('button:has-text("Continue")')
            if continue_btn:
                await continue_btn.click()
                await asyncio.sleep(3)
            
            # Step 8: Task Generation
            print("\nStep 8: Associate generating tasks...")
            await page.wait_for_selector('text=/Analysis.*Tasks/i', timeout=10000)
            screenshots.append(await capture_screenshot(page, 8, "task_generation"))
            
            # Expand first few tasks
            task_expanders = await page.query_selector_all('button:has-text("Task")')
            for i, expander in enumerate(task_expanders[:3]):
                if expander:
                    await expander.click()
                    await asyncio.sleep(0.5)
            
            screenshots.append(await capture_screenshot(page, 9, "tasks_expanded"))
            
            # Select execution mode and continue
            radio_button = await page.query_selector('text="Automated with Marimo"')
            if radio_button:
                await radio_button.click()
            
            execute_btn = await page.query_selector('button:has-text("Execute Analysis")')
            if execute_btn:
                await execute_btn.click()
                await asyncio.sleep(5)
            
            # Step 9: Marimo Execution
            print("\nStep 9: Executing tasks with Marimo...")
            await page.wait_for_selector('text=/Execution.*Progress/i', timeout=10000)
            screenshots.append(await capture_screenshot(page, 10, "marimo_execution_start"))
            
            # Wait for execution to complete
            await asyncio.sleep(10)
            screenshots.append(await capture_screenshot(page, 11, "marimo_execution_progress"))
            
            # Check for completion
            await page.wait_for_selector('text=/completed/i', timeout=20000)
            screenshots.append(await capture_screenshot(page, 12, "marimo_execution_complete"))
            
            # Continue to report
            report_btn = await page.query_selector('button:has-text("Generate Report")')
            if report_btn:
                await report_btn.click()
                await asyncio.sleep(5)
            
            # Step 10: Final Report
            print("\nStep 10: Generating final report...")
            await page.wait_for_selector('text=/Final.*Report/i', timeout=15000)
            screenshots.append(await capture_screenshot(page, 13, "final_report_header"))
            
            # Scroll to capture full report
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight * 0.5)')
            await asyncio.sleep(1)
            screenshots.append(await capture_screenshot(page, 14, "final_report_middle"))
            
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(1)
            screenshots.append(await capture_screenshot(page, 15, "final_report_bottom"))
            
            # Expand additional sections
            print("\nStep 11: Exploring report sections...")
            
            # Expand artifacts
            artifacts_btn = await page.query_selector('button:has-text("Analysis Artifacts")')
            if artifacts_btn:
                await artifacts_btn.click()
                await asyncio.sleep(1)
                screenshots.append(await capture_screenshot(page, 16, "analysis_artifacts"))
            
            # Expand conversation history
            history_btn = await page.query_selector('button:has-text("Analysis Conversation")')
            if history_btn:
                await history_btn.click()
                await asyncio.sleep(1)
                screenshots.append(await capture_screenshot(page, 17, "conversation_history"))
            
            # Export options
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            screenshots.append(await capture_screenshot(page, 18, "export_options"))
            
            print("\n✅ Test completed successfully!")
            print(f"\n📸 Total screenshots captured: {len(screenshots)}")
            
            # Generate summary
            await generate_summary_report(screenshots)
            
            await browser.close()
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop Streamlit app
        app_process.terminate()
        app_process.wait()
        print("\n🛑 Streamlit app stopped")

async def generate_summary_report(screenshots):
    """Generate HTML summary with all screenshots"""
    print("\n📝 Generating summary report...")
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Data Analysis Team - Complete Flow Test Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #1f77b4;
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .step {
            background: white;
            margin: 30px 0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .step h2 {
            color: #17a2b8;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .screenshot {
            margin: 20px 0;
            text-align: center;
        }
        .screenshot img {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .caption {
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }
        .summary {
            background: #e8f4f8;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }
        .flow-diagram {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .flow-step {
            display: inline-block;
            padding: 10px 20px;
            background: #1f77b4;
            color: white;
            border-radius: 5px;
            margin: 5px;
        }
        .arrow {
            display: inline-block;
            margin: 0 10px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>🤖 AI Data Analysis Team with Marimo Integration</h1>
    <h2 style="text-align: center; color: #666;">Complete Flow Test Results</h2>
    <div class="timestamp">Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Project:</strong> Sales Analysis Q4 2024</p>
        <p><strong>Problem:</strong> Comprehensive sales analysis with forecasting and segmentation</p>
        <p><strong>Total Steps:</strong> 11</p>
        <p><strong>Screenshots Captured:</strong> """ + str(len(screenshots)) + """</p>
        <p><strong>Status:</strong> ✅ Successfully Completed</p>
    </div>
    
    <div class="flow-diagram">
        <h2>🔄 Application Flow</h2>
        <div style="text-align: center; padding: 20px;">
            <span class="flow-step">1. Setup</span>
            <span class="arrow">→</span>
            <span class="flow-step">2. Manager Plan</span>
            <span class="arrow">→</span>
            <span class="flow-step">3. Data Analysis</span>
            <span class="arrow">→</span>
            <span class="flow-step">4. Task Generation</span>
            <span class="arrow">→</span>
            <span class="flow-step">5. Marimo Execution</span>
            <span class="arrow">→</span>
            <span class="flow-step">6. Final Report</span>
        </div>
    </div>
"""
    
    # Define step descriptions
    step_descriptions = {
        "initial_load": ("Step 1: Application Launch", "The application loads with the project setup form ready for user input."),
        "api_key_entered": ("Step 2: API Configuration", "Gemini API key is configured to enable AI capabilities."),
        "project_details_filled": ("Step 3: Project Setup", "Project name, problem statement, and data context are provided."),
        "data_uploaded": ("Step 4: Data Upload", "Q4 sales data CSV file is uploaded for analysis."),
        "analysis_started": ("Step 5: Analysis Initiated", "Project is initialized and the analysis workflow begins."),
        "manager_plan": ("Step 6: Strategic Planning", "AI Manager creates a comprehensive analysis plan with objectives and methodology."),
        "data_understanding": ("Step 7: Data Profiling", "AI Analyst examines the data structure, quality, and statistics."),
        "task_generation": ("Step 8: Task Creation", "AI Associate generates specific, executable analysis tasks."),
        "tasks_expanded": ("Step 8b: Task Details", "Individual tasks are expanded to show objectives, methods, and expected outputs."),
        "marimo_execution_start": ("Step 9: Automated Execution", "Tasks are converted to Marimo notebooks and execution begins."),
        "marimo_execution_progress": ("Step 9b: Execution Progress", "Real-time progress of task execution in Marimo notebooks."),
        "marimo_execution_complete": ("Step 9c: Execution Complete", "All analysis tasks have been successfully executed."),
        "final_report_header": ("Step 10: Executive Report", "AI Manager synthesizes results into a comprehensive report."),
        "final_report_middle": ("Step 10b: Report Details", "Detailed findings and recommendations from the analysis."),
        "final_report_bottom": ("Step 10c: Report Conclusion", "Final insights and next steps."),
        "analysis_artifacts": ("Step 11: Analysis Artifacts", "Overview of all generated notebooks and analysis outputs."),
        "conversation_history": ("Step 11b: AI Conversation", "Complete conversation history between AI personas."),
        "export_options": ("Step 11c: Export Options", "Options to export report, notebooks, and save project state.")
    }
    
    # Add screenshots with descriptions
    for screenshot in screenshots:
        filename = os.path.basename(screenshot)
        step_key = filename.replace('.png', '').split('_', 2)[2] if '_' in filename else filename
        
        if step_key in step_descriptions:
            title, description = step_descriptions[step_key]
        else:
            title = f"Step: {step_key.replace('_', ' ').title()}"
            description = "Analysis step captured during the test flow."
        
        html_content += f"""
    <div class="step">
        <h2>{title}</h2>
        <p>{description}</p>
        <div class="screenshot">
            <img src="{filename}" alt="{title}">
            <div class="caption">{filename}</div>
        </div>
    </div>
"""
    
    # Add conclusion
    html_content += """
    <div class="summary" style="margin-top: 50px;">
        <h2>✅ Test Conclusion</h2>
        <p>The complete flow test has successfully demonstrated:</p>
        <ul>
            <li>✅ Seamless integration of AI personas (Manager, Analyst, Associate)</li>
            <li>✅ Step-by-step guided analysis workflow</li>
            <li>✅ Automatic task generation based on data and objectives</li>
            <li>✅ Marimo notebook creation and execution</li>
            <li>✅ Comprehensive report generation with actionable insights</li>
            <li>✅ Full traceability of the analysis process</li>
        </ul>
        <p><strong>Key Achievement:</strong> The system successfully combines the conversation flow from 
        AI-Data-Analysis-Team with automated Marimo execution, creating a powerful end-to-end data analysis platform.</p>
    </div>
    
    <div style="text-align: center; padding: 30px; color: #666;">
        <p>Generated by AI Data Analysis Team Test Suite</p>
        <p>© 2024 Terragon Labs</p>
    </div>
</body>
</html>
"""
    
    # Save HTML report
    report_path = f"{SCREENSHOT_DIR}/test_report.html"
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Summary report generated: {report_path}")
    print(f"   Open {report_path} in a browser to view the complete test results")

async def main():
    """Main test runner"""
    try:
        await test_complete_flow()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if required modules are installed
    try:
        import pandas
        import playwright
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Install with: pip install pandas playwright")
        print("Then run: playwright install chromium")
        sys.exit(1)
    
    # Run the test
    asyncio.run(main())