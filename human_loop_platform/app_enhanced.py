#!/usr/bin/env python3
"""
Enhanced AI Analysis Platform with HITL Features
Improvements: Error handling, retry logic, caching, progress indicators
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import google.generativeai as genai
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import time
from functools import wraps
import hashlib
import asyncio
import websocket
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit
st.set_page_config(
    page_title="AI Analysis Platform - Enhanced",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Retry decorator with exponential backoff
def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries} attempts failed.")
            
            raise last_exception
        return wrapper
    return decorator

# Cache decorator for API responses
@st.cache_data(ttl=3600, show_spinner=False)
def cached_api_call(prompt_hash: str, model_name: str = 'gemini-pro'):
    """Cache API responses for 1 hour"""
    return None  # Will be overridden by actual call

# Initialize session state with enhanced features
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
    if 'api_cache' not in st.session_state:
        st.session_state.api_cache = {}
    if 'confidence_scores' not in st.session_state:
        st.session_state.confidence_scores = {}
    if 'human_feedback' not in st.session_state:
        st.session_state.human_feedback = []
    if 'orchestrator_connected' not in st.session_state:
        st.session_state.orchestrator_connected = False

def render_sidebar():
    """Enhanced sidebar with system monitoring"""
    with st.sidebar:
        st.title("🚀 AI Analysis Platform")
        st.caption("Enhanced with HITL Features")
        st.divider()
        
        # Stage Navigation
        st.subheader("Navigation")
        stages = [
            "📝 Input & Objectives",
            "🎯 Plan Generation", 
            "📊 Data Understanding"
        ]
        
        for i, stage in enumerate(stages):
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(stage, key=f"nav_{i}", use_container_width=True):
                    st.session_state.current_stage = i
                    st.rerun()
            with col2:
                # Stage completion indicator
                if i < st.session_state.current_stage:
                    st.success("✅")
                elif i == st.session_state.current_stage:
                    st.info("🔄")
                else:
                    st.caption("⏳")
        
        # Current stage indicator
        st.divider()
        st.info(f"Current Stage: {stages[st.session_state.current_stage]}")
        
        # System Status with enhanced monitoring
        st.divider()
        st.subheader("System Status")
        
        # API Status
        if st.session_state.api_key:
            st.success("✅ API Key Configured")
            # Show API usage stats
            if 'api_calls' in st.session_state:
                st.caption(f"API Calls: {st.session_state.get('api_calls', 0)}")
                st.caption(f"Cache Hits: {st.session_state.get('cache_hits', 0)}")
        else:
            st.warning("⚠️ API Key Missing")
        
        # Data Status
        if st.session_state.uploaded_data is not None:
            st.success("✅ Data Uploaded")
            st.caption(f"Rows: {len(st.session_state.uploaded_data):,}")
            st.caption(f"Columns: {len(st.session_state.uploaded_data.columns)}")
        else:
            st.warning("⚠️ No Data")
        
        # Orchestrator Status
        if st.session_state.orchestrator_connected:
            st.success("✅ Orchestrator Connected")
        else:
            st.info("ℹ️ Orchestrator Offline")
        
        # Performance Metrics
        st.divider()
        st.subheader("Performance")
        if 'last_api_time' in st.session_state:
            st.metric("Last API Call", f"{st.session_state.last_api_time:.2f}s")
        if 'total_processing_time' in st.session_state:
            st.metric("Total Time", f"{st.session_state.total_processing_time:.1f}s")

@retry_with_backoff(max_retries=3, initial_delay=1)
def safe_api_call(prompt: str, model_name: str = 'gemini-pro') -> Optional[str]:
    """Make API call with retry logic and error handling"""
    start_time = time.time()
    
    try:
        # Generate cache key
        cache_key = hashlib.md5(f"{prompt}{model_name}".encode()).hexdigest()
        
        # Check cache first
        if cache_key in st.session_state.api_cache:
            st.session_state.cache_hits = st.session_state.get('cache_hits', 0) + 1
            logger.info(f"Cache hit for prompt hash: {cache_key}")
            return st.session_state.api_cache[cache_key]
        
        # Configure API
        genai.configure(api_key=st.session_state.api_key)
        model = genai.GenerativeModel(model_name)
        
        # Make API call
        response = model.generate_content(prompt)
        result = response.text
        
        # Cache the response
        st.session_state.api_cache[cache_key] = result
        st.session_state.api_calls = st.session_state.get('api_calls', 0) + 1
        
        # Track timing
        elapsed = time.time() - start_time
        st.session_state.last_api_time = elapsed
        st.session_state.total_processing_time = st.session_state.get('total_processing_time', 0) + elapsed
        
        logger.info(f"API call successful in {elapsed:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        st.error(f"❌ API Error: {str(e)}")
        
        # Provide fallback response
        if "quota" in str(e).lower():
            st.warning("API quota exceeded. Using cached response or fallback.")
            return "API quota exceeded. Please try again later or use a different API key."
        elif "timeout" in str(e).lower():
            st.warning("API timeout. Retrying with shorter prompt...")
            # Try with truncated prompt
            return safe_api_call(prompt[:len(prompt)//2], model_name)
        else:
            raise

def render_stage_0():
    """Enhanced Stage 0 with better error handling and validation"""
    st.header("📝 Stage 0: Input & Objectives")
    st.markdown("Configure your AI analysis settings and upload data")
    
    # Progress indicator
    progress_bar = st.progress(0)
    progress_steps = 0
    total_steps = 3
    
    # API Configuration with enhanced feedback
    with st.expander("🔑 Gemini API Configuration", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            api_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.api_key,
                type="password",
                placeholder="Enter your Gemini API key",
                help="Get your API key from https://makersuite.google.com/app/apikey"
            )
            st.session_state.api_key = api_key
            
            if api_key:
                progress_steps += 1
                progress_bar.progress(progress_steps / total_steps)
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Test Connection", type="primary", disabled=not api_key):
                with st.spinner("Testing connection..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content("Test connection. Reply with 'Connected'.")
                        
                        if response and response.text:
                            st.success("✅ Connected to Gemini API")
                            st.caption(f"Model: gemini-pro")
                            st.session_state.api_tested = True
                        else:
                            st.error("❌ Connection failed: Empty response")
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
                        st.caption("Please check your API key and try again")
    
    # Data Upload with validation
    with st.expander("📁 Data Upload", expanded=True):
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel file (max 200MB)"
        )
        
        if uploaded_file is not None:
            try:
                # Show file info
                file_details = {
                    "Filename": uploaded_file.name,
                    "Size": f"{uploaded_file.size / 1024:.2f} KB",
                    "Type": uploaded_file.type
                }
                st.json(file_details)
                
                # Load data with progress
                with st.spinner(f"Loading {uploaded_file.name}..."):
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.session_state.uploaded_data = df
                    progress_steps += 1
                    progress_bar.progress(progress_steps / total_steps)
                    
                    st.success(f"✅ Loaded {len(df):,} rows and {len(df.columns)} columns")
                    
                    # Data preview with stats
                    st.subheader("Data Preview")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Rows", f"{len(df):,}")
                    with col2:
                        st.metric("Columns", len(df.columns))
                    with col3:
                        st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                    with col4:
                        st.metric("Duplicates", df.duplicated().sum())
                    
                    st.dataframe(df.head(10), use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                st.caption("Please check your file format and try again")
    
    # Business Objectives with suggestions
    with st.expander("🎯 Business Objectives", expanded=True):
        # Provide example objectives
        examples = [
            "Identify sales trends and seasonality patterns",
            "Find customer segments with highest lifetime value",
            "Predict churn risk and recommend retention strategies",
            "Optimize pricing based on demand elasticity",
            "Detect anomalies and potential fraud patterns"
        ]
        
        selected_example = st.selectbox(
            "Select an example or write your own:",
            ["Custom..."] + examples,
            help="Choose a predefined objective or write your own"
        )
        
        if selected_example == "Custom...":
            objective = st.text_area(
                "Business Objective",
                value=st.session_state.business_objective,
                height=100,
                placeholder="Describe what insights you want to extract from your data...",
                help="Be specific about your goals and success metrics"
            )
        else:
            objective = st.text_area(
                "Business Objective",
                value=selected_example,
                height=100,
                help="You can modify this example objective"
            )
        
        st.session_state.business_objective = objective
        
        if objective:
            progress_steps += 1
            progress_bar.progress(progress_steps / total_steps)
            
            # Objective quality score
            quality_score = min(100, len(objective) * 2)
            st.progress(quality_score / 100, text=f"Objective Quality: {quality_score}%")
    
    # Validation and next steps
    st.divider()
    
    all_ready = all([
        st.session_state.api_key,
        st.session_state.uploaded_data is not None,
        st.session_state.business_objective
    ])
    
    if all_ready:
        st.success("✅ All requirements met! Ready to proceed.")
        if st.button("🚀 Proceed to Plan Generation", type="primary", use_container_width=True):
            st.session_state.current_stage = 1
            st.rerun()
    else:
        missing = []
        if not st.session_state.api_key:
            missing.append("API Key")
        if st.session_state.uploaded_data is None:
            missing.append("Data Upload")
        if not st.session_state.business_objective:
            missing.append("Business Objective")
        
        st.warning(f"⚠️ Missing: {', '.join(missing)}")

def render_stage_1():
    """Enhanced Stage 1 with HITL features"""
    st.header("🎯 Stage 1: Plan Generation")
    st.markdown("Generate and refine your analysis plan with AI assistance")
    
    # Check prerequisites
    if not st.session_state.api_key or st.session_state.uploaded_data is None:
        st.error("Please complete Stage 0 first")
        if st.button("← Back to Input & Objectives"):
            st.session_state.current_stage = 0
            st.rerun()
        return
    
    df = st.session_state.uploaded_data
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Analysis Plan")
        
        # Generate plan with confidence scoring
        if st.button("🤖 Generate Analysis Plan", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive analysis plan..."):
                prompt = f"""
                Create a detailed data analysis plan for the following:
                
                Dataset Information:
                - Columns: {', '.join(df.columns.tolist())}
                - Shape: {df.shape}
                - Data types: {df.dtypes.to_dict()}
                - Sample data: {df.head(3).to_string()}
                
                Business Objective: {st.session_state.business_objective}
                
                Provide:
                1. Executive Summary
                2. Analysis Steps (numbered)
                3. Expected Insights
                4. Recommended Visualizations
                5. Risk Factors
                6. Success Metrics
                7. Confidence Score (0-100%)
                
                Format the response clearly with headers and bullet points.
                """
                
                try:
                    response = safe_api_call(prompt)
                    if response:
                        st.session_state.generated_plan = response
                        
                        # Extract confidence score
                        import re
                        confidence_match = re.search(r'(\d+)%', response)
                        if confidence_match:
                            confidence = int(confidence_match.group(1))
                            st.session_state.confidence_scores['plan'] = confidence
                            
                            # HITL: Request human review if confidence < 70%
                            if confidence < 70:
                                st.warning(f"⚠️ Low confidence ({confidence}%). Human review recommended.")
                                with st.expander("🔍 Request Human Review", expanded=True):
                                    review_notes = st.text_area(
                                        "Add review notes:",
                                        placeholder="What aspects need clarification?"
                                    )
                                    if st.button("Submit for Review"):
                                        st.session_state.human_feedback.append({
                                            'stage': 'plan',
                                            'confidence': confidence,
                                            'notes': review_notes,
                                            'timestamp': datetime.now().isoformat()
                                        })
                                        st.success("✅ Submitted for human review")
                            elif confidence >= 90:
                                st.success(f"✅ High confidence plan ({confidence}%)")
                            else:
                                st.info(f"ℹ️ Moderate confidence ({confidence}%)")
                        
                        st.success("✅ Plan generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate plan: {str(e)}")
        
        # Display and edit plan
        if st.session_state.generated_plan:
            # Editable plan with version tracking
            edited_plan = st.text_area(
                "Review and Edit Plan:",
                value=st.session_state.generated_plan,
                height=400,
                help="You can modify the plan before proceeding"
            )
            
            # Track changes
            if edited_plan != st.session_state.generated_plan:
                st.info("📝 Plan has been modified")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Changes"):
                        st.session_state.generated_plan = edited_plan
                        st.success("✅ Changes saved!")
                with col2:
                    if st.button("↩️ Revert Changes"):
                        st.rerun()
        
        # Export plan
        if st.session_state.generated_plan:
            st.download_button(
                "📥 Download Plan",
                st.session_state.generated_plan,
                "analysis_plan.txt",
                "text/plain",
                use_container_width=True
            )
    
    with col2:
        st.subheader("💬 AI Assistant")
        
        # Enhanced chat with context awareness
        chat_container = st.container()
        
        # Chat input with suggestions
        suggestions = [
            "Can you explain the analysis approach?",
            "What are the potential risks?",
            "How long will this analysis take?",
            "What additional data would be helpful?",
            "Can you prioritize the insights?"
        ]
        
        selected_suggestion = st.selectbox(
            "Quick questions:",
            ["Type your own..."] + suggestions
        )
        
        if selected_suggestion == "Type your own...":
            user_input = st.text_input("Ask about your analysis:", key="chat_input")
        else:
            user_input = selected_suggestion
        
        if st.button("Send", type="primary") and user_input:
            with st.spinner("Thinking..."):
                try:
                    context = f"""
                    Data columns: {df.columns.tolist()}
                    Data shape: {df.shape}
                    Objective: {st.session_state.business_objective}
                    Current plan summary: {st.session_state.generated_plan[:500] if st.session_state.generated_plan else 'No plan yet'}
                    Question: {user_input}
                    
                    Provide a helpful, concise response.
                    """
                    
                    response = safe_api_call(context)
                    if response:
                        st.session_state.chat_history.append({
                            "user": user_input,
                            "ai": response,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    st.error(f"Chat error: {str(e)}")
        
        # Display chat history with timestamps
        with chat_container:
            for chat in st.session_state.chat_history[-5:]:
                with st.container():
                    st.info(f"👤 You: {chat['user']}")
                    st.success(f"🤖 AI: {chat['ai']}")
                    st.caption(f"🕒 {chat.get('timestamp', 'Unknown time')}")
    
    # Navigation with validation
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Input", use_container_width=True):
            st.session_state.current_stage = 0
            st.rerun()
    with col2:
        # Show readiness status
        if st.session_state.generated_plan:
            st.success("✅ Ready to proceed")
        else:
            st.warning("⚠️ Generate plan first")
    with col3:
        if st.button(
            "Next: Data Understanding →",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.generated_plan
        ):
            st.session_state.current_stage = 2
            st.rerun()

def render_stage_2():
    """Enhanced Stage 2 with comprehensive insights and HITL"""
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
    
    # Create enhanced tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Overview",
        "📊 Statistics",
        "🔍 Quality",
        "📉 Visualizations",
        "💡 AI Insights",
        "🤖 HITL Control"
    ])
    
    with tab1:
        st.subheader("Data Overview")
        
        # Enhanced metrics with trends
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            missing = df.isnull().sum().sum()
            missing_pct = (missing / (len(df) * len(df.columns))) * 100
            st.metric(
                "Missing Values",
                f"{missing:,}",
                f"{missing_pct:.1f}%",
                delta_color="inverse"
            )
        with col4:
            duplicates = df.duplicated().sum()
            dup_pct = (duplicates / len(df)) * 100
            st.metric(
                "Duplicates",
                duplicates,
                f"{dup_pct:.1f}%",
                delta_color="inverse"
            )
        
        # Data preview with filtering
        st.subheader("Data Sample")
        
        # Add search functionality
        search_term = st.text_input("🔍 Search in data:", placeholder="Type to filter...")
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            filtered_df = df[mask]
            st.info(f"Found {len(filtered_df)} matching rows")
            st.dataframe(filtered_df.head(20), use_container_width=True)
        else:
            st.dataframe(df.head(10), use_container_width=True)
        
        # Column information with insights
        st.subheader("Column Information")
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes,
            'Non-Null': df.count(),
            'Null': df.isnull().sum(),
            'Null %': (df.isnull().sum() / len(df) * 100).round(1),
            'Unique': df.nunique(),
            'Unique %': (df.nunique() / len(df) * 100).round(1)
        })
        
        # Highlight problematic columns
        def highlight_issues(row):
            styles = [''] * len(row)
            if row['Null %'] > 20:
                styles[4] = 'background-color: #ffcccc'
            if row['Unique %'] > 95:
                styles[6] = 'background-color: #ffffcc'
            return styles
        
        st.dataframe(
            col_info.style.apply(highlight_issues, axis=1),
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Statistical Summary")
        
        # Numeric columns stats with insights
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.write("**Numeric Columns Analysis**")
            
            # Enhanced statistics
            stats = df[numeric_cols].describe()
            stats.loc['median'] = df[numeric_cols].median()
            stats.loc['mode'] = df[numeric_cols].mode().iloc[0] if len(df[numeric_cols].mode()) > 0 else np.nan
            stats.loc['skew'] = df[numeric_cols].skew()
            stats.loc['kurtosis'] = df[numeric_cols].kurtosis()
            
            st.dataframe(stats, use_container_width=True)
            
            # Correlation matrix with insights
            st.write("**Correlation Matrix**")
            corr_matrix = df[numeric_cols].corr()
            
            # Find strong correlations
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corr.append({
                            'Variable 1': corr_matrix.columns[i],
                            'Variable 2': corr_matrix.columns[j],
                            'Correlation': round(corr_matrix.iloc[i, j], 3)
                        })
            
            if strong_corr:
                st.warning(f"⚠️ Found {len(strong_corr)} strong correlations (|r| > 0.7):")
                st.dataframe(pd.DataFrame(strong_corr), use_container_width=True)
            
            # Heatmap
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="Correlation Heatmap",
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Categorical columns analysis
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            st.write("**Categorical Columns Analysis**")
            cat_info = []
            for col in categorical_cols:
                cat_info.append({
                    'Column': col,
                    'Unique Values': df[col].nunique(),
                    'Most Frequent': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A',
                    'Frequency': df[col].value_counts().iloc[0] if len(df[col].value_counts()) > 0 else 0,
                    'Missing': df[col].isnull().sum()
                })
            st.dataframe(pd.DataFrame(cat_info), use_container_width=True)
    
    with tab3:
        st.subheader("Data Quality Assessment")
        
        # Quality score calculation
        quality_metrics = {
            'Completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'Uniqueness': (1 - df.duplicated().sum() / len(df)) * 100,
            'Consistency': 100  # Placeholder - would need business rules
        }
        
        overall_quality = np.mean(list(quality_metrics.values()))
        
        # Display quality metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Quality", f"{overall_quality:.1f}%")
        with col2:
            st.metric("Completeness", f"{quality_metrics['Completeness']:.1f}%")
        with col3:
            st.metric("Uniqueness", f"{quality_metrics['Uniqueness']:.1f}%")
        with col4:
            st.metric("Consistency", f"{quality_metrics['Consistency']:.1f}%")
        
        # Quality issues summary
        st.write("**Quality Issues Summary**")
        
        issues = []
        
        # Check for missing values
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 0:
                issues.append({
                    'Type': 'Missing Values',
                    'Column': col,
                    'Severity': 'High' if missing_pct > 20 else 'Medium' if missing_pct > 5 else 'Low',
                    'Details': f"{missing_pct:.1f}% missing"
                })
        
        # Check for outliers in numeric columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)]
            if len(outliers) > 0:
                outlier_pct = (len(outliers) / len(df)) * 100
                issues.append({
                    'Type': 'Outliers',
                    'Column': col,
                    'Severity': 'High' if outlier_pct > 10 else 'Medium' if outlier_pct > 5 else 'Low',
                    'Details': f"{outlier_pct:.1f}% outliers"
                })
        
        if issues:
            issues_df = pd.DataFrame(issues)
            
            # Color code by severity
            def color_severity(val):
                if val == 'High':
                    return 'background-color: #ffcccc'
                elif val == 'Medium':
                    return 'background-color: #ffffcc'
                else:
                    return 'background-color: #ccffcc'
            
            st.dataframe(
                issues_df.style.applymap(color_severity, subset=['Severity']),
                use_container_width=True
            )
        else:
            st.success("✅ No significant quality issues detected!")
    
    with tab4:
        st.subheader("Interactive Visualizations")
        
        if len(numeric_cols) > 0:
            # Advanced visualization options
            viz_type = st.selectbox(
                "Select Visualization Type",
                ["Distribution", "Relationships", "Time Series", "Composition", "Comparison"]
            )
            
            if viz_type == "Distribution":
                selected_col = st.selectbox("Select column:", numeric_cols)
                
                col1, col2 = st.columns(2)
                with col1:
                    # Histogram with KDE
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(
                        x=df[selected_col],
                        nbinsx=30,
                        name='Histogram',
                        opacity=0.7
                    ))
                    fig.update_layout(
                        title=f"Distribution of {selected_col}",
                        xaxis_title=selected_col,
                        yaxis_title="Frequency"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Box plot with outliers
                    fig = go.Figure()
                    fig.add_trace(go.Box(
                        y=df[selected_col],
                        name=selected_col,
                        boxpoints='outliers'
                    ))
                    fig.update_layout(
                        title=f"Box Plot of {selected_col}",
                        yaxis_title=selected_col
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Relationships":
                if len(numeric_cols) > 1:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X-axis:", numeric_cols)
                    with col2:
                        y_col = st.selectbox("Y-axis:", numeric_cols)
                    
                    # Enhanced scatter plot
                    fig = px.scatter(
                        df, x=x_col, y=y_col,
                        title=f"{x_col} vs {y_col}",
                        trendline="ols",
                        marginal_x="histogram",
                        marginal_y="histogram"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show correlation
                    corr = df[x_col].corr(df[y_col])
                    st.info(f"Correlation coefficient: {corr:.3f}")
    
    with tab5:
        st.subheader("AI-Powered Insights")
        
        # Enhanced insights generation with confidence scoring
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🤖 Generate Comprehensive AI Insights", type="primary", use_container_width=True):
                with st.spinner("Analyzing data patterns and generating insights..."):
                    try:
                        # Prepare comprehensive data summary
                        data_summary = f"""
                        Analyze this dataset and provide actionable insights:
                        
                        Dataset Overview:
                        - Shape: {df.shape}
                        - Columns: {', '.join(df.columns.tolist())}
                        - Data types: {df.dtypes.to_dict()}
                        
                        Statistical Summary:
                        {df.describe().to_string()}
                        
                        Missing Values: {df.isnull().sum().to_dict()}
                        Unique Values: {df.nunique().to_dict()}
                        
                        Business Objective: {st.session_state.business_objective}
                        Analysis Plan Summary: {st.session_state.generated_plan[:500] if st.session_state.generated_plan else 'Not available'}
                        
                        Please provide:
                        1. Key Patterns and Trends (with specific numbers)
                        2. Anomalies or Outliers detected
                        3. Correlations and Relationships
                        4. Data Quality Issues
                        5. Actionable Recommendations (prioritized)
                        6. Suggested Next Steps
                        7. Confidence Level (0-100%) for each insight
                        
                        Format as structured markdown with clear sections.
                        """
                        
                        response = safe_api_call(data_summary, 'gemini-pro')
                        if response:
                            st.session_state.data_insights = response
                            
                            # Extract confidence scores
                            import re
                            confidence_matches = re.findall(r'(\d+)%', response)
                            if confidence_matches:
                                avg_confidence = np.mean([int(c) for c in confidence_matches])
                                st.session_state.confidence_scores['insights'] = avg_confidence
                                
                                # HITL trigger for low confidence
                                if avg_confidence < 70:
                                    st.warning(f"⚠️ Low confidence insights ({avg_confidence:.0f}%). Human validation recommended.")
                                else:
                                    st.success(f"✅ Insights generated with {avg_confidence:.0f}% confidence")
                        
                    except Exception as e:
                        st.error(f"Error generating insights: {str(e)}")
                        logger.error(f"Insights generation failed: {str(e)}")
        
        with col2:
            if st.session_state.data_insights:
                # Confidence indicator
                if 'insights' in st.session_state.confidence_scores:
                    confidence = st.session_state.confidence_scores['insights']
                    if confidence >= 80:
                        st.success(f"🎯 {confidence:.0f}%")
                    elif confidence >= 60:
                        st.warning(f"⚠️ {confidence:.0f}%")
                    else:
                        st.error(f"❌ {confidence:.0f}%")
        
        # Display insights with formatting
        if st.session_state.data_insights:
            # Create expandable sections for better readability
            insights_sections = st.session_state.data_insights.split('\n\n')
            for section in insights_sections:
                if section.strip():
                    with st.expander(section.split('\n')[0] if '\n' in section else section[:50], expanded=True):
                        st.markdown(section)
            
            # Export insights
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    "📄 Download Insights (Text)",
                    st.session_state.data_insights,
                    "data_insights.txt",
                    "text/plain"
                )
            with col2:
                # Convert to markdown
                st.download_button(
                    "📝 Download Insights (Markdown)",
                    st.session_state.data_insights,
                    "data_insights.md",
                    "text/markdown"
                )
            with col3:
                # Generate PDF report (placeholder)
                if st.button("📊 Generate Full Report"):
                    st.info("Full report generation coming soon!")
    
    with tab6:
        st.subheader("🤖 Human-in-the-Loop Control Panel")
        
        # HITL Settings
        st.write("**Automation Settings**")
        
        col1, col2 = st.columns(2)
        with col1:
            auto_threshold = st.slider(
                "Auto-approval threshold (%)",
                min_value=50,
                max_value=100,
                value=90,
                step=5,
                help="Automatically approve AI decisions above this confidence level"
            )
            
            review_threshold = st.slider(
                "Human review threshold (%)",
                min_value=0,
                max_value=100,
                value=70,
                step=5,
                help="Request human review below this confidence level"
            )
        
        with col2:
            st.write("**Current Status**")
            if 'confidence_scores' in st.session_state and st.session_state.confidence_scores:
                for key, value in st.session_state.confidence_scores.items():
                    if value >= auto_threshold:
                        st.success(f"✅ {key.title()}: {value:.0f}% (Auto-approved)")
                    elif value < review_threshold:
                        st.error(f"🔍 {key.title()}: {value:.0f}% (Needs review)")
                    else:
                        st.warning(f"⚠️ {key.title()}: {value:.0f}% (Manual check)")
            else:
                st.info("No decisions made yet")
        
        # Feedback History
        st.write("**Human Feedback History**")
        if st.session_state.human_feedback:
            feedback_df = pd.DataFrame(st.session_state.human_feedback)
            st.dataframe(feedback_df, use_container_width=True)
            
            # Export feedback
            st.download_button(
                "📥 Export Feedback Log",
                feedback_df.to_csv(index=False),
                "feedback_log.csv",
                "text/csv"
            )
        else:
            st.info("No feedback recorded yet")
        
        # Manual Override Section
        st.write("**Manual Override**")
        override_stage = st.selectbox(
            "Select stage to override:",
            ["Plan Generation", "Data Insights", "Visualizations"]
        )
        
        override_notes = st.text_area(
            "Override instructions:",
            placeholder="Provide specific instructions for the AI..."
        )
        
        if st.button("🔄 Apply Override", type="primary"):
            if override_notes:
                st.session_state.human_feedback.append({
                    'type': 'override',
                    'stage': override_stage,
                    'instructions': override_notes,
                    'timestamp': datetime.now().isoformat()
                })
                st.success("✅ Override applied successfully")
                st.rerun()
            else:
                st.warning("Please provide override instructions")
    
    # Export and Navigation
    st.divider()
    st.subheader("📥 Export Options")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Export processed data
        csv = df.to_csv(index=False)
        st.download_button(
            "📊 Download Data (CSV)",
            csv,
            "processed_data.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export insights
        if st.session_state.data_insights:
            st.download_button(
                "💡 Download Insights",
                st.session_state.data_insights,
                "insights.txt",
                "text/plain",
                use_container_width=True
            )
    
    with col3:
        # Export plan
        if st.session_state.generated_plan:
            st.download_button(
                "📋 Download Plan",
                st.session_state.generated_plan,
                "analysis_plan.txt",
                "text/plain",
                use_container_width=True
            )
    
    with col4:
        # Complete report
        if st.button("📑 Generate Complete Report", use_container_width=True):
            with st.spinner("Generating comprehensive report..."):
                report = f"""
                # AI Data Analysis Report
                Generated: {datetime.now().isoformat()}
                
                ## Executive Summary
                - Dataset: {len(df)} rows, {len(df.columns)} columns
                - Objective: {st.session_state.business_objective}
                - Overall Quality Score: {overall_quality:.1f}%
                
                ## Analysis Plan
                {st.session_state.generated_plan}
                
                ## Data Insights
                {st.session_state.data_insights}
                
                ## Quality Metrics
                - Completeness: {quality_metrics['Completeness']:.1f}%
                - Uniqueness: {quality_metrics['Uniqueness']:.1f}%
                - Consistency: {quality_metrics['Consistency']:.1f}%
                
                ## Recommendations
                Based on the analysis, we recommend focusing on the insights with confidence scores above 80%.
                
                ---
                Report generated by AI Analysis Platform (Enhanced)
                """
                
                st.download_button(
                    "⬇️ Download Complete Report",
                    report,
                    "complete_analysis_report.md",
                    "text/markdown"
                )

# Main app
def main():
    init_session_state()
    render_sidebar()
    
    # Route to appropriate stage
    if st.session_state.current_stage == 0:
        render_stage_0()
    elif st.session_state.current_stage == 1:
        render_stage_1()
    elif st.session_state.current_stage == 2:
        render_stage_2()
    
    # Footer with metrics
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.caption(f"Session Time: {st.session_state.get('total_processing_time', 0):.1f}s")
    with col2:
        st.caption(f"API Calls: {st.session_state.get('api_calls', 0)}")
    with col3:
        st.caption(f"Cache Hits: {st.session_state.get('cache_hits', 0)}")
    with col4:
        st.caption("Version: 2.0 Enhanced")

if __name__ == "__main__":
    main()