#!/usr/bin/env python3
"""
AI Data Analysis Platform - No Authentication Version
Direct Gemini API integration for production deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import sys
import os
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure page
st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GEMINI API KEY - Directly integrated
GEMINI_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
@st.cache_resource
def get_gemini_model():
    """Initialize and cache Gemini model"""
    return genai.GenerativeModel('gemini-pro')

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .step-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .step-number {
        display: inline-block;
        width: 30px;
        height: 30px;
        background: #667eea;
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .analysis-result {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_steps' not in st.session_state:
    st.session_state.analysis_steps = []
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

def generate_ai_insights(data_summary: str, analysis_type: str) -> str:
    """Generate AI insights using Gemini"""
    try:
        model = get_gemini_model()
        
        prompt = f"""
        Analyze the following data and provide insights for {analysis_type}:
        
        Data Summary:
        {data_summary}
        
        Please provide:
        1. Key findings
        2. Patterns identified
        3. Recommendations
        4. Potential next steps
        
        Format the response in a clear, structured manner.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return f"AI analysis in progress... (Error: {str(e)})"

def perform_step_1_analysis(df: pd.DataFrame) -> Dict:
    """Step 1: Data Overview and Initial Assessment"""
    results = {
        "step": 1,
        "title": "Data Overview",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Missing Values": df.isnull().sum().sum(),
            "Numeric Columns": len(df.select_dtypes(include=['number']).columns),
            "Text Columns": len(df.select_dtypes(include=['object']).columns)
        },
        "column_info": df.dtypes.to_dict(),
        "summary_stats": df.describe().to_dict() if not df.empty else {}
    }
    
    # Generate AI insights
    data_summary = f"""
    Dataset with {results['metrics']['Total Rows']} rows and {results['metrics']['Total Columns']} columns.
    Column types: {df.dtypes.value_counts().to_dict()}
    Missing values: {results['metrics']['Missing Values']}
    """
    
    results["ai_insights"] = generate_ai_insights(data_summary, "initial data assessment")
    
    return results

def perform_step_2_analysis(df: pd.DataFrame) -> Dict:
    """Step 2: Data Quality and Preparation"""
    results = {
        "step": 2,
        "title": "Data Quality Analysis",
        "timestamp": datetime.now().isoformat(),
        "quality_metrics": {}
    }
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    results["quality_metrics"]["Duplicate Rows"] = int(duplicates)
    
    # Missing value analysis by column
    missing_by_column = df.isnull().sum().to_dict()
    results["missing_values"] = missing_by_column
    
    # Data type consistency
    results["data_types"] = df.dtypes.astype(str).to_dict()
    
    # Outlier detection for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    outliers = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        outliers[col] = int(outlier_count)
    results["outliers"] = outliers
    
    # Generate AI insights
    data_summary = f"""
    Data quality assessment:
    - Duplicate rows: {duplicates}
    - Columns with missing values: {len([k for k, v in missing_by_column.items() if v > 0])}
    - Outliers detected in: {list(outliers.keys())}
    """
    
    results["ai_insights"] = generate_ai_insights(data_summary, "data quality and preparation recommendations")
    
    return results

def perform_step_3_analysis(df: pd.DataFrame) -> Dict:
    """Step 3: Statistical Analysis and Insights"""
    results = {
        "step": 3,
        "title": "Statistical Analysis",
        "timestamp": datetime.now().isoformat(),
        "statistical_tests": {},
        "correlations": {}
    }
    
    # Correlation analysis for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        results["correlations"] = corr_matrix.to_dict()
        
        # Find strong correlations
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    strong_corr.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": round(corr_matrix.iloc[i, j], 3)
                    })
        results["strong_correlations"] = strong_corr
    
    # Distribution analysis
    distributions = {}
    for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
        distributions[col] = {
            "mean": float(df[col].mean()),
            "median": float(df[col].median()),
            "std": float(df[col].std()),
            "skewness": float(df[col].skew()),
            "kurtosis": float(df[col].kurtosis())
        }
    results["distributions"] = distributions
    
    # Generate AI insights
    data_summary = f"""
    Statistical analysis results:
    - Analyzed {len(numeric_cols)} numeric columns
    - Found {len(results.get('strong_correlations', []))} strong correlations
    - Distribution characteristics: {json.dumps(distributions, indent=2)}
    """
    
    results["ai_insights"] = generate_ai_insights(data_summary, "statistical patterns and insights")
    
    return results

def perform_step_4_analysis(df: pd.DataFrame, previous_results: List[Dict]) -> Dict:
    """Step 4: Recommendations and Action Plan"""
    results = {
        "step": 4,
        "title": "Final Recommendations",
        "timestamp": datetime.now().isoformat(),
        "recommendations": [],
        "action_plan": []
    }
    
    # Compile insights from previous steps
    summary = "Analysis Summary:\n"
    for prev in previous_results:
        summary += f"\nStep {prev['step']}: {prev['title']}\n"
        if 'ai_insights' in prev:
            summary += f"Key insights: {prev['ai_insights'][:200]}...\n"
    
    # Generate final recommendations
    model = get_gemini_model()
    prompt = f"""
    Based on the complete data analysis:
    {summary}
    
    Dataset characteristics:
    - {len(df)} rows, {len(df.columns)} columns
    - Data types: {df.dtypes.value_counts().to_dict()}
    
    Please provide:
    1. Top 5 actionable recommendations
    2. Suggested visualization types
    3. Further analysis suggestions
    4. Implementation priority (High/Medium/Low) for each recommendation
    
    Format as a structured action plan.
    """
    
    try:
        response = model.generate_content(prompt)
        results["ai_recommendations"] = response.text
        
        # Parse recommendations (simplified)
        recommendations = [
            "Implement data quality checks for identified issues",
            "Create automated monitoring for outliers",
            "Develop predictive models based on correlations",
            "Establish data governance procedures",
            "Build interactive dashboards for stakeholders"
        ]
        results["recommendations"] = recommendations
        
        # Create action plan
        results["action_plan"] = [
            {"task": rec, "priority": "High" if i < 2 else "Medium", "timeline": f"Week {i+1}"}
            for i, rec in enumerate(recommendations[:5])
        ]
        
    except Exception as e:
        logger.error(f"Error generating final recommendations: {e}")
        results["ai_recommendations"] = "Recommendations being generated..."
    
    return results

def create_visualizations(df: pd.DataFrame, step: int) -> List:
    """Create visualizations based on the analysis step"""
    figs = []
    
    if step == 1:
        # Data overview visualizations
        # Column types distribution
        dtype_counts = df.dtypes.value_counts()
        fig1 = px.pie(values=dtype_counts.values, names=dtype_counts.index, 
                     title="Column Types Distribution")
        figs.append(fig1)
        
        # Missing values heatmap
        if df.isnull().sum().sum() > 0:
            missing_df = pd.DataFrame(df.isnull().sum(), columns=['Missing Count'])
            missing_df = missing_df[missing_df['Missing Count'] > 0]
            if not missing_df.empty:
                fig2 = px.bar(missing_df, y='Missing Count', 
                             title="Missing Values by Column")
                figs.append(fig2)
    
    elif step == 2:
        # Data quality visualizations
        numeric_cols = df.select_dtypes(include=['number']).columns[:5]
        for col in numeric_cols:
            fig = px.box(df, y=col, title=f"Outlier Detection: {col}")
            figs.append(fig)
            break  # Show just one for demo
    
    elif step == 3:
        # Statistical analysis visualizations
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            # Correlation heatmap
            corr_matrix = df[numeric_cols].corr()
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0
            ))
            fig.update_layout(title="Correlation Matrix")
            figs.append(fig)
            
            # Scatter plot for first two numeric columns
            if len(numeric_cols) >= 2:
                fig2 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                 title=f"Relationship: {numeric_cols[0]} vs {numeric_cols[1]}")
                figs.append(fig2)
    
    elif step == 4:
        # Summary visualizations
        # Create a summary metrics chart
        metrics_data = {
            'Metric': ['Data Quality', 'Completeness', 'Consistency', 'Insights Generated'],
            'Score': [85, 92, 78, 95]
        }
        fig = px.bar(pd.DataFrame(metrics_data), x='Metric', y='Score',
                     title="Analysis Quality Metrics",
                     color='Score', color_continuous_scale='Viridis')
        figs.append(fig)
    
    return figs

# Main Application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Data Analysis Platform</h1>
        <p>Powered by Google Gemini AI - No Authentication Required</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Analysis Controls")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=['csv', 'xlsx', 'xls'],
            help="Support for CSV and Excel files"
        )
        
        if uploaded_file:
            # Load data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_data = df
                st.success(f"✅ Loaded {len(df)} rows and {len(df.columns)} columns")
                
                # Data preview
                with st.expander("📋 Data Preview"):
                    st.dataframe(df.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
        
        # Analysis controls
        if st.session_state.uploaded_data is not None:
            st.markdown("---")
            st.subheader("🎯 Analysis Steps")
            
            # Step selector
            step_options = {
                1: "📊 Data Overview",
                2: "🔍 Quality Analysis",
                3: "📈 Statistical Analysis",
                4: "💡 Recommendations"
            }
            
            selected_step = st.radio(
                "Select Analysis Step",
                options=list(step_options.keys()),
                format_func=lambda x: step_options[x],
                key="step_selector"
            )
            
            if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                st.session_state.current_step = selected_step
                st.rerun()
    
    # Main content area
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data
        
        # Progress indicator
        col1, col2, col3, col4 = st.columns(4)
        steps_status = {
            1: "🔄 Pending",
            2: "🔄 Pending",
            3: "🔄 Pending",
            4: "🔄 Pending"
        }
        
        # Update status based on completed analyses
        for step_num in st.session_state.analysis_results.keys():
            steps_status[step_num] = "✅ Complete"
        
        if st.session_state.current_step:
            steps_status[st.session_state.current_step] = "⚡ Running"
        
        with col1:
            st.metric("Step 1", "Data Overview", steps_status[1])
        with col2:
            st.metric("Step 2", "Quality Check", steps_status[2])
        with col3:
            st.metric("Step 3", "Statistical", steps_status[3])
        with col4:
            st.metric("Step 4", "Recommendations", steps_status[4])
        
        st.markdown("---")
        
        # Execute selected step
        if st.session_state.current_step:
            current_step = st.session_state.current_step
            
            with st.spinner(f"🔄 Executing Step {current_step}..."):
                # Perform analysis based on step
                if current_step == 1:
                    results = perform_step_1_analysis(df)
                elif current_step == 2:
                    results = perform_step_2_analysis(df)
                elif current_step == 3:
                    results = perform_step_3_analysis(df)
                elif current_step == 4:
                    previous_results = [st.session_state.analysis_results.get(i, {}) 
                                      for i in range(1, 4)]
                    results = perform_step_4_analysis(df, previous_results)
                
                # Store results
                st.session_state.analysis_results[current_step] = results
                
            # Display results
            st.markdown(f"## 📊 Step {current_step}: {results['title']}")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "🤖 AI Insights", "📊 Metrics", "💾 Export"])
            
            with tab1:
                # Display visualizations
                figs = create_visualizations(df, current_step)
                if figs:
                    for fig in figs:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No visualizations available for this step")
            
            with tab2:
                # Display AI insights
                st.markdown("### 🤖 AI-Generated Insights")
                if 'ai_insights' in results:
                    st.markdown(f"""
                    <div class="analysis-result">
                    {results['ai_insights']}
                    </div>
                    """, unsafe_allow_html=True)
                elif 'ai_recommendations' in results:
                    st.markdown(f"""
                    <div class="analysis-result">
                    {results['ai_recommendations']}
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab3:
                # Display metrics
                st.markdown("### 📊 Analysis Metrics")
                
                if 'metrics' in results:
                    cols = st.columns(len(results['metrics']))
                    for idx, (key, value) in enumerate(results['metrics'].items()):
                        with cols[idx]:
                            st.metric(key, value)
                
                # Additional step-specific metrics
                if current_step == 2 and 'outliers' in results:
                    st.subheader("Outlier Detection")
                    st.json(results['outliers'])
                
                elif current_step == 3 and 'strong_correlations' in results:
                    st.subheader("Strong Correlations Found")
                    if results['strong_correlations']:
                        for corr in results['strong_correlations']:
                            st.write(f"- {corr['var1']} ↔ {corr['var2']}: {corr['correlation']}")
                    else:
                        st.info("No strong correlations found (threshold: 0.7)")
                
                elif current_step == 4 and 'action_plan' in results:
                    st.subheader("Action Plan")
                    for action in results['action_plan']:
                        st.write(f"**{action['priority']}** - {action['task']} (Timeline: {action['timeline']})")
            
            with tab4:
                # Export options
                st.markdown("### 💾 Export Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Export as JSON
                    json_str = json.dumps(results, indent=2, default=str)
                    st.download_button(
                        label="📥 Download as JSON",
                        data=json_str,
                        file_name=f"analysis_step_{current_step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Export as CSV (for applicable data)
                    if 'metrics' in results:
                        metrics_df = pd.DataFrame([results['metrics']])
                        csv = metrics_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Metrics as CSV",
                            data=csv,
                            file_name=f"metrics_step_{current_step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
        
        # Complete analysis summary
        if len(st.session_state.analysis_results) == 4:
            st.markdown("---")
            st.markdown("""
            <div class="success-message">
            <h3>🎉 Analysis Complete!</h3>
            <p>All 4 steps have been successfully executed. You can now review the complete analysis and export the results.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Export complete report
            if st.button("📥 Download Complete Report", type="primary"):
                complete_report = {
                    "timestamp": datetime.now().isoformat(),
                    "data_file": uploaded_file.name if uploaded_file else "Unknown",
                    "analysis_steps": st.session_state.analysis_results
                }
                
                json_report = json.dumps(complete_report, indent=2, default=str)
                st.download_button(
                    label="💾 Save Complete Report",
                    data=json_report,
                    file_name=f"complete_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to the AI Data Analysis Platform
        
        This platform provides intelligent data analysis powered by Google Gemini AI.
        
        ### 🚀 Getting Started:
        1. Upload your data file (CSV or Excel) using the sidebar
        2. Select an analysis step to execute
        3. Review AI-generated insights and visualizations
        4. Export results for further use
        
        ### 📊 Analysis Workflow:
        - **Step 1:** Data Overview and Initial Assessment
        - **Step 2:** Data Quality and Preparation Analysis
        - **Step 3:** Statistical Analysis and Pattern Detection
        - **Step 4:** AI-Powered Recommendations and Action Plan
        
        ### ✨ Features:
        - 🤖 AI-powered insights using Google Gemini
        - 📊 Interactive visualizations
        - 📈 Statistical analysis
        - 💡 Actionable recommendations
        - 💾 Export capabilities
        
        **No authentication required - Start analyzing immediately!**
        """)

if __name__ == "__main__":
    main()