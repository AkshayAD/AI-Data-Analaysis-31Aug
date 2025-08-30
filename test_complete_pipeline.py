#!/usr/bin/env python3
"""
Complete End-to-End Pipeline Test
Testing the entire system with a realistic customer analytics scenario
"""

import sys
import json
from pathlib import Path
import subprocess
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from agents import (
    AgentOrchestrator,
    Task,
    DataAnalysisAgent,
    VisualizationAgent,
    MLAgent
)
from marimo_integration import NotebookBuilder, NotebookRunner


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def run_complete_pipeline():
    """Run the complete customer analytics pipeline"""
    
    print_section("COMPLETE END-TO-END PIPELINE TEST")
    print("Scenario: Customer Lifetime Value Prediction & Analytics")
    
    # Initialize orchestrator and agents
    print("\n1. Initializing agents...")
    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("visualization", VisualizationAgent())
    orchestrator.register_agent("ml", MLAgent())
    print("   ✓ Agents registered: data_analysis, visualization, ml")
    
    # Define data path
    data_path = str(Path(__file__).parent / "data" / "sample" / "customer_purchases.csv")
    print(f"   ✓ Using data: {data_path}")
    
    # Define complete workflow
    print("\n2. Defining workflow tasks...")
    tasks = [
        # Step 1: Initial data analysis
        Task(
            id="initial_analysis",
            type="analyze",
            data={
                "type": "analyze",
                "data_path": data_path
            },
            agent_type="data_analysis",
            dependencies=[]
        ),
        
        # Step 2: Data summary
        Task(
            id="data_summary",
            type="summary",
            data={
                "type": "summary",
                "data_path": data_path
            },
            agent_type="data_analysis",
            dependencies=[]
        ),
        
        # Step 3: Clean data
        Task(
            id="clean_data",
            type="clean",
            data={
                "type": "clean",
                "data_path": data_path,
                "output_path": "/tmp/cleaned_customers.csv"
            },
            agent_type="data_analysis",
            dependencies=["initial_analysis"]
        ),
        
        # Step 4: AutoML to find best model
        Task(
            id="automl",
            type="auto_ml",
            data={
                "ml_task": "auto_ml",
                "data_path": "/tmp/cleaned_customers.csv",
                "target_column": "customer_lifetime_value"
            },
            agent_type="ml",
            dependencies=["clean_data"]
        ),
        
        # Step 5: Train best model
        Task(
            id="train_model",
            type="train",
            data={
                "ml_task": "train",
                "data_path": "/tmp/cleaned_customers.csv",
                "target_column": "customer_lifetime_value",
                "model_type": "auto"
            },
            agent_type="ml",
            dependencies=["automl"]
        ),
        
        # Step 6: Create visualizations
        Task(
            id="create_visualizations",
            type="auto",
            data={
                "viz_type": "auto",
                "data_path": "/tmp/cleaned_customers.csv"
            },
            agent_type="visualization",
            dependencies=["clean_data"]
        ),
        
        # Step 7: Create dashboard
        Task(
            id="create_dashboard",
            type="dashboard",
            data={
                "viz_type": "dashboard",
                "data_path": "/tmp/cleaned_customers.csv"
            },
            agent_type="visualization",
            dependencies=["train_model", "create_visualizations"]
        )
    ]
    
    print(f"   ✓ Defined {len(tasks)} tasks with dependencies")
    
    # Execute workflow
    print("\n3. Executing workflow...")
    start_time = time.time()
    results = orchestrator.execute_workflow(tasks)
    execution_time = time.time() - start_time
    
    # Print results for each task
    print_section("EXECUTION RESULTS")
    
    for task in tasks:
        task_result = results['task_results'][task.id]
        if 'error' in task_result:
            print(f"\n❌ Task: {task.id}")
            print(f"   Error: {task_result['error']}")
        else:
            print(f"\n✅ Task: {task.id}")
            
            # Print specific results based on task type
            if task.id == "initial_analysis":
                analysis = task_result.get('analysis', {})
                print(f"   - Data shape: {analysis.get('shape')}")
                print(f"   - Columns: {len(analysis.get('columns', []))}")
                print(f"   - Missing values: {sum(analysis.get('missing_values', {}).values())}")
                
            elif task.id == "data_summary":
                summary = task_result.get('summary', {})
                print(f"   - Total rows: {summary.get('rows')}")
                print(f"   - Memory usage: {summary.get('memory_usage', 0):.2f} MB")
                
            elif task.id == "clean_data":
                print(f"   - Original shape: {task_result.get('original_shape')}")
                print(f"   - Cleaned shape: {task_result.get('cleaned_shape')}")
                print(f"   - Rows removed: {task_result.get('rows_removed')}")
                
            elif task.id == "automl":
                if 'results' in task_result:
                    print(f"   - Models tested: {task_result.get('models_tested')}")
                    print(f"   - Best model: {task_result.get('best_model')}")
                    print(f"   - Best R² score: {task_result.get('best_score', 0):.3f}")
                    
            elif task.id == "train_model":
                print(f"   - Model type: {task_result.get('model_type')}")
                metrics = task_result.get('metrics', {})
                if 'r2' in metrics:
                    print(f"   - R² score: {metrics['r2']:.3f}")
                if 'mse' in metrics:
                    print(f"   - MSE: {metrics['mse']:.2f}")
                    
            elif task.id in ["create_visualizations", "create_dashboard"]:
                if 'notebook_path' in task_result:
                    print(f"   - Generated: {task_result['notebook_path']}")
                elif 'visualization_path' in task_result:
                    print(f"   - Generated: {task_result['visualization_path']}")
                elif 'dashboard_path' in task_result:
                    print(f"   - Generated: {task_result['dashboard_path']}")
    
    # Summary
    print_section("WORKFLOW SUMMARY")
    summary = results['summary']
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success rate: {summary['success_rate']*100:.0f}%")
    print(f"Execution time: {execution_time:.2f} seconds")
    
    # Test generated notebooks
    print_section("TESTING GENERATED NOTEBOOKS")
    
    # Find generated notebooks
    notebook_dir = Path("marimo_notebooks")
    notebooks = list(notebook_dir.glob("*.py"))
    print(f"Found {len(notebooks)} generated notebooks")
    
    # Test if notebooks have valid syntax
    for notebook in notebooks[-3:]:  # Test last 3 notebooks
        print(f"\nTesting: {notebook.name}")
        
        # Check Python syntax
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(notebook)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"   ✓ Valid Python syntax")
            
            # Check if it's a valid Marimo notebook
            with open(notebook) as f:
                content = f.read()
                if "import marimo as mo" in content and "@app.cell" in content:
                    print(f"   ✓ Valid Marimo structure")
                else:
                    print(f"   ✗ Invalid Marimo structure")
        else:
            print(f"   ✗ Syntax error: {result.stderr}")
    
    # Create final integrated notebook
    print_section("CREATING INTEGRATED ANALYSIS NOTEBOOK")
    
    builder = NotebookBuilder()
    builder.add_markdown("# Customer Lifetime Value Analysis")
    builder.add_markdown("## Complete Pipeline Results")
    builder.add_import("import pandas as pd")
    builder.add_import("import numpy as np")
    builder.add_import("import matplotlib.pyplot as plt")
    builder.add_import("import seaborn as sns")
    
    # Add data loading
    builder.add_cell("""
import pandas as pd
df = pd.read_csv('/tmp/cleaned_customers.csv')
print(f"Loaded {len(df)} customer records")
df.head()
#RETURN: df""")
    
    # Add statistics
    builder.add_cell("""
# Summary statistics
summary = df.describe()
print("Key metrics:")
print(f"Average CLV: ${df['customer_lifetime_value'].mean():.2f}")
print(f"Average orders: {df['total_orders'].mean():.1f}")
print(f"Average age: {df['age'].mean():.1f} years")
summary
#RETURN: summary""")
    
    # Add correlation analysis
    builder.add_cell("""
# Correlation analysis
plt.figure(figsize=(10, 8))
numeric_cols = df.select_dtypes(include=[np.number]).columns
correlation = df[numeric_cols].corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f')
plt.title('Feature Correlation Matrix')
plt.tight_layout()
plt.show()""")
    
    # Add CLV distribution
    builder.add_cell("""
# Customer Lifetime Value Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
axes[0].hist(df['customer_lifetime_value'], bins=20, edgecolor='black', alpha=0.7)
axes[0].set_xlabel('Customer Lifetime Value ($)')
axes[0].set_ylabel('Number of Customers')
axes[0].set_title('CLV Distribution')
axes[0].grid(True, alpha=0.3)

# Box plot by age group
df['age_group'] = pd.cut(df['age'], bins=[0, 30, 40, 50, 100], labels=['<30', '30-40', '40-50', '50+'])
df.boxplot(column='customer_lifetime_value', by='age_group', ax=axes[1])
axes[1].set_xlabel('Age Group')
axes[1].set_ylabel('Customer Lifetime Value ($)')
axes[1].set_title('CLV by Age Group')

plt.suptitle('')
plt.tight_layout()
plt.show()""")
    
    # Save integrated notebook
    integrated_path = Path("marimo_notebooks/integrated_analysis.py")
    builder.save(integrated_path)
    print(f"Created integrated notebook: {integrated_path}")
    
    # Final status
    print_section("PIPELINE TEST COMPLETE")
    
    if summary['success_rate'] == 1.0:
        print("🎉 SUCCESS: All pipeline stages completed successfully!")
        print("\nWhat was tested:")
        print("✓ Data loading and analysis")
        print("✓ Data cleaning")
        print("✓ Multiple ML models (AutoML)")
        print("✓ Model training and evaluation")
        print("✓ Visualization generation")
        print("✓ Dashboard creation")
        print("✓ Notebook generation and validation")
        print("\nThe system successfully processed customer data through")
        print("a complete analytics pipeline with 7 coordinated tasks!")
    else:
        print("⚠️  Some tasks failed. Review the results above.")
    
    return results


if __name__ == "__main__":
    try:
        results = run_complete_pipeline()
        
        # Return success/failure
        if results['summary']['success_rate'] == 1.0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)