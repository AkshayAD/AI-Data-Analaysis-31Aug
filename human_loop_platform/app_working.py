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
import time
import traceback
from typing import Optional, Dict, Any

# Configure Streamlit
st.set_page_config(
    page_title="AI Analysis Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def categorize_error(error: Exception) -> Dict[str, Any]:
    """Categorize error and provide user-friendly message"""
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    # Categorize by error type and content
    if "api_key_invalid" in error_str or "invalid api key" in error_str or "unauthorized" in error_str:
        return {
            "category": "authentication",
            "message": "Invalid API key",
            "details": "The API key provided is invalid or has been revoked. Please check your key and try again.",
            "action": "Get a valid API key from https://makersuite.google.com/app/apikey",
            "recoverable": False
        }
    elif "quota" in error_str or "rate limit" in error_str or "429" in error_str:
        return {
            "category": "rate_limit",
            "message": "API quota exceeded",
            "details": "You've exceeded the API rate limit. Please wait a moment before trying again.",
            "action": "Wait 60 seconds before retrying, or upgrade your API plan",
            "recoverable": True
        }
    elif "timeout" in error_str or "timed out" in error_str:
        return {
            "category": "timeout",
            "message": "Request timed out",
            "details": "The API request took too long to respond. This might be due to network issues or server load.",
            "action": "Check your internet connection and try again",
            "recoverable": True
        }
    elif "network" in error_str or "connection" in error_str or "unable to connect" in error_str:
        return {
            "category": "network",
            "message": "Network error",
            "details": "Unable to connect to the API. Please check your internet connection.",
            "action": "Verify your internet connection is stable",
            "recoverable": True
        }
    elif "content" in error_str and ("policy" in error_str or "safety" in error_str):
        return {
            "category": "content_policy",
            "message": "Content policy violation",
            "details": "The content may violate the API's usage policies.",
            "action": "Review and modify your content to comply with usage policies",
            "recoverable": False
        }
    elif "model" in error_str and "not found" in error_str:
        return {
            "category": "model",
            "message": "Model not available",
            "details": "The requested model is not available or doesn't exist.",
            "action": "Use a different model like 'gemini-pro' or 'gemini-1.5-pro'",
            "recoverable": False
        }
    else:
        return {
            "category": "unknown",
            "message": "Unexpected error",
            "details": f"An unexpected error occurred: {error_str[:200]}",
            "action": "Try again or contact support if the issue persists",
            "recoverable": True
        }

def retry_api_call(func, *args, max_retries: int = 3, delay: float = 1.0, **kwargs):
    """Retry API calls with exponential backoff"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_info = categorize_error(e)
            
            # Don't retry if not recoverable
            if not error_info["recoverable"]:
                raise e
            
            # Exponential backoff
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                time.sleep(wait_time)
                continue
            else:
                raise e
    
    raise last_error

def handle_api_error(error: Exception, operation: str = "API operation") -> None:
    """Handle API errors with user-friendly messages"""
    error_info = categorize_error(error)
    
    # Update session state
    st.session_state.api_retry_count = st.session_state.get('api_retry_count', 0) + 1
    st.session_state.last_error_time = datetime.now()
    
    # Display error to user
    with st.container():
        st.error(f"❌ {operation} failed: {error_info['message']}")
        
        with st.expander("📋 Error Details", expanded=False):
            st.write(f"**What happened:** {error_info['details']}")
            st.write(f"**What to do:** {error_info['action']}")
            st.write(f"**Error category:** {error_info['category']}")
            
            if st.session_state.api_retry_count > 1:
                st.warning(f"This error has occurred {st.session_state.api_retry_count} times")
            
            # Show technical details in debug mode
            if st.checkbox("Show technical details", key=f"debug_{operation}"):
                st.code(f"Error type: {type(error).__name__}\nFull error: {str(error)}\n\nTraceback:\n{traceback.format_exc()}")

def safe_api_configure(api_key: str) -> bool:
    """Safely configure the API with error handling"""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        handle_api_error(e, "API configuration")
        return False

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
    if 'api_retry_count' not in st.session_state:
        st.session_state.api_retry_count = 0
    if 'last_error_time' not in st.session_state:
        st.session_state.last_error_time = None

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
                            # Reset retry count for new test
                            st.session_state.api_retry_count = 0
                            
                            # Use retry logic for connection test
                            def test_connection():
                                genai.configure(api_key=api_key)
                                model = genai.GenerativeModel('gemini-pro')
                                return model.generate_content("Say 'Connected!'")
                            
                            response = retry_api_call(test_connection, max_retries=3, delay=1.0)
                            
                            # Update session state for persistence
                            st.session_state.api_status = 'connected'
                            st.session_state.api_status_message = "API Connected Successfully"
                            st.session_state.api_error_details = ""
                            
                            # Force rerun to show updated status
                            st.rerun()
                            
                        except Exception as e:
                            # Categorize the error
                            error_info = categorize_error(e)
                            
                            # Update session state for persistence
                            st.session_state.api_status = 'failed'
                            st.session_state.api_status_message = error_info['message']
                            st.session_state.api_error_details = f"{error_info['details']} | Action: {error_info['action']}"
                            
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
                # Attempt to read the file with appropriate method
                if uploaded_file.name.endswith('.csv'):
                    # Try different encodings for CSV files
                    try:
                        df = pd.read_csv(uploaded_file)
                    except UnicodeDecodeError:
                        uploaded_file.seek(0)  # Reset file pointer
                        df = pd.read_csv(uploaded_file, encoding='latin-1')
                    except pd.errors.EmptyDataError:
                        raise ValueError("The CSV file appears to be empty. Please upload a file with data.")
                else:
                    # Handle Excel files
                    try:
                        df = pd.read_excel(uploaded_file)
                    except Exception as excel_error:
                        if "openpyxl" in str(excel_error).lower():
                            raise ValueError("Excel file reading requires openpyxl. Please ensure the file is a valid Excel file.")
                        raise excel_error
                
                # Validate the dataframe
                if df.empty:
                    raise ValueError("The uploaded file contains no data. Please upload a file with data.")
                
                if len(df.columns) == 0:
                    raise ValueError("The uploaded file has no columns. Please check the file format.")
                
                # Store successfully loaded data
                st.session_state.uploaded_data = df
                st.success(f"✅ Uploaded: {uploaded_file.name} ({len(df)} rows, {len(df.columns)} columns)")
                
                # Show preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)
                
                # Basic stats with error handling
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows", len(df))
                with col2:
                    st.metric("Columns", len(df.columns))
                with col3:
                    numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
                    st.metric("Numeric Cols", numeric_cols)
                with col4:
                    memory_kb = df.memory_usage(deep=True).sum() / 1024
                    if memory_kb < 1024:
                        st.metric("Memory", f"{memory_kb:.1f} KB")
                    else:
                        st.metric("Memory", f"{memory_kb/1024:.1f} MB")
                
            except ValueError as ve:
                st.error(f"❌ File Error: {str(ve)}")
                st.session_state.uploaded_data = None
            except Exception as e:
                error_msg = str(e)
                if "codec" in error_msg.lower() or "decode" in error_msg.lower():
                    st.error("❌ File encoding error. Try saving the file as UTF-8 or use a different format.")
                elif "permission" in error_msg.lower():
                    st.error("❌ Permission denied. Please check file permissions.")
                elif "memory" in error_msg.lower():
                    st.error("❌ File too large. Please upload a smaller file or sample of your data.")
                else:
                    st.error(f"❌ Error loading file: {error_msg[:200]}")
                    with st.expander("Technical Details"):
                        st.code(traceback.format_exc())
                st.session_state.uploaded_data = None
    
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
                    # Reset retry count
                    st.session_state.api_retry_count = 0
                    
                    # Validate prerequisites
                    if not st.session_state.api_key:
                        raise ValueError("No API key configured. Please add your API key in Stage 0.")
                    
                    if st.session_state.uploaded_data is None:
                        raise ValueError("No data uploaded. Please upload data in Stage 0.")
                    
                    if not st.session_state.business_objective:
                        raise ValueError("No business objective specified. Please add your objective in Stage 0.")
                    
                    # Create plan generation function for retry
                    def generate_plan():
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
                        
                        return model.generate_content(prompt)
                    
                    # Execute with retry logic
                    response = retry_api_call(generate_plan, max_retries=3, delay=2.0)
                    st.session_state.generated_plan = response.text
                    st.success("✅ Plan generated successfully!")
                    
                except ValueError as ve:
                    # Handle validation errors
                    st.error(f"❌ Validation Error: {str(ve)}")
                except Exception as e:
                    # Handle API errors with detailed information
                    handle_api_error(e, "Plan generation")
        
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
            with st.spinner("Processing your question..."):
                try:
                    # Reset retry count
                    st.session_state.api_retry_count = 0
                    
                    # Validate prerequisites
                    if not st.session_state.api_key:
                        raise ValueError("No API key configured. Please configure API in Stage 0.")
                    
                    if st.session_state.uploaded_data is None:
                        raise ValueError("No data available for context. Please upload data first.")
                    
                    # Create chat function for retry
                    def process_chat():
                        genai.configure(api_key=st.session_state.api_key)
                        model = genai.GenerativeModel('gemini-pro')
                        
                        context = f"""
                        Data columns: {st.session_state.uploaded_data.columns.tolist()}
                        Objective: {st.session_state.business_objective}
                        Current plan: {st.session_state.generated_plan[:500] if st.session_state.generated_plan else 'No plan generated yet'}
                        Question: {user_input}
                        """
                        
                        return model.generate_content(context)
                    
                    # Execute with retry logic
                    response = retry_api_call(process_chat, max_retries=3, delay=2.0)
                    st.session_state.chat_history.append({"user": user_input, "ai": response.text})
                    
                    # Force refresh to show new message
                    st.rerun()
                    
                except ValueError as ve:
                    st.error(f"❌ Validation Error: {str(ve)}")
                except Exception as e:
                    handle_api_error(e, "Chat processing")
        
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
                    # Reset retry count
                    st.session_state.api_retry_count = 0
                    
                    # Validate prerequisites
                    if not st.session_state.api_key:
                        raise ValueError("No API key configured. Please configure API in Stage 0.")
                    
                    # Create insights function for retry
                    def generate_insights():
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
                        
                        Business Objective: {st.session_state.business_objective if st.session_state.business_objective else 'General data analysis'}
                        
                        Provide key insights, patterns, and recommendations based on this data.
                        """
                        
                        return model.generate_content(data_summary)
                    
                    # Execute with retry logic
                    response = retry_api_call(generate_insights, max_retries=3, delay=2.0)
                    st.session_state.data_insights = response.text
                    st.success("✅ Insights generated successfully!")
                    
                except ValueError as ve:
                    st.error(f"❌ Validation Error: {str(ve)}")
                except Exception as e:
                    handle_api_error(e, "AI insights generation")
        
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