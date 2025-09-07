#!/usr/bin/env python3
"""
Working AI Analysis Platform with Real Gemini Integration
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import google.generativeai as genai
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# Configure Streamlit
st.set_page_config(
    page_title="AI Analysis Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'business_objective' not in st.session_state:
        st.session_state.business_objective = ""
    if 'generated_plan' not in st.session_state:
        st.session_state.generated_plan = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'data_insights' not in st.session_state:
        st.session_state.data_insights = ""
    if 'api_status' not in st.session_state:
        st.session_state.api_status = None  # None, 'connected', 'failed'
    if 'api_status_message' not in st.session_state:
        st.session_state.api_status_message = ""
    if 'api_error_details' not in st.session_state:
        st.session_state.api_error_details = ""

def render_sidebar():
    """Render sidebar with navigation"""
    with st.sidebar:
        st.title("🚀 AI Analysis Platform")
        st.divider()
        
        # Stage Navigation
        st.subheader("Navigation")
        stages = [
            "📝 Input & Objectives",
            "🎯 Plan Generation", 
            "📊 Data Understanding"
        ]
        
        for i, stage in enumerate(stages):
            if st.button(stage, key=f"nav_{i}", use_container_width=True):
                st.session_state.current_stage = i
                st.rerun()
        
        # Current stage indicator
        st.divider()
        st.info(f"Current Stage: {stages[st.session_state.current_stage]}")
        
        # System Status
        st.divider()
        st.subheader("System Status")
        
        # API Connection Status
        if st.session_state.api_status == 'connected':
            st.success("✅ API Connected")
        elif st.session_state.api_status == 'failed':
            st.error("❌ API Failed")
        elif st.session_state.api_key:
            st.info("ℹ️ API Not Tested")
        else:
            st.warning("⚠️ No API Key")
        
        # Data Upload Status
        if st.session_state.uploaded_data is not None:
            df = st.session_state.uploaded_data
            st.success("✅ Data Uploaded")
            st.caption(f"{len(df)} rows × {len(df.columns)} cols")
        else:
            st.warning("⚠️ No Data")

def render_stage_0():
    """Stage 0: Input & Objectives"""
    st.header("📝 Stage 0: Input & Objectives")
    st.markdown("Configure your AI analysis settings and upload data")
    
    # API Configuration
    with st.expander("🔑 Gemini API Configuration", expanded=True):
        # Display persistent connection status
        if st.session_state.api_status == 'connected':
            st.success(f"✅ Connected - {st.session_state.api_status_message}")
        elif st.session_state.api_status == 'failed':
            st.error(f"❌ Failed - {st.session_state.api_status_message}")
            if st.session_state.api_error_details:
                st.caption(f"Error details: {st.session_state.api_error_details}")
        elif st.session_state.api_key:
            st.info("ℹ️ API key entered but not tested")
        else:
            st.warning("⚠️ No API key configured")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.api_key,
                type="password",
                placeholder="Enter your Gemini API key"
            )
            st.session_state.api_key = api_key
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Test Connection", type="primary"):
                if api_key:
                    with st.spinner("Testing connection..."):
                        try:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content("Say 'Connected!'")
                            
                            # Update session state for persistence
                            st.session_state.api_status = 'connected'
                            st.session_state.api_status_message = "API Connected Successfully"
                            st.session_state.api_error_details = ""
                            
                            # Force rerun to show updated status
                            st.rerun()
                            
                        except Exception as e:
                            # Update session state for persistence
                            st.session_state.api_status = 'failed'
                            st.session_state.api_status_message = "Connection failed"
                            
                            # Store detailed error for display
                            error_msg = str(e)
                            if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
                                st.session_state.api_error_details = "Invalid API key. Please check your key and try again."
                            elif "quota" in error_msg.lower():
                                st.session_state.api_error_details = "API quota exceeded. Please try again later."
                            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                                st.session_state.api_error_details = "Network error. Please check your internet connection."
                            else:
                                st.session_state.api_error_details = error_msg[:200]  # Limit error message length
                            
                            # Force rerun to show updated status
                            st.rerun()
                else:
                    st.session_state.api_status = 'failed'
                    st.session_state.api_status_message = "No API key provided"
                    st.session_state.api_error_details = "Please enter an API key before testing the connection."
                    st.rerun()
        
        # Model Selection
        model_choice = st.selectbox(
            "Select Model",
            ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
            index=0
        )
        st.session_state.model_choice = model_choice
    
    # File Upload
    with st.expander("📁 Data Upload", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv', 'xlsx'],
            help="Upload your data file for analysis"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_data = df
                st.success(f"✅ Uploaded: {uploaded_file.name} ({len(df)} rows, {len(df.columns)} columns)")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Basic stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    st.metric("Numeric Cols", len(df.select_dtypes(include=[np.number]).columns))
                with col4:
                    st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    # Business Objective
    with st.expander("🎯 Business Objective", expanded=True):
        objective = st.text_area(
            "What is your analysis objective?",
            value=st.session_state.business_objective,
            height=100,
            placeholder="Describe what insights you want to extract from your data..."
        )
        st.session_state.business_objective = objective
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if st.button("Next: Plan Generation →", type="primary", use_container_width=True):
            if not st.session_state.api_key:
                st.error("Please configure your API key first")
            elif st.session_state.uploaded_data is None:
                st.error("Please upload data first")
            elif not st.session_state.business_objective:
                st.error("Please enter your business objective")
            else:
                st.session_state.current_stage = 1
                st.rerun()

def render_stage_1():
    """Stage 1: Plan Generation"""
    st.header("🎯 Stage 1: Plan Generation")
    st.markdown("Generate and refine your analysis plan with AI assistance")
    
    # Check prerequisites
    if not st.session_state.api_key or st.session_state.uploaded_data is None:
        st.error("Please complete Stage 0 first")
        if st.button("← Back to Input & Objectives"):
            st.session_state.current_stage = 0
            st.rerun()
        return
    
    # Plan Generation
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Analysis Plan")
        
        # Generate Plan button
        if st.button("🤖 Generate AI Plan", type="primary"):
            with st.spinner("Generating plan..."):
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    # Create prompt with data info
                    df = st.session_state.uploaded_data
                    data_info = f"""
                    Data Overview:
                    - Rows: {len(df)}
                    - Columns: {', '.join(df.columns.tolist())}
                    - Data types: {df.dtypes.to_dict()}
                    - Sample: {df.head(3).to_string()}
                    
                    Business Objective: {st.session_state.business_objective}
                    """
                    
                    prompt = f"""Create a detailed data analysis plan for the following:
                    {data_info}
                    
                    Provide:
                    1. Key analysis steps
                    2. Recommended visualizations
                    3. Statistical methods to apply
                    4. Expected insights
                    """
                    
                    response = model.generate_content(prompt)
                    st.session_state.generated_plan = response.text
                    
                except Exception as e:
                    st.error(f"Error generating plan: {str(e)}")
        
        # Plan Editor
        plan_text = st.text_area(
            "Edit Analysis Plan",
            value=st.session_state.generated_plan,
            height=400,
            help="You can edit the generated plan"
        )
        st.session_state.generated_plan = plan_text
        
        # Save button
        if st.button("💾 Save Plan"):
            st.success("✅ Plan saved successfully!")
    
    with col2:
        st.subheader("💬 AI Assistant")
        
        # Chat interface
        chat_container = st.container()
        
        # Chat input
        user_input = st.text_input("Ask a question about your analysis:", key="chat_input")
        
        if st.button("Send", type="primary") and user_input:
            try:
                genai.configure(api_key=st.session_state.api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                context = f"""
                Data columns: {st.session_state.uploaded_data.columns.tolist()}
                Objective: {st.session_state.business_objective}
                Current plan: {st.session_state.generated_plan[:500]}
                Question: {user_input}
                """
                
                response = model.generate_content(context)
                st.session_state.chat_history.append({"user": user_input, "ai": response.text})
                
            except Exception as e:
                st.error(f"Chat error: {str(e)}")
        
        # Display chat history
        with chat_container:
            for chat in st.session_state.chat_history[-5:]:  # Show last 5 messages
                st.info(f"You: {chat['user']}")
                st.success(f"AI: {chat['ai']}")
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Input", use_container_width=True):
            st.session_state.current_stage = 0
            st.rerun()
    with col3:
        if st.button("Next: Data Understanding →", type="primary", use_container_width=True):
            st.session_state.current_stage = 2
            st.rerun()

def render_stage_2():
    """Stage 2: Data Understanding"""
    st.header("📊 Stage 2: Data Understanding")
    st.markdown("Explore and understand your data with AI-powered insights")
    
    # Check prerequisites
    if st.session_state.uploaded_data is None:
        st.error("Please upload data first")
        if st.button("← Back to Input & Objectives"):
            st.session_state.current_stage = 0
            st.rerun()
        return
    
    df = st.session_state.uploaded_data
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Overview", "📊 Statistics", "🔍 Quality", "📉 Visualizations", "💡 AI Insights"])
    
    with tab1:
        st.subheader("Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        with col4:
            st.metric("Duplicates", df.duplicated().sum())
        
        # Data preview
        st.subheader("Data Sample")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Column info
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes,
            'Non-Null': df.count(),
            'Null': df.isnull().sum(),
            'Unique': df.nunique()
        })
        st.dataframe(col_info, use_container_width=True)
    
    with tab2:
        st.subheader("Statistical Summary")
        
        # Numeric columns stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.write("**Numeric Columns Statistics**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                st.subheader("Correlation Matrix")
                corr = df[numeric_cols].corr()
                fig = px.imshow(corr, text_auto=True, aspect="auto",
                              title="Correlation Heatmap")
                st.plotly_chart(fig, use_container_width=True)
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.write("**Categorical Columns**")
            for col in categorical_cols[:5]:  # Show first 5
                st.write(f"**{col}** - Unique values: {df[col].nunique()}")
                value_counts = df[col].value_counts().head(10)
                st.bar_chart(value_counts)
    
    with tab3:
        st.subheader("Data Quality Assessment")
        
        # Missing values analysis
        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing Count': df.isnull().sum(),
            'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
        
        if len(missing_df) > 0:
            st.write("**Missing Values**")
            st.dataframe(missing_df, use_container_width=True)
            
            # Visualization
            fig = px.bar(missing_df, x='Column', y='Missing %', 
                        title="Missing Values by Column")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No missing values detected!")
        
        # Outliers detection for numeric columns
        if len(numeric_cols) > 0:
            st.write("**Outlier Detection (IQR Method)**")
            outlier_info = []
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
                if len(outliers) > 0:
                    outlier_info.append({
                        'Column': col,
                        'Outliers': len(outliers),
                        'Percentage': f"{len(outliers)/len(df)*100:.2f}%"
                    })
            
            if outlier_info:
                st.dataframe(pd.DataFrame(outlier_info), use_container_width=True)
            else:
                st.info("No significant outliers detected")
    
    with tab4:
        st.subheader("Data Visualizations")
        
        if len(numeric_cols) > 0:
            # Distribution plots
            st.write("**Distribution Plots**")
            selected_col = st.selectbox("Select column for distribution", numeric_cols)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.histogram(df, x=selected_col, nbins=30,
                                  title=f"Distribution of {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.box(df, y=selected_col, 
                            title=f"Box Plot of {selected_col}")
                st.plotly_chart(fig, use_container_width=True)
            
            # Scatter plot
            if len(numeric_cols) > 1:
                st.write("**Scatter Plot**")
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
                
                fig = px.scatter(df, x=x_col, y=y_col, 
                               title=f"{x_col} vs {y_col}")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.subheader("AI-Powered Insights")
        
        if st.button("🤖 Generate AI Insights", type="primary"):
            with st.spinner("Analyzing data..."):
                try:
                    genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel('gemini-pro')
                    
                    # Prepare data summary
                    data_summary = f"""
                    Dataset Overview:
                    - Shape: {df.shape}
                    - Columns: {', '.join(df.columns.tolist())}
                    - Numeric columns statistics:
                    {df.describe().to_string()}
                    
                    Missing values: {df.isnull().sum().to_dict()}
                    
                    Business Objective: {st.session_state.business_objective}
                    
                    Provide key insights, patterns, and recommendations based on this data.
                    """
                    
                    response = model.generate_content(data_summary)
                    st.session_state.data_insights = response.text
                    
                except Exception as e:
                    st.error(f"Error generating insights: {str(e)}")
        
        if st.session_state.data_insights:
            st.markdown(st.session_state.data_insights)
    
    # Export functionality
    st.divider()
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # Export processed data
        csv = df.to_csv(index=False)
        st.download_button(
            "📊 Download Data (CSV)",
            csv,
            "processed_data.csv",
            "text/csv"
        )
    
    with col2:
        # Export report
        report = f"""
# Data Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Dataset Overview
- Rows: {len(df)}
- Columns: {len(df.columns)}

## Business Objective
{st.session_state.business_objective}

## Analysis Plan
{st.session_state.generated_plan}

## AI Insights
{st.session_state.data_insights}
"""
        st.download_button(
            "📝 Download Report",
            report,
            "analysis_report.md",
            "text/markdown"
        )
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Back to Plan Generation", use_container_width=True):
            st.session_state.current_stage = 1
            st.rerun()

def main():
    """Main application"""
    init_session_state()
    render_sidebar()
    
    # Render current stage
    if st.session_state.current_stage == 0:
        render_stage_0()
    elif st.session_state.current_stage == 1:
        render_stage_1()
    elif st.session_state.current_stage == 2:
        render_stage_2()

if __name__ == "__main__":
    main()