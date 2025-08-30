#!/usr/bin/env python3
"""
Quick Start Example for AI Data Analysis Team
Demonstrates basic usage of agents and Marimo integration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from agents import DataAnalysisAgent
from marimo_integration import NotebookBuilder, NotebookRunner


def example_data_analysis():
    """Example: Analyze sample sales data"""
    print("=== Data Analysis Example ===")
    
    # Create agent
    agent = DataAnalysisAgent()
    
    # Analyze data
    data_path = Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv"
    
    # Run analysis
    result = agent.execute({
        'type': 'analyze',
        'data_path': str(data_path)
    })
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Data shape: {result['analysis']['shape']}")
    print(f"Columns: {result['analysis']['columns']}")
    print(f"Missing values: {result['analysis']['missing_values']}")
    
    # Get summary
    result = agent.execute({
        'type': 'summary',
        'data_path': str(data_path)
    })
    
    if 'success' in result:
        print(f"Total rows: {result['summary']['rows']}")
        print(f"Total columns: {result['summary']['columns']}")
        print(f"Memory usage: {result['summary']['memory_usage']:.2f} MB")


def example_create_notebook():
    """Example: Create an analysis notebook"""
    print("\n=== Notebook Creation Example ===")
    
    builder = NotebookBuilder()
    
    # Build a simple analysis notebook
    data_path = Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv"
    
    builder.add_markdown("# Sales Data Analysis")
    builder.add_import("import matplotlib.pyplot as plt")
    builder.add_data_load("sales_df", str(data_path))
    
    # Add analysis cells
    builder.add_cell("""
# Group by product and sum revenue
product_revenue = sales_df.groupby('product')['revenue'].sum().sort_values(ascending=False)
product_revenue
""")
    
    builder.add_cell("""
# Create bar chart
plt.figure(figsize=(10, 6))
product_revenue.plot(kind='bar')
plt.title('Total Revenue by Product')
plt.xlabel('Product')
plt.ylabel('Revenue ($)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")
    
    # Save notebook
    notebook_path = Path(__file__).parent.parent / "marimo_notebooks" / "sales_analysis.py"
    notebook_path.parent.mkdir(exist_ok=True)
    builder.save(notebook_path)
    
    print(f"Notebook created: {notebook_path}")
    print(f"Run with: marimo run {notebook_path}")
    
    return notebook_path


def example_agent_with_notebook():
    """Example: Agent creating and running a notebook"""
    print("\n=== Agent + Notebook Integration Example ===")
    
    # Agent analyzes data first
    agent = DataAnalysisAgent()
    data_path = Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv"
    
    result = agent.execute({
        'type': 'analyze',
        'data_path': str(data_path)
    })
    
    if 'error' not in result:
        # Based on analysis, create appropriate notebook
        columns = result['analysis']['columns']
        numeric_cols = [col for col, dtype in result['analysis']['dtypes'].items() 
                        if 'float' in dtype or 'int' in dtype]
        
        print(f"Found numeric columns: {numeric_cols}")
        
        # Create visualization notebook
        builder = NotebookBuilder()
        builder.add_markdown("# Automated Analysis Report")
        builder.add_data_load("df", str(data_path))
        
        # Add histogram for each numeric column
        for col in numeric_cols:
            if col != 'date':  # Skip date columns
                builder.add_plot("df", plot_type="histogram", column=col)
        
        notebook_path = Path(__file__).parent.parent / "marimo_notebooks" / "auto_analysis.py"
        builder.save(notebook_path)
        
        print(f"Auto-generated notebook: {notebook_path}")


if __name__ == "__main__":
    # Run examples
    example_data_analysis()
    notebook_path = example_create_notebook()
    example_agent_with_notebook()
    
    print("\n=== Quick Start Complete ===")
    print("Next steps:")
    print("1. Run the CLI: python src/python/cli.py --help")
    print("2. Try the notebook: marimo run marimo_notebooks/sales_analysis.py")
    print("3. Run tests: pytest tests/")
    print("4. Explore the examples directory")