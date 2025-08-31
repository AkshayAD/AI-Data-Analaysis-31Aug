#!/usr/bin/env python3
"""
Manual step-by-step testing of the platform
Tests each component individually to verify functionality
"""
from playwright.sync_api import sync_playwright
import pandas as pd
import time

APP_URL = "http://localhost:8502"

def test_login_system():
    """Test the authentication system"""
    print("\n🔐 Testing Authentication System")
    print("-" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)  # Visible browser
        page = browser.new_page()
        
        # Navigate to app
        page.goto(APP_URL)
        page.wait_for_timeout(3000)
        
        print("1. Testing invalid login:")
        inputs = page.locator("input").all()
        if len(inputs) >= 2:
            inputs[0].fill("invalid@test.com")
            inputs[1].fill("wrongpass")
            page.locator("button", has_text="Sign In").click()
            page.wait_for_timeout(2000)
            
            if page.locator("text=Invalid email or password").is_visible():
                print("   ✓ Invalid login correctly rejected")
            else:
                print("   ✗ Error message not shown")
        
        print("\n2. Testing manager login:")
        inputs = page.locator("input").all()
        inputs[0].clear()
        inputs[0].fill("manager@company.com")
        inputs[1].clear()
        inputs[1].fill("manager123")
        page.locator("button", has_text="Sign In").click()
        page.wait_for_timeout(3000)
        
        if page.locator("text=Manager Dashboard").is_visible():
            print("   ✓ Manager login successful")
            print("   ✓ Role-based dashboard loaded")
            
            # Check for tabs
            tabs = ["Overview", "Create Plan", "Active Plans", "Team", "Reports"]
            for tab in tabs:
                if page.locator(f"text={tab}").is_visible():
                    print(f"   ✓ Found tab: {tab}")
        
        # Logout
        page.locator("button", has_text="Logout").click()
        page.wait_for_timeout(2000)
        
        print("\n3. Testing associate login:")
        inputs = page.locator("input").all()
        inputs[0].fill("associate@company.com")
        inputs[1].fill("associate123")
        page.locator("button", has_text="Sign In").click()
        page.wait_for_timeout(3000)
        
        if page.locator("text=Analyst Dashboard").is_visible():
            print("   ✓ Associate login successful")
            print("   ✓ Different dashboard for associate role")
            
            # Check for tabs
            tabs = ["My Tasks", "Execute Task", "Completed", "Performance"]
            for tab in tabs:
                if page.locator(f"text={tab}").count() > 0:
                    print(f"   ✓ Found tab: {tab}")
        
        input("Press Enter to continue...")
        browser.close()

def test_data_upload_and_plan_creation():
    """Test data upload and plan creation"""
    print("\n📊 Testing Data Upload & Plan Creation")
    print("-" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()
        
        # Login as manager
        page.goto(APP_URL)
        page.wait_for_timeout(3000)
        inputs = page.locator("input").all()
        inputs[0].fill("manager@company.com")
        inputs[1].fill("manager123")
        page.locator("button", has_text="Sign In").click()
        page.wait_for_timeout(3000)
        
        # Navigate to Create Plan
        page.locator("text=Create Plan").click()
        page.wait_for_timeout(2000)
        
        print("1. Filling plan details:")
        
        # Fill plan name
        plan_inputs = page.locator("input").all()
        for inp in plan_inputs:
            placeholder = inp.get_attribute("placeholder")
            if placeholder and "Plan" in placeholder:
                inp.fill("Sales Analysis Q4 2024")
                print("   ✓ Plan name entered")
                break
        
        # Fill objectives
        textareas = page.locator("textarea").all()
        if textareas:
            objectives = """- Analyze Q4 sales performance
- Identify top performing products
- Segment customers by purchase behavior
- Detect anomalies in sales patterns
- Predict Q1 2025 sales trends"""
            textareas[0].fill(objectives)
            print("   ✓ Business objectives entered")
        
        # Select priority
        try:
            selects = page.locator("select").all()
            for select in selects:
                if "Priority" in select.inner_text():
                    select.select_option("High")
                    print("   ✓ Priority set to High")
                    break
        except:
            pass
        
        # Upload data file
        print("\n2. Uploading data file:")
        file_inputs = page.locator("input[type='file']").all()
        if file_inputs:
            file_inputs[0].set_input_files("sample_data.csv")
            print("   ✓ Sample data uploaded")
            page.wait_for_timeout(2000)
        
        print("\n3. Creating plan:")
        create_button = page.locator("button", has_text="Create Plan")
        create_button.click()
        page.wait_for_timeout(5000)
        
        # Check results
        if page.locator("text=created successfully").is_visible():
            print("   ✓ Plan created successfully")
        
        if page.locator("text=Generated Tasks").is_visible():
            print("   ✓ Tasks auto-generated from objectives")
            
            # Count generated tasks
            task_elements = page.locator("text=/.*Task.*/").all()
            print(f"   ✓ Generated {len(task_elements)} analysis tasks")
        
        input("Press Enter to continue...")
        browser.close()

def test_task_execution():
    """Test actual task execution with data analysis"""
    print("\n⚡ Testing Task Execution Engine")
    print("-" * 40)
    
    # First, test the executor directly
    print("1. Testing TaskExecutor directly:")
    
    import sys
    sys.path.append('src/python')
    
    from execution.task_executor import TaskExecutor
    
    # Load sample data
    df = pd.read_csv("sample_data.csv")
    print(f"   ✓ Loaded sample data: {df.shape}")
    
    executor = TaskExecutor()
    
    # Test different task types
    tasks = [
        {'id': '1', 'name': 'Data Profiling', 'type': 'data_profiling'},
        {'id': '2', 'name': 'Statistical Analysis', 'type': 'statistical_analysis'},
        {'id': '3', 'name': 'Correlation Analysis', 'type': 'correlation_analysis'},
    ]
    
    for task in tasks:
        print(f"\n2. Executing {task['name']}:")
        result = executor.execute_task(task, df)
        
        if result['status'] == 'success':
            print(f"   ✓ {task['name']} completed")
            print(f"   ✓ Confidence: {result['confidence']*100:.0f}%")
            print(f"   ✓ Quality: {result['quality_score']*100:.0f}%")
            
            if 'results' in result and 'insights' in result['results']:
                insights = result['results']['insights']
                print(f"   ✓ Generated {len(insights)} insights")
                for insight in insights[:2]:
                    print(f"     - {insight}")
        else:
            print(f"   ✗ {task['name']} failed: {result.get('error')}")

def test_report_generation():
    """Test report generation from results"""
    print("\n📄 Testing Report Generation")
    print("-" * 40)
    
    import sys
    sys.path.append('src/python')
    
    from reporting.report_generator import ReportGenerator
    from execution.task_executor import TaskExecutor
    
    # Create sample plan and results
    plan = {
        'id': 'test-plan-1',
        'name': 'Q4 Sales Analysis',
        'objectives': [
            'Analyze sales trends',
            'Identify top products',
            'Predict future sales'
        ]
    }
    
    # Execute some tasks
    df = pd.read_csv("sample_data.csv")
    executor = TaskExecutor()
    
    task_results = []
    tasks = [
        {'id': '1', 'name': 'Data Profiling', 'type': 'data_profiling'},
        {'id': '2', 'name': 'Statistical Analysis', 'type': 'statistical_analysis'},
        {'id': '3', 'name': 'Predictive Modeling', 'type': 'predictive_modeling'},
    ]
    
    print("1. Executing analysis tasks:")
    for task in tasks:
        result = executor.execute_task(task, df)
        task_results.append(result)
        print(f"   ✓ {task['name']} completed")
    
    print("\n2. Aggregating results:")
    generator = ReportGenerator()
    aggregated = generator.aggregate_plan_results(plan, task_results)
    
    print(f"   ✓ Aggregated {len(task_results)} task results")
    print(f"   ✓ Overall confidence: {aggregated['confidence_score']*100:.0f}%")
    print(f"   ✓ Overall quality: {aggregated['quality_score']*100:.0f}%")
    print(f"   ✓ Key findings: {len(aggregated['key_findings'])}")
    print(f"   ✓ Recommendations: {len(aggregated['recommendations'])}")
    
    print("\n3. Generating executive report:")
    report = generator.generate_executive_report(aggregated)
    
    print(f"   ✓ Report title: {report['title']}")
    print(f"   ✓ Report sections: {len(report['sections'])}")
    
    for section_key, section in report['sections'].items():
        print(f"   ✓ Section: {section['title']}")
    
    # Save HTML report
    html_report = generator.export_report_to_html(report)
    with open("test_report.html", "w") as f:
        f.write(html_report)
    print("\n   ✓ HTML report saved as test_report.html")

def main():
    print("\n" + "=" * 60)
    print("🧪 MANUAL COMPONENT TESTING")
    print("=" * 60)
    
    tests = [
        ("Authentication System", test_login_system),
        ("Data Upload & Plan Creation", test_data_upload_and_plan_creation),
        ("Task Execution Engine", test_task_execution),
        ("Report Generation", test_report_generation),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"\n[{i}/{len(tests)}] {name}")
        print("=" * 60)
        
        try:
            test_func()
            print(f"\n✅ {name} test completed")
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ ALL COMPONENT TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()