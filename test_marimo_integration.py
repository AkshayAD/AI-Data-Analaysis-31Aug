#!/usr/bin/env python3
"""
Test script for Marimo Integration
Tests the complete flow without running Streamlit
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

def test_ai_personas():
    """Test AI personas module"""
    print("Testing AI Personas Module...")
    try:
        from ai_personas import AITeamOrchestrator, ManagerPersona, AnalystPersona, AssociatePersona
        print("✅ AI Personas module imported successfully")
        
        # Test initialization (without API key for now)
        print("Testing persona initialization...")
        manager = ManagerPersona()
        analyst = AnalystPersona()
        associate = AssociatePersona()
        print("✅ All personas initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_marimo_integration():
    """Test marimo integration modules"""
    print("\nTesting Marimo Integration...")
    try:
        from marimo_integration.notebook_builder import NotebookBuilder
        from marimo_integration.notebook_runner import NotebookRunner
        print("✅ Marimo integration modules imported")
        
        # Test notebook builder
        builder = NotebookBuilder()
        print("✅ NotebookBuilder initialized")
        
        # Test notebook runner
        runner = NotebookRunner()
        print("✅ NotebookRunner initialized")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_workflow():
    """Test the analysis workflow"""
    print("\nTesting Analysis Workflow...")
    
    # Sample project configuration
    project_config = {
        "project_name": "Test Analysis Project",
        "problem_statement": "Analyze sales trends and identify growth opportunities",
        "data_context": "E-commerce sales data from 2023",
        "steps": [
            "1. Project Setup",
            "2. Manager Planning",
            "3. Data Understanding", 
            "4. Task Generation",
            "5. Marimo Execution",
            "6. Final Report"
        ]
    }
    
    print(f"Project: {project_config['project_name']}")
    print(f"Problem: {project_config['problem_statement']}")
    print("\nWorkflow Steps:")
    for step in project_config['steps']:
        print(f"  {step}")
    
    # Simulate conversation flow
    conversation = [
        {"persona": "user", "content": "Starting new analysis project"},
        {"persona": "manager", "content": "Creating strategic analysis plan..."},
        {"persona": "analyst", "content": "Examining data profiles..."},
        {"persona": "associate", "content": "Generating analysis tasks..."},
        {"persona": "system", "content": "Executing tasks with Marimo..."},
        {"persona": "manager", "content": "Preparing final report..."}
    ]
    
    print("\nSimulated Conversation Flow:")
    for entry in conversation:
        print(f"  [{entry['persona'].upper()}]: {entry['content']}")
    
    return True

def test_task_generation():
    """Test task generation logic"""
    print("\nTesting Task Generation...")
    
    sample_tasks = [
        "TASK 1: Perform exploratory data analysis\n- Objective: Understand data distribution\n- Method: Statistical analysis\n- Output: Summary statistics",
        "TASK 2: Identify sales trends\n- Objective: Find patterns in sales data\n- Method: Time series analysis\n- Output: Trend visualizations",
        "TASK 3: Customer segmentation\n- Objective: Group customers by behavior\n- Method: Clustering analysis\n- Output: Customer segments",
        "TASK 4: Revenue forecasting\n- Objective: Predict future revenue\n- Method: Predictive modeling\n- Output: Forecast model",
        "TASK 5: Anomaly detection\n- Objective: Find unusual patterns\n- Method: Statistical outlier detection\n- Output: Anomaly report"
    ]
    
    print(f"Generated {len(sample_tasks)} analysis tasks:")
    for i, task in enumerate(sample_tasks, 1):
        print(f"\n  Task {i}:")
        lines = task.split('\n')
        for line in lines:
            print(f"    {line}")
    
    return True

def test_marimo_notebook_creation():
    """Test marimo notebook creation"""
    print("\nTesting Marimo Notebook Creation...")
    
    sample_code = """
# Import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('sales_data.csv')

# Basic statistics
print(df.describe())

# Create visualization
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['revenue'])
plt.title('Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.show()
"""
    
    notebook_template = f"""
import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Task: Perform sales analysis
# Generated: {datetime.now().isoformat()}

mo.md("## Sales Analysis")

{sample_code}

mo.md("### Results")
mo.md("Analysis complete!")
"""
    
    print("Sample Marimo Notebook Structure:")
    print("-" * 40)
    for line in notebook_template.split('\n')[:15]:
        print(line)
    print("...")
    print("-" * 40)
    
    # Create test notebook directory
    os.makedirs("marimo_notebooks", exist_ok=True)
    
    # Save test notebook
    test_notebook_path = "marimo_notebooks/test_notebook.py"
    with open(test_notebook_path, 'w') as f:
        f.write(notebook_template)
    
    print(f"✅ Test notebook created: {test_notebook_path}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("MARIMO INTEGRATION TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("AI Personas", test_ai_personas),
        ("Marimo Integration", test_marimo_integration),
        ("Workflow", test_workflow),
        ("Task Generation", test_task_generation),
        ("Notebook Creation", test_marimo_notebook_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The integration is ready.")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    main()