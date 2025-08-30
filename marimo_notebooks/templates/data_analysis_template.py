#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Marimo Data Analysis Template
This template provides a reactive notebook structure for data analysis tasks
that can be orchestrated by AI agents.
"""

import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional
import json

# ============================================================================
# AGENT PARAMETERS CELL
# This cell receives parameters from the orchestrating agent
# ============================================================================

agent_params = mo.ui.dictionary({
    "data_source": mo.ui.text(value="", label="Data Source Path"),
    "analysis_type": mo.ui.dropdown(
        options=["descriptive", "diagnostic", "predictive", "prescriptive"],
        value="descriptive",
        label="Analysis Type"
    ),
    "target_variable": mo.ui.text(value="", label="Target Variable (if applicable)"),
    "groupby_columns": mo.ui.text(value="", label="Group By Columns (comma-separated)"),
    "filters": mo.ui.text_area(value="{}", label="Filters (JSON format)"),
    "output_format": mo.ui.dropdown(
        options=["json", "html", "markdown", "excel"],
        value="json",
        label="Output Format"
    )
})

mo.md(f"""
# Data Analysis Notebook

**Agent ID:** {mo.state.get("agent_id", "manual")}  
**Task ID:** {mo.state.get("task_id", "none")}  
**Template:** Data Analysis

## Configuration
{agent_params}
""")

# ============================================================================
# DATA LOADING CELL
# Loads data based on agent parameters
# ============================================================================

@mo.cell
def load_data(params=agent_params.value):
    """Load data from specified source"""
    
    data_source = params.get("data_source", "")
    
    if not data_source:
        return mo.md("⚠️ No data source specified"), None
    
    try:
        # Support multiple file formats
        if data_source.endswith('.csv'):
            df = pd.read_csv(data_source)
        elif data_source.endswith('.parquet'):
            df = pd.read_parquet(data_source)
        elif data_source.endswith('.json'):
            df = pd.read_json(data_source)
        elif data_source.endswith('.xlsx') or data_source.endswith('.xls'):
            df = pd.read_excel(data_source)
        else:
            # Try to read as CSV by default
            df = pd.read_csv(data_source)
        
        # Apply filters if specified
        filters_str = params.get("filters", "{}")
        if filters_str and filters_str != "{}":
            filters = json.loads(filters_str)
            for column, condition in filters.items():
                if column in df.columns:
                    if isinstance(condition, dict):
                        # Complex filter (e.g., {"operator": ">", "value": 100})
                        op = condition.get("operator", "==")
                        val = condition.get("value")
                        if op == ">":
                            df = df[df[column] > val]
                        elif op == "<":
                            df = df[df[column] < val]
                        elif op == ">=":
                            df = df[df[column] >= val]
                        elif op == "<=":
                            df = df[df[column] <= val]
                        elif op == "==":
                            df = df[df[column] == val]
                        elif op == "!=":
                            df = df[df[column] != val]
                        elif op == "in":
                            df = df[df[column].isin(val)]
                    else:
                        # Simple filter
                        df = df[df[column] == condition]
        
        info_md = mo.md(f"""
        ### Data Loaded Successfully ✅
        - **Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns
        - **Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB
        - **Data Types:** {dict(df.dtypes.value_counts())}
        """)
        
        return info_md, df
        
    except Exception as e:
        error_md = mo.md(f"""
        ### Error Loading Data ❌
        **Error:** {str(e)}
        """)
        return error_md, None

data_info, df = load_data()
data_info

# ============================================================================
# DATA PROFILING CELL
# Generates comprehensive data profile
# ============================================================================

@mo.cell
def profile_data(df):
    """Generate data profile"""
    
    if df is None:
        return mo.md("No data to profile")
    
    profile = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": df.dtypes.to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "missing_percentage": (df.isnull().sum() / len(df) * 100).to_dict(),
        "unique_values": df.nunique().to_dict(),
        "numeric_summary": {},
        "categorical_summary": {}
    }
    
    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        profile["numeric_summary"] = df[numeric_cols].describe().to_dict()
    
    # Categorical columns summary
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols[:10]:  # Limit to first 10 categorical columns
        value_counts = df[col].value_counts().head(10)
        profile["categorical_summary"][col] = value_counts.to_dict()
    
    # Create visual summary
    summary_md = mo.md(f"""
    ## Data Profile
    
    ### Overview
    - **Total Records:** {profile['shape'][0]:,}
    - **Total Features:** {profile['shape'][1]}
    - **Numeric Features:** {len(numeric_cols)}
    - **Categorical Features:** {len(categorical_cols)}
    
    ### Missing Data
    {pd.DataFrame({
        'Column': profile['missing_values'].keys(),
        'Missing Count': profile['missing_values'].values(),
        'Missing %': [f"{v:.1f}%" for v in profile['missing_percentage'].values()]
    }).to_markdown() if any(profile['missing_values'].values()) else "No missing values ✅"}
    
    ### Unique Values
    {pd.DataFrame({
        'Column': profile['unique_values'].keys(),
        'Unique Count': profile['unique_values'].values(),
        'Cardinality': [f"{v/profile['shape'][0]*100:.1f}%" for v in profile['unique_values'].values()]
    }).head(10).to_markdown()}
    """)
    
    return summary_md, profile

profile_summary, data_profile = profile_data(df)
profile_summary

# ============================================================================
# ANALYSIS CELL
# Performs analysis based on specified type
# ============================================================================

@mo.cell
def perform_analysis(df, params=agent_params.value):
    """Perform specified analysis type"""
    
    if df is None:
        return mo.md("No data to analyze"), None
    
    analysis_type = params.get("analysis_type", "descriptive")
    target_variable = params.get("target_variable", "")
    groupby_columns = params.get("groupby_columns", "")
    
    results = {
        "analysis_type": analysis_type,
        "timestamp": pd.Timestamp.now().isoformat(),
        "findings": {}
    }
    
    # Descriptive Analysis
    if analysis_type == "descriptive":
        # Basic statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        results["findings"]["summary_statistics"] = df[numeric_cols].describe().to_dict()
        
        # Correlation matrix
        if len(numeric_cols) > 1:
            results["findings"]["correlations"] = df[numeric_cols].corr().to_dict()
        
        # Group by analysis if specified
        if groupby_columns:
            groups = [col.strip() for col in groupby_columns.split(",") if col.strip() in df.columns]
            if groups:
                grouped_stats = df.groupby(groups)[numeric_cols].agg(['mean', 'sum', 'count'])
                results["findings"]["grouped_statistics"] = grouped_stats.to_dict()
    
    # Diagnostic Analysis
    elif analysis_type == "diagnostic":
        if target_variable and target_variable in df.columns:
            # Analyze relationships with target
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            correlations_with_target = {}
            
            for col in numeric_cols:
                if col != target_variable:
                    corr = df[col].corr(df[target_variable])
                    correlations_with_target[col] = corr
            
            results["findings"]["target_correlations"] = correlations_with_target
            
            # Feature importance (simplified)
            sorted_corrs = sorted(correlations_with_target.items(), 
                                key=lambda x: abs(x[1]), 
                                reverse=True)
            results["findings"]["top_features"] = dict(sorted_corrs[:10])
    
    # Predictive Analysis (placeholder for agent to inject ML code)
    elif analysis_type == "predictive":
        results["findings"]["message"] = "Predictive analysis requires ML agent collaboration"
        # Agent can inject specific predictive modeling code here
    
    # Prescriptive Analysis (placeholder for optimization)
    elif analysis_type == "prescriptive":
        results["findings"]["message"] = "Prescriptive analysis requires optimization agent"
        # Agent can inject optimization code here
    
    # Create results display
    results_md = mo.md(f"""
    ## Analysis Results
    
    **Type:** {analysis_type.title()} Analysis  
    **Timestamp:** {results['timestamp']}
    
    ### Key Findings
    {json.dumps(results['findings'], indent=2, default=str)[:1000]}...
    """)
    
    return results_md, results

analysis_display, analysis_results = perform_analysis(df)
analysis_display

# ============================================================================
# VISUALIZATION CELL
# Creates visualizations based on data and analysis
# ============================================================================

@mo.cell
def create_visualizations(df, analysis_results):
    """Create relevant visualizations"""
    
    if df is None:
        return mo.md("No data to visualize"), None
    
    figs = []
    
    # Create figure with subplots
    numeric_cols = df.select_dtypes(include=[np.number]).columns[:6]  # Limit to 6 columns
    
    if len(numeric_cols) > 0:
        # Distribution plots
        fig1, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(numeric_cols):
            if idx < 6:
                axes[idx].hist(df[col].dropna(), bins=30, edgecolor='black', alpha=0.7)
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
                axes[idx].grid(True, alpha=0.3)
        
        # Hide unused subplots
        for idx in range(len(numeric_cols), 6):
            axes[idx].set_visible(False)
        
        plt.suptitle('Feature Distributions', fontsize=16, y=1.02)
        plt.tight_layout()
        figs.append(fig1)
        
        # Correlation heatmap
        if len(numeric_cols) > 1:
            fig2, ax = plt.subplots(figsize=(10, 8))
            corr_matrix = df[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, square=True, ax=ax)
            ax.set_title('Correlation Heatmap', fontsize=16, pad=20)
            plt.tight_layout()
            figs.append(fig2)
    
    # Create display
    viz_md = mo.md(f"""
    ## Visualizations
    
    Generated {len(figs)} visualization(s) based on the data analysis.
    """)
    
    return viz_md, figs

viz_display, figures = create_visualizations(df, analysis_results)
viz_display

# Display figures
if figures:
    for fig in figures:
        mo.output(fig)
        plt.close(fig)

# ============================================================================
# EXPORT CELL
# Exports results in specified format
# ============================================================================

@mo.cell
def export_results(df, analysis_results, params=agent_params.value):
    """Export results in specified format"""
    
    output_format = params.get("output_format", "json")
    
    export_data = {
        "metadata": {
            "agent_id": mo.state.get("agent_id", "manual"),
            "task_id": mo.state.get("task_id", "none"),
            "timestamp": pd.Timestamp.now().isoformat(),
            "data_shape": df.shape if df is not None else None
        },
        "parameters": params,
        "analysis_results": analysis_results,
        "data_profile": data_profile if 'data_profile' in locals() else None
    }
    
    # Format based on output type
    if output_format == "json":
        output = json.dumps(export_data, indent=2, default=str)
        mo.state["export_output"] = output
        display = mo.md(f"""
        ### Export Ready (JSON)
        ```json
        {output[:500]}...
        ```
        """)
    
    elif output_format == "html":
        # Create HTML report
        html_content = f"""
        <html>
        <head><title>Analysis Report</title></head>
        <body>
            <h1>Data Analysis Report</h1>
            <h2>Metadata</h2>
            <pre>{json.dumps(export_data['metadata'], indent=2)}</pre>
            <h2>Results</h2>
            <pre>{json.dumps(export_data['analysis_results'], indent=2, default=str)}</pre>
        </body>
        </html>
        """
        mo.state["export_output"] = html_content
        display = mo.md("### Export Ready (HTML)")
    
    elif output_format == "markdown":
        # Create Markdown report
        md_content = f"""
# Data Analysis Report

## Metadata
- Agent ID: {export_data['metadata']['agent_id']}
- Task ID: {export_data['metadata']['task_id']}
- Timestamp: {export_data['metadata']['timestamp']}

## Analysis Results
{json.dumps(export_data['analysis_results'], indent=2, default=str)}
        """
        mo.state["export_output"] = md_content
        display = mo.md(md_content)
    
    else:
        display = mo.md("### Export format not yet implemented")
    
    return display

export_display = export_results(df, analysis_results)
export_display

# ============================================================================
# FINAL OUTPUT CELL
# Provides final output to the agent
# ============================================================================

mo.md("""
## Analysis Complete ✅

The analysis has been completed successfully. Results are available in the specified output format and can be accessed by the orchestrating agent through the notebook state.

**Next Steps:**
- Agent can retrieve results from `mo.state["export_output"]`
- Additional analysis can be triggered by updating parameters
- Notebook can be saved for reproducibility
""")

# Make results available to agent
mo.state["analysis_complete"] = True
mo.state["final_results"] = {
    "success": True,
    "data_shape": df.shape if df is not None else None,
    "analysis_type": agent_params.value.get("analysis_type"),
    "results": analysis_results,
    "export_ready": True
}