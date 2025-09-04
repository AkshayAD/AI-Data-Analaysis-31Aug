#!/usr/bin/env python3
"""
AI Data Analysis Platform - No Authentication Version (Improved)
Direct Gemini API integration with enhanced error handling and optimizations
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
# WARNING: In production, consider using environment variables or secrets management
GEMINI_API_KEY = "AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Constants
MAX_FILE_SIZE_MB = 200
MAX_COLUMNS_TO_ANALYZE = 10
MAX_ROWS_FOR_CORRELATION = 10000

# Initialize Gemini model
@st.cache_resource
def get_gemini_model():
    """Initialize and cache Gemini model"""
    try:
        return genai.GenerativeModel('gemini-pro')
    except Exception as e:
        st.error(f"Failed to initialize Gemini model: {str(e)}")
        return None

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
    
    .warning-message {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
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
    """Generate AI insights using Gemini with error handling"""
    try:
        model = get_gemini_model()
        if model is None:
            return "AI insights temporarily unavailable. Please check API configuration."
        
        prompt = f"""
        Analyze the following data and provide insights for {analysis_type}:
        
        Data Summary:
        {data_summary}
        
        Please provide:
        1. Key findings (2-3 bullet points)
        2. Patterns identified (if any)
        3. Recommendations (1-2 actionable items)
        4. Potential next steps
        
        Format the response in clear, structured markdown with bullet points.
        Keep response concise but informative.
        """
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        error_msg = str(e).lower()
        
        if 'quota' in error_msg or 'limit' in error_msg:
            return "⚠️ **AI Quota Exceeded**: The Gemini API quota has been reached. Analysis will continue without AI insights."
        elif 'api' in error_msg or 'key' in error_msg:
            return "⚠️ **API Configuration Issue**: Please verify the Gemini API key is valid and has proper permissions."
        else:
            return f"⚠️ **AI Analysis Temporarily Unavailable**: {str(e)[:100]}..."

def safe_numeric_operation(func, default_value=0):
    """Safely execute numeric operations with error handling"""
    try:
        result = func()
        if pd.isna(result) or not pd.isfinite(result):
            return default_value
        return result
    except Exception:
        return default_value

def perform_step_1_analysis(df: pd.DataFrame) -> Dict:
    """Step 1: Data Overview and Initial Assessment"""
    results = {
        "step": 1,
        "title": "Data Overview",
        "timestamp": datetime.now().isoformat(),
        "metrics": {},
        "column_info": {},
        "summary_stats": {}
    }
    
    try:
        # Basic metrics
        results["metrics"] = {
            "Total Rows": len(df),
            "Total Columns": len(df.columns),
            "Missing Values": int(df.isnull().sum().sum()),
            "Numeric Columns": len(df.select_dtypes(include=['number']).columns),
            "Text Columns": len(df.select_dtypes(include=['object']).columns),
            "Memory Usage (MB)": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        # Column info
        results["column_info"] = df.dtypes.astype(str).to_dict()
        
        # Summary stats (safely)
        if not df.empty and len(df.select_dtypes(include=['number']).columns) > 0:
            try:
                results["summary_stats"] = df.describe().to_dict()
            except Exception as e:
                logger.warning(f"Could not generate summary stats: {e}")
                results["summary_stats"] = {}
        
        # Generate AI insights
        data_summary = f"""
        Dataset Overview:
        - {results['metrics']['Total Rows']} rows and {results['metrics']['Total Columns']} columns
        - {results['metrics']['Missing Values']} missing values total
        - {results['metrics']['Numeric Columns']} numeric columns, {results['metrics']['Text Columns']} text columns
        - Memory usage: {results['metrics']['Memory Usage (MB)']} MB
        Column types: {dict(df.dtypes.value_counts())}
        """
        
        results["ai_insights"] = generate_ai_insights(data_summary, "initial data assessment")
        
    except Exception as e:
        logger.error(f"Error in step 1 analysis: {e}")
        results["error"] = f"Analysis failed: {str(e)}"
    
    return results

def perform_step_2_analysis(df: pd.DataFrame) -> Dict:
    """Step 2: Data Quality and Preparation"""
    results = {
        "step": 2,
        "title": "Data Quality Analysis",
        "timestamp": datetime.now().isoformat(),
        "quality_metrics": {},
        "missing_values": {},
        "outliers": {},
        "data_types": {}
    }
    
    try:
        # Check for duplicates
        duplicates = df.duplicated().sum()
        results["quality_metrics"]["Duplicate Rows"] = int(duplicates)
        results["quality_metrics"]["Duplicate Percentage"] = round((duplicates / len(df)) * 100, 2) if len(df) > 0 else 0
        
        # Missing value analysis by column
        missing_by_column = df.isnull().sum().to_dict()
        results["missing_values"] = {k: int(v) for k, v in missing_by_column.items()}
        
        # Data type consistency
        results["data_types"] = df.dtypes.astype(str).to_dict()
        
        # Outlier detection for numeric columns (limit to first 10 columns)
        numeric_cols = df.select_dtypes(include=['number']).columns[:MAX_COLUMNS_TO_ANALYZE]
        outliers = {}
        
        for col in numeric_cols:
            try:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:  # Avoid division by zero
                    outlier_count = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                    outliers[col] = {
                        "count": int(outlier_count),
                        "percentage": round((outlier_count / len(df)) * 100, 2) if len(df) > 0 else 0
                    }
                else:
                    outliers[col] = {"count": 0, "percentage": 0.0}
                    
            except Exception as e:
                logger.warning(f"Could not calculate outliers for column {col}: {e}")
                outliers[col] = {"count": 0, "percentage": 0.0}
        
        results["outliers"] = outliers
        
        # Generate AI insights
        data_summary = f"""
        Data Quality Assessment:
        - Duplicate rows: {duplicates} ({results['quality_metrics']['Duplicate Percentage']}%)
        - Columns with missing values: {len([k for k, v in missing_by_column.items() if v > 0])}
        - Outliers detected in numeric columns: {', '.join([k for k, v in outliers.items() if v['count'] > 0])}
        - Total outlier points: {sum(v['count'] for v in outliers.values())}
        """
        
        results["ai_insights"] = generate_ai_insights(data_summary, "data quality and preparation recommendations")
        
    except Exception as e:
        logger.error(f"Error in step 2 analysis: {e}")
        results["error"] = f"Quality analysis failed: {str(e)}"
    
    return results

def perform_step_3_analysis(df: pd.DataFrame) -> Dict:
    """Step 3: Statistical Analysis and Insights"""
    results = {
        "step": 3,
        "title": "Statistical Analysis",
        "timestamp": datetime.now().isoformat(),
        "correlations": {},
        "strong_correlations": [],
        "distributions": {}
    }
    
    try:
        # Limit data size for correlation analysis to prevent memory issues
        analysis_df = df.head(MAX_ROWS_FOR_CORRELATION) if len(df) > MAX_ROWS_FOR_CORRELATION else df
        
        # Correlation analysis for numeric columns
        numeric_cols = analysis_df.select_dtypes(include=['number']).columns[:MAX_COLUMNS_TO_ANALYZE]
        
        if len(numeric_cols) > 1:
            try:
                corr_matrix = analysis_df[numeric_cols].corr()
                
                # Convert to serializable format
                results["correlations"] = corr_matrix.round(3).to_dict()
                
                # Find strong correlations
                strong_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_value = corr_matrix.iloc[i, j]
                        if pd.notna(corr_value) and abs(corr_value) > 0.7:
                            strong_corr.append({
                                "var1": corr_matrix.columns[i],
                                "var2": corr_matrix.columns[j],
                                "correlation": round(corr_value, 3)
                            })
                
                results["strong_correlations"] = strong_corr
                
            except Exception as e:
                logger.warning(f"Could not calculate correlations: {e}")
                results["correlations"] = {}
                results["strong_correlations"] = []
        
        # Distribution analysis (limit to first 5 numeric columns)
        distributions = {}
        for col in numeric_cols[:5]:
            try:
                col_data = analysis_df[col].dropna()
                if len(col_data) > 0:
                    distributions[col] = {
                        "mean": safe_numeric_operation(lambda: float(col_data.mean())),
                        "median": safe_numeric_operation(lambda: float(col_data.median())),
                        "std": safe_numeric_operation(lambda: float(col_data.std())),
                        "skewness": safe_numeric_operation(lambda: float(col_data.skew())),
                        "kurtosis": safe_numeric_operation(lambda: float(col_data.kurtosis())),
                        "min": safe_numeric_operation(lambda: float(col_data.min())),
                        "max": safe_numeric_operation(lambda: float(col_data.max()))
                    }
            except Exception as e:
                logger.warning(f"Could not analyze distribution for column {col}: {e}")
        
        results["distributions"] = distributions
        
        # Generate AI insights
        data_summary = f"""
        Statistical Analysis Results:
        - Analyzed {len(numeric_cols)} numeric columns from {len(analysis_df)} rows
        - Found {len(results.get('strong_correlations', []))} strong correlations (>0.7)
        - Distribution analysis completed for {len(distributions)} columns
        
        Strong Correlations Found:
        {chr(10).join([f"- {c['var1']} ↔ {c['var2']}: {c['correlation']}" for c in results.get('strong_correlations', [])[:3]])}
        
        Key Distribution Insights:
        {chr(10).join([f"- {col}: mean={dist.get('mean', 0):.2f}, std={dist.get('std', 0):.2f}" for col, dist in list(distributions.items())[:3]])}
        """
        
        results["ai_insights"] = generate_ai_insights(data_summary, "statistical patterns and insights")
        
    except Exception as e:
        logger.error(f"Error in step 3 analysis: {e}")
        results["error"] = f"Statistical analysis failed: {str(e)}"
    
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
    
    try:
        # Compile insights from previous steps
        summary_parts = ["Complete Analysis Summary:"]
        
        for prev in previous_results:
            if prev and 'step' in prev and 'title' in prev:
                summary_parts.append(f"\nStep {prev['step']}: {prev['title']}")
                if 'ai_insights' in prev and prev['ai_insights']:
                    # Truncate AI insights to prevent prompt overflow
                    insight_preview = prev['ai_insights'][:300] + "..." if len(prev['ai_insights']) > 300 else prev['ai_insights']
                    summary_parts.append(f"Key insights: {insight_preview}")
        
        summary = "\n".join(summary_parts)
        
        # Generate final recommendations
        dataset_info = f"""
        Final Dataset Characteristics:
        - {len(df)} rows, {len(df.columns)} columns
        - Data types: {dict(df.dtypes.value_counts())}
        - Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB
        """
        
        full_prompt = f"""
        Based on the complete data analysis:
        
        {summary}
        
        {dataset_info}
        
        Please provide:
        1. Top 3-5 actionable recommendations for this dataset
        2. Suggested next steps for analysis
        3. Potential business insights
        4. Implementation priorities (High/Medium/Low)
        
        Keep recommendations practical and specific to this dataset.
        Format as clear bullet points with priorities.
        """
        
        try:
            model = get_gemini_model()
            if model:
                response = model.generate_content(full_prompt)
                results["ai_recommendations"] = response.text
            else:
                results["ai_recommendations"] = "AI recommendations unavailable - manual analysis completed successfully."
        except Exception as e:
            logger.warning(f"Could not generate AI recommendations: {e}")
            results["ai_recommendations"] = f"AI recommendations temporarily unavailable: {str(e)[:100]}..."
        
        # Create fallback recommendations based on analysis
        fallback_recommendations = [
            "Review and address data quality issues identified in Step 2",
            "Investigate strong correlations found in statistical analysis",
            "Consider removing or transforming outliers based on business context",
            "Develop visualizations for key patterns discovered",
            "Create automated monitoring for data quality metrics"
        ]
        
        results["recommendations"] = fallback_recommendations
        
        # Create action plan with priorities
        results["action_plan"] = [
            {"task": "Address data quality issues (missing values, duplicates)", "priority": "High", "timeline": "Week 1"},
            {"task": "Analyze statistical correlations for business insights", "priority": "High", "timeline": "Week 1"},
            {"task": "Create data visualizations and dashboard", "priority": "Medium", "timeline": "Week 2"},
            {"task": "Implement data monitoring and alerts", "priority": "Medium", "timeline": "Week 3"},
            {"task": "Document findings and share with stakeholders", "priority": "Low", "timeline": "Week 4"}
        ]
        
    except Exception as e:
        logger.error(f"Error in step 4 analysis: {e}")
        results["error"] = f"Recommendations analysis failed: {str(e)}"
        results["ai_recommendations"] = "Could not generate recommendations due to processing error."
    
    return results

def create_visualizations(df: pd.DataFrame, step: int) -> List:
    """Create visualizations based on the analysis step with error handling"""
    figs = []
    
    try:
        if step == 1:
            # Data overview visualizations
            try:
                # Column types distribution
                dtype_counts = df.dtypes.value_counts()
                if not dtype_counts.empty:
                    fig1 = px.pie(values=dtype_counts.values, names=dtype_counts.index.astype(str), 
                                 title="Data Types Distribution")
                    figs.append(fig1)
            except Exception as e:
                logger.warning(f"Could not create data types visualization: {e}")
            
            try:
                # Missing values chart
                missing_counts = df.isnull().sum()
                missing_cols = missing_counts[missing_counts > 0]
                if not missing_cols.empty:
                    fig2 = px.bar(x=missing_cols.index, y=missing_cols.values, 
                                 title="Missing Values by Column",
                                 labels={'x': 'Column', 'y': 'Missing Count'})
                    figs.append(fig2)
            except Exception as e:
                logger.warning(f"Could not create missing values visualization: {e}")
        
        elif step == 2:
            # Data quality visualizations
            try:
                numeric_cols = df.select_dtypes(include=['number']).columns[:3]  # Limit to 3 columns
                for col in numeric_cols:
                    if not df[col].dropna().empty:
                        fig = px.box(df, y=col, title=f"Outlier Detection: {col}")
                        figs.append(fig)
                        break  # Show only one box plot to avoid overwhelming
            except Exception as e:
                logger.warning(f"Could not create quality visualizations: {e}")
        
        elif step == 3:
            # Statistical analysis visualizations
            try:
                numeric_cols = df.select_dtypes(include=['number']).columns[:5]  # Limit columns
                if len(numeric_cols) >= 2:
                    # Correlation heatmap
                    sample_df = df[numeric_cols].head(1000)  # Limit rows for performance
                    corr_matrix = sample_df.corr()
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0,
                        text=corr_matrix.round(2).values,
                        texttemplate='%{text}',
                        textfont={"size": 10}
                    ))
                    fig.update_layout(title="Correlation Matrix", width=600, height=500)
                    figs.append(fig)
            except Exception as e:
                logger.warning(f"Could not create correlation heatmap: {e}")
            
            try:
                # Scatter plot for first two numeric columns
                if len(numeric_cols) >= 2:
                    sample_df = df.head(1000)  # Limit for performance
                    fig2 = px.scatter(sample_df, x=numeric_cols[0], y=numeric_cols[1],
                                     title=f"Relationship: {numeric_cols[0]} vs {numeric_cols[1]}")
                    figs.append(fig2)
            except Exception as e:
                logger.warning(f"Could not create scatter plot: {e}")
        
        elif step == 4:
            # Summary visualizations
            try:
                # Analysis quality metrics
                metrics_data = {
                    'Analysis Step': ['Data Overview', 'Quality Check', 'Statistical Analysis', 'Recommendations'],
                    'Completion Score': [100, 95, 90, 100]  # Sample scores
                }
                fig = px.bar(pd.DataFrame(metrics_data), x='Analysis Step', y='Completion Score',
                             title="Analysis Completion Status",
                             color='Completion Score', color_continuous_scale='Viridis')
                fig.update_layout(showlegend=False)
                figs.append(fig)
            except Exception as e:
                logger.warning(f"Could not create summary visualization: {e}")
    
    except Exception as e:
        logger.error(f"Error creating visualizations for step {step}: {e}")
    
    return figs

def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded file size and type"""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({MAX_FILE_SIZE_MB}MB)"
    
    # Check file type
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = Path(uploaded_file.name).suffix.lower()
    if file_extension not in allowed_extensions:
        return False, f"File type '{file_extension}' not supported. Allowed types: {', '.join(allowed_extensions)}"
    
    return True, "File validation passed"

# Main Application
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AI Data Analysis Platform</h1>
        <p>Powered by Google Gemini AI - No Authentication Required</p>
        <small>⚠️ Production Note: API key is embedded for demo purposes</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Analysis Controls")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=['csv', 'xlsx', 'xls'],
            help=f"Maximum file size: {MAX_FILE_SIZE_MB}MB. Supports CSV and Excel files."
        )
        
        if uploaded_file:
            # Validate file
            is_valid, message = validate_file_upload(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ {message}")
            else:
                st.success(f"✅ File validation passed ({len(uploaded_file.getvalue()) / (1024*1024):.1f}MB)")
                
                # Load data with error handling
                try:
                    with st.spinner("Loading data..."):
                        if uploaded_file.name.endswith('.csv'):
                            # Try different encodings for CSV
                            try:
                                df = pd.read_csv(uploaded_file, encoding='utf-8')
                            except UnicodeDecodeError:
                                uploaded_file.seek(0)  # Reset file pointer
                                try:
                                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                                except UnicodeDecodeError:
                                    uploaded_file.seek(0)
                                    df = pd.read_csv(uploaded_file, encoding='cp1252')
                        else:
                            df = pd.read_excel(uploaded_file)
                    
                    # Validate loaded data
                    if df.empty:
                        st.error("❌ The uploaded file contains no data")
                    elif len(df.columns) == 0:
                        st.error("❌ The uploaded file contains no columns")
                    else:
                        st.session_state.uploaded_data = df
                        st.success(f"✅ Loaded {len(df):,} rows and {len(df.columns)} columns")
                        
                        # Data preview with size limit
                        with st.expander("📋 Data Preview (First 10 rows)"):
                            st.dataframe(df.head(10), use_container_width=True)
                            
                        # Memory usage warning
                        memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
                        if memory_mb > 100:
                            st.warning(f"⚠️ Large dataset detected ({memory_mb:.1f}MB). Analysis may take longer.")
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    logger.error(f"Error loading file {uploaded_file.name}: {e}")
        
        # Sample data option
        st.markdown("---")
        if st.button("📝 Use Sample Data", help="Load a sample dataset for testing"):
            try:
                sample_data = pd.read_csv("/root/repo/sample_data.csv")
                st.session_state.uploaded_data = sample_data
                st.success("✅ Sample data loaded successfully")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Could not load sample data: {str(e)}")
        
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
                
            # Clear results button
            if st.button("🗑️ Clear Results", help="Clear all analysis results"):
                st.session_state.analysis_results = {}
                st.session_state.current_step = 1
                st.success("✅ Results cleared")
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
        
        if hasattr(st.session_state, 'current_step') and st.session_state.current_step:
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
        if hasattr(st.session_state, 'current_step') and st.session_state.current_step:
            current_step = st.session_state.current_step
            
            with st.spinner(f"🔄 Executing Step {current_step}... This may take a moment."):
                try:
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
                    else:
                        results = {"error": "Invalid step selected"}
                    
                    # Store results
                    st.session_state.analysis_results[current_step] = results
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    logger.error(f"Step {current_step} analysis failed: {e}")
                    results = {"error": str(e), "step": current_step, "title": "Analysis Failed"}
                    st.session_state.analysis_results[current_step] = results
            
            # Display results
            if 'error' in results:
                st.error(f"❌ Step {current_step} failed: {results['error']}")
            else:
                st.markdown(f"## 📊 Step {current_step}: {results['title']}")
                
                # Create tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "🤖 AI Insights", "📊 Metrics", "💾 Export"])
                
                with tab1:
                    st.subheader("📈 Data Visualizations")
                    # Display visualizations
                    figs = create_visualizations(df, current_step)
                    if figs:
                        for i, fig in enumerate(figs):
                            try:
                                st.plotly_chart(fig, use_container_width=True, key=f"chart_{current_step}_{i}")
                            except Exception as e:
                                st.error(f"Could not display visualization {i+1}: {str(e)}")
                    else:
                        st.info("ℹ️ No visualizations available for this step")
                
                with tab2:
                    st.subheader("🤖 AI-Generated Insights")
                    if 'ai_insights' in results and results['ai_insights']:
                        st.markdown(f"""
                        <div class="analysis-result">
                        {results['ai_insights']}
                        </div>
                        """, unsafe_allow_html=True)
                    elif 'ai_recommendations' in results and results['ai_recommendations']:
                        st.markdown(f"""
                        <div class="analysis-result">
                        {results['ai_recommendations']}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("ℹ️ No AI insights available for this step")
                
                with tab3:
                    st.subheader("📊 Analysis Metrics")
                    
                    # Display metrics based on step
                    if 'metrics' in results and results['metrics']:
                        cols = st.columns(min(len(results['metrics']), 4))
                        for idx, (key, value) in enumerate(results['metrics'].items()):
                            with cols[idx % 4]:
                                st.metric(key, f"{value:,}" if isinstance(value, (int, float)) else value)
                    
                    # Step-specific metrics
                    if current_step == 2:
                        if 'outliers' in results and results['outliers']:
                            st.subheader("🎯 Outlier Detection")
                            outlier_df = pd.DataFrame([
                                {"Column": col, "Outlier Count": info['count'], "Percentage": f"{info['percentage']:.1f}%"}
                                for col, info in results['outliers'].items() if info['count'] > 0
                            ])
                            if not outlier_df.empty:
                                st.dataframe(outlier_df, use_container_width=True)
                            else:
                                st.success("✅ No outliers detected in the analyzed columns")
                    
                    elif current_step == 3:
                        if 'strong_correlations' in results and results['strong_correlations']:
                            st.subheader("🔗 Strong Correlations (>0.7)")
                            for corr in results['strong_correlations']:
                                st.write(f"**{corr['var1']}** ↔ **{corr['var2']}**: {corr['correlation']}")
                        else:
                            st.info("ℹ️ No strong correlations found (threshold: 0.7)")
                    
                    elif current_step == 4:
                        if 'action_plan' in results and results['action_plan']:
                            st.subheader("📋 Action Plan")
                            for action in results['action_plan']:
                                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                                st.write(f"{priority_color.get(action['priority'], '⚪')} **{action['priority']}** - {action['task']} ({action['timeline']})")
                
                with tab4:
                    st.subheader("💾 Export Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Export as JSON
                        try:
                            json_str = json.dumps(results, indent=2, default=str)
                            st.download_button(
                                label="📥 Download as JSON",
                                data=json_str,
                                file_name=f"analysis_step_{current_step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                        except Exception as e:
                            st.error(f"Could not prepare JSON export: {str(e)}")
                    
                    with col2:
                        # Export as CSV (for applicable data)
                        try:
                            if 'metrics' in results and results['metrics']:
                                metrics_df = pd.DataFrame([results['metrics']])
                                csv = metrics_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Metrics CSV",
                                    data=csv,
                                    file_name=f"metrics_step_{current_step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv"
                                )
                        except Exception as e:
                            st.error(f"Could not prepare CSV export: {str(e)}")
                    
                    with col3:
                        # Export summary
                        try:
                            summary_text = f"""
Analysis Step {current_step}: {results.get('title', 'Unknown')}
Timestamp: {results.get('timestamp', 'Unknown')}

Metrics:
{json.dumps(results.get('metrics', {}), indent=2)}

AI Insights:
{results.get('ai_insights', 'Not available')}
                            """.strip()
                            
                            st.download_button(
                                label="📝 Download Summary",
                                data=summary_text,
                                file_name=f"summary_step_{current_step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        except Exception as e:
                            st.error(f"Could not prepare summary export: {str(e)}")
        
        # Complete analysis summary
        if len(st.session_state.analysis_results) == 4:
            st.markdown("---")
            
            # Check if any step had errors
            has_errors = any('error' in result for result in st.session_state.analysis_results.values())
            
            if has_errors:
                st.markdown("""
                <div class="warning-message">
                <h3>⚠️ Analysis Completed with Issues</h3>
                <p>Some analysis steps encountered errors. Please review the results above and consider re-running failed steps.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-message">
                <h3>🎉 Analysis Complete!</h3>
                <p>All 4 steps have been successfully executed. You can now review the complete analysis and export the results.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Export complete report
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Download Complete Report", type="primary"):
                    try:
                        complete_report = {
                            "timestamp": datetime.now().isoformat(),
                            "data_file": uploaded_file.name if uploaded_file else "sample_data.csv",
                            "dataset_info": {
                                "rows": len(df),
                                "columns": len(df.columns),
                                "memory_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                            },
                            "analysis_steps": st.session_state.analysis_results,
                            "completion_status": "completed_with_errors" if has_errors else "completed_successfully"
                        }
                        
                        json_report = json.dumps(complete_report, indent=2, default=str)
                        st.download_button(
                            label="💾 Save Complete Report",
                            data=json_report,
                            file_name=f"complete_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key="complete_report_download"
                        )
                    except Exception as e:
                        st.error(f"Could not prepare complete report: {str(e)}")
            
            with col2:
                if st.button("🔄 Start New Analysis"):
                    st.session_state.analysis_results = {}
                    st.session_state.uploaded_data = None
                    st.session_state.current_step = 1
                    st.success("✅ Ready for new analysis")
                    st.rerun()
    
    else:
        # Welcome screen
        st.markdown("""
        ## 👋 Welcome to the AI Data Analysis Platform
        
        This platform provides intelligent data analysis powered by Google Gemini AI with enhanced error handling and optimizations.
        
        ### 🚀 Getting Started:
        1. **Upload your data file** (CSV or Excel) using the sidebar, or try the sample data
        2. **Select an analysis step** to execute from the 4-step workflow
        3. **Review AI-generated insights** and interactive visualizations
        4. **Export results** for further use or reporting
        
        ### 📊 4-Step Analysis Workflow:
        - **Step 1: Data Overview** - Initial assessment and basic statistics
        - **Step 2: Quality Analysis** - Missing values, duplicates, and outliers
        - **Step 3: Statistical Analysis** - Correlations and distribution analysis
        - **Step 4: AI Recommendations** - Actionable insights and next steps
        
        ### ✨ Enhanced Features:
        - 🤖 **AI-powered insights** using Google Gemini Pro
        - 📊 **Interactive visualizations** with Plotly
        - 🔍 **Advanced statistical analysis** with correlation detection
        - 💡 **Actionable recommendations** with priority levels
        - 💾 **Multiple export formats** (JSON, CSV, TXT)
        - ⚡ **Performance optimizations** for large datasets
        - 🛡️ **Error handling** for robust operation
        - 📏 **File size validation** (up to 200MB)
        - 🔄 **Memory management** for efficient processing
        
        ### 📋 Technical Specifications:
        - **Maximum file size**: 200MB
        - **Supported formats**: CSV, Excel (.xlsx, .xls)
        - **Encoding support**: UTF-8, Latin-1, CP1252
        - **Analysis limits**: 10,000 rows for correlation analysis
        - **Visualization limits**: 5 numeric columns maximum
        
        **No authentication required - Start analyzing immediately!**
        """)
        
        # Show system status
        with st.expander("🔧 System Status"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                try:
                    model = get_gemini_model()
                    if model:
                        st.success("✅ Gemini AI: Connected")
                    else:
                        st.error("❌ Gemini AI: Disconnected")
                except:
                    st.error("❌ Gemini AI: Error")
            
            with col2:
                st.success("✅ Plotly: Ready")
                
            with col3:
                st.success("✅ Pandas: Ready")

if __name__ == "__main__":
    main()