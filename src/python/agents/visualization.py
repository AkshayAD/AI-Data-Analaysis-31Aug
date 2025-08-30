"""
Phase 2: Visualization Agent
Creates various types of visualizations from data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

from .base import BaseAgent, AgentConfig
from marimo_integration import NotebookBuilder


class VisualizationAgent(BaseAgent):
    """Agent for creating data visualizations"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                name="VisualizationAgent",
                description="Creates data visualizations and charts"
            )
        super().__init__(config)
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute visualization task"""
        viz_type = task.get('viz_type', 'auto')
        
        if viz_type == 'auto':
            return self._auto_visualize(task)
        elif viz_type == 'dashboard':
            return self._create_dashboard(task)
        elif viz_type == 'report':
            return self._create_report(task)
        else:
            return self._create_specific_viz(task, viz_type)
    
    def _auto_visualize(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically choose and create appropriate visualizations"""
        data_path = task.get('data_path')
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = pd.read_csv(data_path)
            
            # Analyze data to determine best visualizations
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            builder = NotebookBuilder()
            builder.add_markdown("# Auto-Generated Visualizations")
            builder.add_import("import matplotlib.pyplot as plt")
            builder.add_import("import seaborn as sns")
            builder.add_data_load("df", data_path)
            
            # Create appropriate visualizations
            visualizations_created = []
            
            # Correlation heatmap for numeric columns
            if len(numeric_cols) > 1:
                builder.add_cell("""
import seaborn as sns
plt.figure(figsize=(10, 8))
correlation = df[%s].corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.show()
""" % str(numeric_cols))
                visualizations_created.append("correlation_heatmap")
            
            # Distribution plots for numeric columns
            for col in numeric_cols[:3]:  # Limit to first 3
                builder.add_cell(f"""
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.hist(df['{col}'], bins=30, edgecolor='black')
plt.title('Histogram: {col}')
plt.xlabel('{col}')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
df.boxplot(column='{col}')
plt.title('Box Plot: {col}')
plt.tight_layout()
plt.show()
""")
                visualizations_created.append(f"distribution_{col}")
            
            # Bar plots for categorical columns
            for col in categorical_cols[:2]:  # Limit to first 2
                builder.add_cell(f"""
plt.figure(figsize=(10, 6))
df['{col}'].value_counts().plot(kind='bar')
plt.title('Count by {col}')
plt.xlabel('{col}')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")
                visualizations_created.append(f"bar_{col}")
            
            # Time series if date column exists
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols and numeric_cols:
                builder.add_cell(f"""
df['{date_cols[0]}'] = pd.to_datetime(df['{date_cols[0]}'])
plt.figure(figsize=(12, 6))
for col in {numeric_cols[:3]}:
    plt.plot(df['{date_cols[0]}'], df[col], label=col, marker='o')
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('Time Series')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
""")
                visualizations_created.append("time_series")
            
            # Save notebook
            notebook_path = Path("marimo_notebooks") / f"auto_viz_{Path(data_path).stem}.py"
            builder.save(notebook_path)
            
            return {
                'success': True,
                'notebook_path': str(notebook_path),
                'visualizations': visualizations_created,
                'data_shape': df.shape,
                'columns_analyzed': {
                    'numeric': numeric_cols,
                    'categorical': categorical_cols
                }
            }
            
        except Exception as e:
            self.logger.error(f"Auto visualization failed: {e}")
            return {'error': str(e)}
    
    def _create_dashboard(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create an interactive dashboard"""
        data_path = task.get('data_path')
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = pd.read_csv(data_path)
            
            # Create Plotly-based dashboard notebook
            builder = NotebookBuilder()
            builder.add_markdown("# Interactive Dashboard")
            builder.add_import("import plotly.express as px")
            builder.add_import("import plotly.graph_objects as go")
            builder.add_import("from plotly.subplots import make_subplots")
            builder.add_data_load("df", data_path)
            
            # Add interactive plots
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                builder.add_cell(f"""
# Interactive scatter plot
fig = px.scatter(df, x='{numeric_cols[0]}', y='{numeric_cols[1]}', 
                 title='Interactive Scatter Plot')
fig.show()
""")
            
            # Save dashboard notebook
            notebook_path = Path("marimo_notebooks") / f"dashboard_{Path(data_path).stem}.py"
            builder.save(notebook_path)
            
            return {
                'success': True,
                'dashboard_path': str(notebook_path),
                'type': 'interactive_dashboard'
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard creation failed: {e}")
            return {'error': str(e)}
    
    def _create_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive report with visualizations"""
        data_path = task.get('data_path')
        analysis_results = task.get('analysis_results', {})
        
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = pd.read_csv(data_path)
            
            builder = NotebookBuilder()
            builder.add_markdown(f"# Data Analysis Report")
            builder.add_markdown(f"## Dataset: {Path(data_path).name}")
            builder.add_import("import matplotlib.pyplot as plt")
            builder.add_import("import seaborn as sns")
            builder.add_data_load("df", data_path)
            
            # Add summary statistics
            builder.add_markdown("## Summary Statistics")
            builder.add_cell("df.describe()")
            
            # Add visualizations based on analysis
            builder.add_markdown("## Data Visualizations")
            
            # Distribution of numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols[:3]:
                builder.add_cell(f"""
plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
df['{col}'].hist(bins=30, edgecolor='black')
plt.title('Distribution of {col}')
plt.subplot(1, 3, 2)
df.boxplot(column='{col}')
plt.title('Box Plot')
plt.subplot(1, 3, 3)
df['{col}'].plot(kind='density')
plt.title('Density Plot')
plt.tight_layout()
plt.show()
""")
            
            # Save report
            report_path = Path("marimo_notebooks") / f"report_{Path(data_path).stem}.py"
            builder.save(report_path)
            
            return {
                'success': True,
                'report_path': str(report_path),
                'type': 'analysis_report'
            }
            
        except Exception as e:
            self.logger.error(f"Report creation failed: {e}")
            return {'error': str(e)}
    
    def _create_specific_viz(self, task: Dict[str, Any], viz_type: str) -> Dict[str, Any]:
        """Create a specific type of visualization"""
        data_path = task.get('data_path')
        columns = task.get('columns', [])
        
        if not data_path:
            return {'error': 'No data_path provided'}
        
        try:
            df = pd.read_csv(data_path)
            
            builder = NotebookBuilder()
            builder.add_markdown(f"# {viz_type.title()} Visualization")
            builder.add_data_load("df", data_path)
            
            if viz_type == 'scatter' and len(columns) >= 2:
                builder.add_plot("df", plot_type="scatter", x=columns[0], y=columns[1])
            elif viz_type == 'histogram' and columns:
                builder.add_plot("df", plot_type="histogram", column=columns[0])
            elif viz_type == 'heatmap':
                numeric_df = df.select_dtypes(include=[np.number])
                builder.add_cell("""
import seaborn as sns
plt.figure(figsize=(10, 8))
sns.heatmap(df.select_dtypes(include=[np.number]).corr(), annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()
""")
            else:
                return {'error': f'Unsupported visualization type: {viz_type}'}
            
            # Save visualization
            viz_path = Path("marimo_notebooks") / f"{viz_type}_{Path(data_path).stem}.py"
            builder.save(viz_path)
            
            return {
                'success': True,
                'visualization_path': str(viz_path),
                'type': viz_type
            }
            
        except Exception as e:
            self.logger.error(f"Visualization creation failed: {e}")
            return {'error': str(e)}