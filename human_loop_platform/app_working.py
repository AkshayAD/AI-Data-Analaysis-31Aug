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
import os
from dotenv import load_dotenv
import hashlib

# Import orchestrator bridge (if available)
try:
    from orchestrator_bridge import (
        get_bridge_instance,
        connect_to_orchestrator,
        submit_task,
        get_task_status,
        handle_websocket_updates
    )
    ORCHESTRATOR_AVAILABLE = True
    
    # Additional imports for HITL
    import requests
    ORCHESTRATOR_URL = "http://localhost:8000"
    
    def check_pending_approvals():
        """Check for pending approval tasks"""
        try:
            response = requests.get(f"{ORCHESTRATOR_URL}/pending-reviews", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("reviews", [])
        except:
            pass
        return []
    
    def approve_task(task_id, feedback=""):
        """Approve a pending task"""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/tasks/{task_id}/approve",
                json={"feedback": feedback, "reviewer_id": "streamlit_user"},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def reject_task(task_id, feedback=""):
        """Reject a pending task"""
        try:
            response = requests.post(
                f"{ORCHESTRATOR_URL}/tasks/{task_id}/reject",
                json={"feedback": feedback, "reviewer_id": "streamlit_user"},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
            
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("Orchestrator bridge not available. HITL features disabled.")

# Configure caching - will be set after environment loads
CACHE_TTL = 3600  # 1 hour default

# Load environment variables
def load_environment():
    """Load environment variables from .env file"""
    env_paths = [
        Path(__file__).parent / ".env",  # Same directory as app
        Path(__file__).parent.parent / ".env",  # Root directory
        Path.cwd() / ".env"  # Current working directory
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded environment from: {env_path}")
            break
    else:
        # Try loading from default location
        load_dotenv()

def get_api_key_from_env():
    """Get API key from environment with fallback options"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    # Also check alternative environment variable names
    if not api_key:
        api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        api_key = os.getenv('AI_API_KEY')
    
    return api_key

def get_app_config():
    """Get application configuration from environment"""
    return {
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'port': int(os.getenv('STREAMLIT_SERVER_PORT', 8503)),
        'cache_ttl': int(os.getenv('CACHE_TTL_SECONDS', 3600)),
        'allowed_hosts': os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    }

# Cached API functions
@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def cached_generate_plan(objective: str, data_sample: str, api_key: str, model_name: str = 'gemini-pro') -> str:
    """Generate analysis plan with caching based on objective and data"""
    # Check if we're in mock mode
    if api_key == "MOCK_API_KEY" or os.getenv('MOCK_MODE') == 'true':
        # Return a mock analysis plan
        return f"""## 📊 AI-Generated Analysis Plan (Mock Mode)

### 📋 Executive Summary
This analysis plan is generated in **mock mode** for testing purposes. Based on your objective and data sample, here's a comprehensive approach to analyze your e-commerce data.

### 🎯 Analysis Objective
{objective[:200]}...

### 📈 Data Exploration Steps
1. **Data Quality Assessment**
   - Check for missing values and outliers
   - Validate data types and formats
   - Identify data completeness

2. **Descriptive Statistics**
   - Calculate mean, median, mode for numeric columns
   - Analyze frequency distributions
   - Examine data ranges and variances

### 📊 Statistical Analysis Methods
1. **Correlation Analysis** - Identify relationships between variables
2. **Time Series Analysis** - Detect trends and seasonality
3. **Segmentation Analysis** - Group customers by behavior
4. **Regression Analysis** - Predict future outcomes

### 🎨 Visualization Recommendations
- **Bar Charts** for category comparisons
- **Line Charts** for trend analysis
- **Heatmaps** for correlation matrices
- **Scatter Plots** for relationship analysis
- **Box Plots** for distribution analysis

### 💡 Key Insights to Extract
1. Top performing product categories
2. Customer purchase patterns
3. Seasonal trends and peaks
4. Price sensitivity analysis
5. Geographic distribution patterns

### ✅ Success Metrics
- Increase in average order value
- Customer retention rate improvement
- Inventory optimization efficiency
- Marketing ROI enhancement

*Note: This is a mock plan generated for testing. Connect a real API key for actual AI-powered analysis.*"""
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Based on this business objective: {objective}
    
    And this data sample:
    {data_sample}
    
    Create a detailed analysis plan including:
    1. Data preparation steps
    2. Analysis techniques to apply
    3. Expected insights
    4. Visualization recommendations
    
    Format as a clear, actionable plan.
    """
    
    response = model.generate_content(prompt)
    return response.text

@st.cache_data(ttl=CACHE_TTL, show_spinner=False)
def cached_chat_response(question: str, context: str, api_key: str, model_name: str = 'gemini-pro') -> str:
    """Generate chat response with caching based on question and context"""
    # Check if we're in mock mode
    if api_key == "MOCK_API_KEY" or os.getenv('MOCK_MODE') == 'true':
        return f"""**Mock AI Response:**

Based on your question about "{question[:50]}...", here's a simulated response:

This is a mock response generated for testing purposes. In a real scenario, the AI would analyze your data context and provide specific insights about:
- Data patterns and trends
- Statistical relationships
- Actionable recommendations
- Potential areas of concern

*Note: Connect a real API key for actual AI-powered responses.*"""
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    full_context = f"""
    Context: {context}
    
    Question: {question}
    
    Please provide a helpful and detailed answer.
    """
    
    response = model.generate_content(full_context)
    return response.text

@st.cache_data(ttl=CACHE_TTL, show_spinner=False) 
def cached_generate_insights(data_summary: str, objective: str, api_key: str, model_name: str = 'gemini-pro') -> str:
    """Generate data insights with caching based on data and objective"""
    # Check if we're in mock mode
    if api_key == "MOCK_API_KEY" or os.getenv('MOCK_MODE') == 'true':
        return """## 🔍 AI-Generated Insights (Mock Mode)

### 📊 Key Patterns and Trends
• **Sales Growth**: Consistent upward trend in Q1 with 15% month-over-month growth
• **Category Performance**: Electronics showing highest revenue contribution (35%)
• **Customer Behavior**: Peak purchasing hours between 7-9 PM
• **Geographic Patterns**: Highest sales concentration in urban areas

### 📈 Statistical Insights
• **Average Order Value**: $75.50 with standard deviation of $23.20
• **Customer Retention**: 68% repeat purchase rate within 30 days
• **Conversion Rate**: 3.2% from browse to purchase
• **Cart Abandonment**: 42% of initiated checkouts not completed

### 💡 Actionable Recommendations
• **Inventory Optimization**: Increase stock for top 20% performing products
• **Marketing Focus**: Target evening hours for promotional campaigns
• **Pricing Strategy**: Consider dynamic pricing for high-demand periods
• **Customer Experience**: Simplify checkout process to reduce abandonment

### ⚠️ Potential Risks or Concerns
• **Seasonal Dependency**: 40% of revenue concentrated in Q4
• **Single Category Risk**: Over-reliance on electronics category
• **Geographic Limitation**: Limited market penetration in rural areas
• **Price Sensitivity**: High correlation between discounts and sales volume

*Note: This is mock analysis for testing. Connect a real API key for actual data insights.*"""
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    Analyze this data summary:
    {data_summary}
    
    Business objective: {objective}
    
    Provide:
    1. Key patterns and trends
    2. Statistical insights
    3. Actionable recommendations
    4. Potential risks or concerns
    
    Format as clear bullet points.
    """
    
    response = model.generate_content(prompt)
    return response.text

@st.cache_data(ttl=60, show_spinner=False)  # Short cache for connection test
def cached_test_connection(api_key: str) -> Dict[str, Any]:
    """Test API connection with short-term caching"""
    # Check if we're in mock mode for testing
    if api_key == "MOCK_API_KEY" or os.getenv('MOCK_MODE') == 'true':
        return {
            "success": True,
            "mock": True,
            "message": "Mock mode - API connection simulated"
        }
    
    # Validate API key format
    if not api_key or len(api_key) < 20:
        return {
            "success": False,
            "error": "invalid_format",
            "message": "API key format appears invalid"
        }
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say 'Connected!'")
        return {
            "success": True,
            "mock": False,
            "message": "API connection successful"
        }
    except Exception as e:
        error_str = str(e)
        if "API_KEY_INVALID" in error_str.upper() or "INVALID API KEY" in error_str.upper():
            return {
                "success": False,
                "error": "invalid_key",
                "message": "API key is invalid or revoked",
                "details": error_str
            }
        elif "quota" in error_str.lower() or "rate" in error_str.lower():
            return {
                "success": False,
                "error": "rate_limit",
                "message": "API rate limit exceeded",
                "details": error_str
            }
        else:
            return {
                "success": False,
                "error": "network",
                "message": "Network or connection error",
                "details": error_str
            }

# Load environment variables
load_environment()

# Update cache TTL from environment
CACHE_TTL = int(os.getenv('CACHE_TTL_SECONDS', '3600'))

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
    
    # Initialize API key from environment or empty
    if 'api_key' not in st.session_state:
        env_api_key = get_api_key_from_env()
        st.session_state.api_key = env_api_key if env_api_key else ""
    
    # Track if API key came from environment
    if 'api_key_source' not in st.session_state:
        env_api_key = get_api_key_from_env()
        st.session_state.api_key_source = "environment" if env_api_key else "user_input"
    
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
    
    # Orchestrator integration
    if 'orchestrator_connected' not in st.session_state:
        st.session_state.orchestrator_connected = False
    if 'orchestrator_status' not in st.session_state:
        st.session_state.orchestrator_status = "Disconnected"
    if 'hitl_enabled' not in st.session_state:
        st.session_state.hitl_enabled = False
    if 'current_task_id' not in st.session_state:
        st.session_state.current_task_id = None
    if 'task_updates' not in st.session_state:
        st.session_state.task_updates = []
    if 'last_error_time' not in st.session_state:
        st.session_state.last_error_time = None
    if 'pending_approvals' not in st.session_state:
        st.session_state.pending_approvals = []

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
            if st.session_state.api_key_source == "environment":
                st.caption("🌍 From env var")
        elif st.session_state.api_status == 'failed':
            st.error("❌ API Failed")
        elif st.session_state.api_key:
            if st.session_state.api_key_source == "environment":
                st.info("🌍 API From Env (Not Tested)")
            else:
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
        
        # Orchestrator Status
        if ORCHESTRATOR_AVAILABLE:
            st.divider()
            st.subheader("Orchestrator Status")
            
            # Add test attribute for UI tests
            status_container = st.container()
            with status_container:
                if st.session_state.orchestrator_connected:
                    st.success(f"✅ {st.session_state.orchestrator_status}")
                    st.markdown('<div data-testid="orchestrator-status">Connected</div>', unsafe_allow_html=True)
                else:
                    st.warning(f"⚠️ {st.session_state.orchestrator_status}")
                    st.markdown('<div data-testid="orchestrator-status">Disconnected</div>', unsafe_allow_html=True)
                
                # Connect button
                if st.button("🔌 Connect to Orchestrator", use_container_width=True):
                    with st.spinner("Connecting..."):
                        if connect_to_orchestrator():
                            st.session_state.orchestrator_connected = True
                            st.session_state.orchestrator_status = "Connected"
                            st.success("Connected!")
                            st.rerun()
                        else:
                            st.session_state.orchestrator_connected = False
                            st.session_state.orchestrator_status = "Connection Failed"
                            st.error("Failed to connect")
            
            # HITL Workflow Toggle
            st.divider()
            hitl_enabled = st.checkbox(
                "Enable HITL Workflow",
                value=st.session_state.hitl_enabled,
                key="hitl_checkbox",
                help="Enable Human-in-the-Loop workflow for AI decisions"
            )
            st.session_state.hitl_enabled = hitl_enabled
            
            if hitl_enabled:
                st.caption("✅ HITL workflow enabled")
                # Check for pending approvals
                if st.button("🔍 Check Pending Approvals"):
                    with st.spinner("Checking..."):
                        pending = check_pending_approvals()
                        if pending:
                            st.warning(f"⚠️ {len(pending)} tasks awaiting review")
                            st.session_state.pending_approvals = pending
                        else:
                            st.info("No pending approvals")
                
            # Current Task Status
            if st.session_state.current_task_id:
                st.divider()
                st.subheader("Current Task")
                st.markdown(f'<div data-testid="task-id">{st.session_state.current_task_id}</div>', 
                          unsafe_allow_html=True)
                
                # Task updates
                if st.session_state.task_updates:
                    with st.expander("Status Updates", expanded=False):
                        updates_text = "\n".join(st.session_state.task_updates[-5:])
                        st.markdown(f'<div data-testid="status-updates">{updates_text}</div>', 
                                  unsafe_allow_html=True)

def render_stage_0():
    """Stage 0: Input & Objectives"""
    st.header("📝 Stage 0: Input & Objectives")
    st.markdown("Configure your AI analysis settings and upload data")
    
    # API Configuration
    with st.expander("🔑 Gemini API Configuration", expanded=True):
        # Display environment variable status
        if st.session_state.api_key_source == "environment":
            st.info("🌍 **API Key loaded from environment variable**")
            st.caption("Key is securely loaded from GEMINI_API_KEY environment variable")
        
        # Display persistent connection status
        if st.session_state.api_status == 'connected':
            st.success(f"✅ Connected - {st.session_state.api_status_message}")
        elif st.session_state.api_status == 'failed':
            st.error(f"❌ Failed - {st.session_state.api_status_message}")
            if st.session_state.api_error_details:
                st.caption(f"Error details: {st.session_state.api_error_details}")
        elif st.session_state.api_key:
            if st.session_state.api_key_source == "environment":
                st.info("ℹ️ Environment API key loaded but not tested")
            else:
                st.info("ℹ️ API key entered but not tested")
        else:
            st.warning("⚠️ No API key configured")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Show different UI based on source
            if st.session_state.api_key_source == "environment":
                # Show masked key with option to override
                masked_key = "●●●●●●●●" + (st.session_state.api_key[-4:] if len(st.session_state.api_key) > 4 else "")
                st.text_input(
                    "Gemini API Key (from environment)",
                    value=masked_key,
                    type="password",
                    disabled=True,
                    help="API key is loaded from environment variable GEMINI_API_KEY"
                )
                
                # Allow user to override
                if st.checkbox("Override with manual key", key="override_env_key"):
                    api_key = st.text_input(
                        "Enter manual API key",
                        value="",
                        type="password",
                        placeholder="Enter your Gemini API key to override environment"
                    )
                    if api_key:
                        st.session_state.api_key = api_key
                        st.session_state.api_key_source = "user_input"
                        st.rerun()
                else:
                    api_key = st.session_state.api_key
            else:
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
                            
                            # Use cached connection test with retry
                            def test_connection_wrapper():
                                result = cached_test_connection(api_key)
                                if not result["success"]:
                                    error_msg = result.get("message", "Connection test failed")
                                    if result.get("details"):
                                        error_msg += f": {result['details']}"
                                    raise Exception(error_msg)
                                return result
                            
                            response = retry_api_call(test_connection_wrapper, max_retries=3, delay=1.0)
                            
                            # Update session state for persistence
                            st.session_state.api_status = 'connected'
                            if response.get("mock"):
                                st.session_state.api_status_message = "Mock Mode - Testing without real API"
                            else:
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
                    
                    # Prepare data sample for caching
                    df = st.session_state.uploaded_data
                    data_sample = f"""
                    Data Overview:
                    - Rows: {len(df)}
                    - Columns: {', '.join(df.columns.tolist())}
                    - Data types: {df.dtypes.to_dict()}
                    - Sample: {df.head(3).to_string()}
                    """
                    
                    # Use cached function with retry for network issues
                    def generate_plan_wrapper():
                        return cached_generate_plan(
                            objective=st.session_state.business_objective,
                            data_sample=data_sample,
                            api_key=st.session_state.api_key,
                            model_name='gemini-pro'
                        )
                    
                    # Execute with retry logic for network errors (cache handles API responses)
                    result = retry_api_call(generate_plan_wrapper, max_retries=3, delay=2.0)
                    st.session_state.generated_plan = result
                    st.success("✅ Plan generated successfully!")
                    
                except ValueError as ve:
                    # Handle validation errors
                    st.error(f"❌ Validation Error: {str(ve)}")
                except Exception as e:
                    # Handle API errors with detailed information
                    handle_api_error(e, "Plan generation")
        
        # Plan Editor - only show if plan exists
        if st.session_state.generated_plan:
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
        else:
            # Show empty state with guidance
            st.info("📝 **No plan generated yet**")
            st.markdown("""
            Click the **🤖 Generate AI Plan** button above to create an analysis plan based on your:
            - Uploaded data
            - Business objectives
            - Analysis requirements
            
            The AI will generate a comprehensive plan including:
            - Data exploration steps
            - Statistical analysis methods
            - Visualization recommendations
            - Key insights to extract
            """)
        
        # Submit to Orchestrator button
        if ORCHESTRATOR_AVAILABLE and st.session_state.orchestrator_connected:
            st.divider()
            if st.button("🚀 Submit to Orchestrator", type="primary", use_container_width=True):
                with st.spinner("Submitting task to orchestrator..."):
                    try:
                        # Prepare task parameters
                        df = st.session_state.uploaded_data
                        task_params = {
                            "objective": st.session_state.business_objective,
                            "plan": st.session_state.generated_plan,
                            "data_info": {
                                "rows": len(df),
                                "columns": list(df.columns),
                                "types": {str(k): str(v) for k, v in df.dtypes.to_dict().items()}
                            }
                        }
                        
                        # Submit task
                        task_id = submit_task(
                            task_type="data_analysis",
                            parameters=task_params,
                            priority=2,
                            confidence_threshold=0.7,
                            require_human_review=st.session_state.hitl_enabled
                        )
                        
                        if task_id:
                            st.session_state.current_task_id = task_id
                            st.session_state.task_updates = [f"Task {task_id} submitted"]
                            st.success(f"✅ Task submitted! ID: {task_id}")
                            
                            # Register WebSocket handler
                            def handle_update(update_data):
                                st.session_state.task_updates.append(str(update_data))
                            
                            handle_websocket_updates(handle_update)
                        else:
                            st.error("Failed to submit task to orchestrator")
                            
                    except Exception as e:
                        st.error(f"Error submitting task: {str(e)}")
    
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
                    
                    # Prepare context for caching
                    context = f"""
                    Data columns: {st.session_state.uploaded_data.columns.tolist()}
                    Objective: {st.session_state.business_objective}
                    Current plan: {st.session_state.generated_plan[:500] if st.session_state.generated_plan else 'No plan generated yet'}
                    """
                    
                    # Use cached function
                    def process_chat_wrapper():
                        return cached_chat_response(
                            question=user_input,
                            context=context,
                            api_key=st.session_state.api_key,
                            model_name='gemini-pro'
                        )
                    
                    # Execute with retry logic for network errors
                    response_text = retry_api_call(process_chat_wrapper, max_retries=3, delay=2.0)
                    st.session_state.chat_history.append({"user": user_input, "ai": response_text})
                    
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
    tabs = ["📈 Overview", "📊 Statistics", "🔍 Quality", "📉 Visualizations", "💡 AI Insights"]
    if ORCHESTRATOR_AVAILABLE and st.session_state.orchestrator_connected:
        tabs.append("✅ Pending Approvals")
    tab_objects = st.tabs(tabs)
    tab1, tab2, tab3, tab4, tab5 = tab_objects[:5]
    tab6 = tab_objects[5] if len(tab_objects) > 5 else None
    
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
                    
                    # Prepare data summary for caching
                    data_summary = f"""
                    Dataset Overview:
                    - Shape: {df.shape}
                    - Columns: {', '.join(df.columns.tolist())}
                    - Numeric columns statistics:
                    {df.describe().to_string()}
                    
                    Missing values: {df.isnull().sum().to_dict()}
                    """
                    
                    objective = st.session_state.business_objective if st.session_state.business_objective else 'General data analysis'
                    
                    # Use cached function
                    def generate_insights_wrapper():
                        return cached_generate_insights(
                            data_summary=data_summary,
                            objective=objective,
                            api_key=st.session_state.api_key,
                            model_name='gemini-pro'
                        )
                    
                    # Execute with retry logic for network errors
                    result = retry_api_call(generate_insights_wrapper, max_retries=3, delay=2.0)
                    st.session_state.data_insights = result
                    st.success("✅ Insights generated successfully!")
                    
                except ValueError as ve:
                    st.error(f"❌ Validation Error: {str(ve)}")
                except Exception as e:
                    handle_api_error(e, "AI insights generation")
        
        if st.session_state.data_insights:
            st.markdown(st.session_state.data_insights)
    
    # HITL Pending Approvals Tab
    if tab6 and ORCHESTRATOR_AVAILABLE and st.session_state.orchestrator_connected:
        with tab6:
            st.subheader("✅ Pending Approvals")
            st.markdown("Review and approve/reject tasks requiring human decision")
            
            # Refresh button
            if st.button("🔄 Refresh Pending Tasks", key="refresh_approvals"):
                with st.spinner("Loading pending approvals..."):
                    st.session_state.pending_approvals = check_pending_approvals()
                    st.rerun()
            
            # Initialize pending approvals if not set
            if 'pending_approvals' not in st.session_state:
                st.session_state.pending_approvals = []
            
            pending = st.session_state.pending_approvals
            
            if not pending:
                st.info("🎆 No tasks awaiting approval")
                st.markdown("Tasks that require human review will appear here when their confidence scores are below the threshold.")
            else:
                st.warning(f"⚠️ {len(pending)} tasks awaiting your review")
                
                # Display each pending task
                for idx, review in enumerate(pending):
                    with st.expander(f"Task {idx+1}: {review.get('task_id', 'Unknown')[:8]}...", expanded=idx==0):
                        # Task details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Confidence Score", f"{review.get('confidence_score', 0)*100:.1f}%")
                            st.caption(f"Priority: {review.get('priority', 'MEDIUM')}")
                        with col2:
                            st.metric("Review Type", review.get('review_type', 'APPROVAL'))
                            st.caption(f"Created: {review.get('created_at', 'Unknown')[:19]}")
                        
                        # Context and AI recommendation
                        st.markdown("**Context:**")
                        context = review.get('context', {})
                        if context:
                            st.json(context)
                        
                        if review.get('ai_recommendation'):
                            st.info(f"🤖 AI Recommendation: {review['ai_recommendation']}")
                        
                        # Review actions
                        st.markdown("**Your Decision:**")
                        feedback = st.text_area(
                            "Feedback (optional)",
                            key=f"feedback_{review.get('task_id', idx)}",
                            placeholder="Enter your feedback or reasoning..."
                        )
                        
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("✅ Approve", key=f"approve_{review.get('task_id', idx)}", type="primary"):
                                with st.spinner("Processing approval..."):
                                    if approve_task(review['task_id'], feedback):
                                        st.success("Task approved successfully!")
                                        # Remove from pending list
                                        st.session_state.pending_approvals = [
                                            r for r in st.session_state.pending_approvals 
                                            if r.get('task_id') != review['task_id']
                                        ]
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to approve task")
                        
                        with col2:
                            if st.button("❌ Reject", key=f"reject_{review.get('task_id', idx)}"):
                                with st.spinner("Processing rejection..."):
                                    if reject_task(review['task_id'], feedback):
                                        st.warning("Task rejected")
                                        # Remove from pending list
                                        st.session_state.pending_approvals = [
                                            r for r in st.session_state.pending_approvals 
                                            if r.get('task_id') != review['task_id']
                                        ]
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to reject task")
                        
                        with col3:
                            # Add test identifier for Playwright
                            st.markdown(f'<button data-testid="review-task-{idx}">Review Task</button>', unsafe_allow_html=True)
            
            # Summary metrics
            if pending:
                st.divider()
                st.subheader("📈 Review Statistics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    high_priority = sum(1 for r in pending if r.get('priority') in ['HIGH', 'CRITICAL', 'URGENT'])
                    st.metric("High Priority", high_priority)
                with col2:
                    avg_confidence = sum(r.get('confidence_score', 0) for r in pending) / len(pending) if pending else 0
                    st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
                with col3:
                    st.metric("Total Pending", len(pending))
    
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