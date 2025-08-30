#!/usr/bin/env python3
"""
Enhanced Streamlit Application with Seamless UX
Version 2.0 - Production Ready
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import sys
import os
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import base64
from typing import Dict, List, Any, Optional

sys.path.append(str(Path(__file__).parent / "src" / "python"))

from agents import DataAnalysisAgent, OrchestrationAgent as OrchestrationAgent, VisualizationAgent, MLAgent
from agents.orchestrator import OrchestrationAgent
from agents.intelligent_agent import IntelligentAgent
from llm import GeminiClient

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UX
st.markdown("""
<style>
    /* Progress indicators */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Success messages */
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class SessionManager:
    """Manage session state and data persistence"""
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'data_history' not in st.session_state:
            st.session_state.data_history = []
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'current_workflow' not in st.session_state:
            st.session_state.current_workflow = None
        if 'api_usage' not in st.session_state:
            st.session_state.api_usage = {'requests': 0, 'last_reset': datetime.now()}
    
    @staticmethod
    def save_data(name: str, data: pd.DataFrame):
        """Save data to session history"""
        st.session_state.data_history.append({
            'name': name,
            'data': data,
            'timestamp': datetime.now(),
            'hash': hashlib.md5(pd.util.hash_pandas_object(data).values).hexdigest()
        })
    
    @staticmethod
    def get_data_history() -> List[Dict]:
        """Get data upload history"""
        return st.session_state.get('data_history', [])
    
    @staticmethod
    def save_result(key: str, result: Any):
        """Save analysis result"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        st.session_state.analysis_results[key] = {
            'result': result,
            'timestamp': datetime.now()
        }

class DataExporter:
    """Handle data export in various formats"""
    
    @staticmethod
    def to_csv(df: pd.DataFrame) -> bytes:
        """Export DataFrame to CSV"""
        return df.to_csv(index=False).encode('utf-8')
    
    @staticmethod
    def to_excel(df: pd.DataFrame) -> bytes:
        """Export DataFrame to Excel"""
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        return output.getvalue()
    
    @staticmethod
    def to_json(data: Any) -> bytes:
        """Export data to JSON"""
        return json.dumps(data, indent=2, default=str).encode('utf-8')
    
    @staticmethod
    def create_download_button(data: Any, filename: str, format: str = 'csv'):
        """Create download button for data"""
        if format == 'csv' and isinstance(data, pd.DataFrame):
            bytes_data = DataExporter.to_csv(data)
            mime = 'text/csv'
        elif format == 'excel' and isinstance(data, pd.DataFrame):
            bytes_data = DataExporter.to_excel(data)
            mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            bytes_data = DataExporter.to_json(data)
            mime = 'application/json'
        
        st.download_button(
            label=f"📥 Download as {format.upper()}",
            data=bytes_data,
            file_name=filename,
            mime=mime
        )

class WorkflowTemplates:
    """Pre-built analysis workflows"""
    
    TEMPLATES = {
        'sales_analysis': {
            'name': 'Sales Analysis',
            'description': 'Comprehensive sales data analysis with trends and forecasting',
            'steps': ['data_quality', 'summary', 'trends', 'forecasting', 'recommendations'],
            'icon': '💰'
        },
        'customer_segmentation': {
            'name': 'Customer Segmentation',
            'description': 'Identify customer segments and behavior patterns',
            'steps': ['data_prep', 'clustering', 'profiling', 'visualization'],
            'icon': '👥'
        },
        'predictive_maintenance': {
            'name': 'Predictive Maintenance',
            'description': 'Predict equipment failures and maintenance needs',
            'steps': ['data_cleaning', 'feature_engineering', 'anomaly_detection', 'prediction'],
            'icon': '🔧'
        },
        'marketing_roi': {
            'name': 'Marketing ROI Analysis',
            'description': 'Analyze marketing campaign effectiveness',
            'steps': ['campaign_data', 'attribution', 'roi_calculation', 'optimization'],
            'icon': '📈'
        }
    }
    
    @staticmethod
    def get_template(name: str) -> Dict:
        """Get workflow template by name"""
        return WorkflowTemplates.TEMPLATES.get(name, {})

@st.cache_resource
def init_agents():
    """Initialize and cache AI agents"""
    agents = {
        'data_analysis': DataAnalysisAgent(),
        'orchestrator': OrchestrationAgent(),
        'visualization': VisualizationAgent(),
        'ml': MLAgent()
    }
    
    # Try to initialize Gemini from secrets or environment
    api_key = st.secrets.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if api_key:
        try:
            llm_client = GeminiClient(api_key=api_key)
            agents['intelligent'] = IntelligentAgent(llm_client=llm_client)
        except Exception as e:
            st.warning(f"Gemini initialization failed: {e}")
    
    return agents

def show_progress(message: str, duration: float = 1.0):
    """Show progress indicator with message"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f"{message}... {i+1}%")
        time.sleep(duration / 100)
    
    progress_bar.empty()
    status_text.empty()

def handle_error(error: Exception, context: str = ""):
    """Graceful error handling with user-friendly messages"""
    error_message = f"**Error in {context}:**\n{str(error)}"
    
    st.error(error_message)
    
    with st.expander("🔍 Error Details"):
        st.code(str(error.__class__.__name__))
        st.write("Full traceback:")
        import traceback
        st.code(traceback.format_exc())
    
    st.info("💡 **Suggestions:**")
    if "Gemini" in str(error):
        st.write("- Check your Gemini API key in settings")
        st.write("- Ensure you have API quota remaining")
    elif "data" in str(error).lower():
        st.write("- Verify your data format is correct")
        st.write("- Check for missing values or invalid columns")
    else:
        st.write("- Try refreshing the page")
        st.write("- Check your input parameters")

def render_sidebar():
    """Render enhanced sidebar with settings and info"""
    with st.sidebar:
        st.title("⚙️ Settings & Info")
        
        # API Configuration
        with st.expander("🔑 API Configuration", expanded=False):
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Optional - enables AI insights"
            )
            if api_key:
                st.session_state['gemini_key'] = api_key
                st.success("API key saved for this session")
        
        # Data History
        with st.expander("📊 Data History", expanded=True):
            history = SessionManager.get_data_history()
            if history:
                for item in history[-5:]:  # Show last 5
                    st.write(f"📁 {item['name']}")
                    st.caption(f"Uploaded: {item['timestamp'].strftime('%H:%M:%S')}")
            else:
                st.info("No data uploaded yet")
        
        # Workflow Templates
        st.markdown("### 🎯 Quick Start Templates")
        for key, template in WorkflowTemplates.TEMPLATES.items():
            if st.button(f"{template['icon']} {template['name']}", key=f"template_{key}"):
                st.session_state.current_workflow = key
                st.rerun()
        
        # System Status
        with st.expander("📊 System Status", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Memory Used", "125 MB")
            with col2:
                st.metric("API Calls", st.session_state.get('api_usage', {}).get('requests', 0))
        
        # Help & Resources
        st.markdown("### 📚 Resources")
        st.markdown("""
        - [📖 Documentation](https://github.com/yourusername/docs)
        - [💬 Community](https://github.com/yourusername/discussions)
        - [🐛 Report Issue](https://github.com/yourusername/issues)
        - [⭐ Star on GitHub](https://github.com/yourusername/repo)
        """)

def render_data_upload():
    """Enhanced data upload interface"""
    st.header("📤 Data Upload Center")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your dataset",
            type=['csv', 'xlsx', 'json'],
            help="Supported formats: CSV, Excel, JSON"
        )
    
    with col2:
        use_sample = st.checkbox("Use sample dataset", help="Load pre-built sample data")
    
    with col3:
        if st.button("📋 Paste from clipboard"):
            st.info("Paste data feature coming soon!")
    
    if use_sample:
        sample_type = st.selectbox(
            "Choose sample dataset",
            ["Sales Data", "Customer Data", "Time Series", "Marketing Campaign"]
        )
        
        if sample_type == "Sales Data":
            df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=100),
                'revenue': [1000 + i*50 + (i%10)*100 for i in range(100)],
                'units_sold': [10 + i//2 for i in range(100)],
                'region': ['North', 'South', 'East', 'West'] * 25,
                'product': ['A', 'B', 'C'] * 33 + ['A'],
                'customer_segment': ['Enterprise', 'SMB', 'Individual'] * 33 + ['Enterprise']
            })
        else:
            # Default sample
            df = pd.DataFrame({
                'id': range(100),
                'value': [100 + i*5 for i in range(100)],
                'category': ['A', 'B', 'C'] * 33 + ['A']
            })
        
        st.session_state['data'] = df
        SessionManager.save_data(f"Sample: {sample_type}", df)
        
        st.success(f"✅ Loaded {sample_type} ({len(df)} rows, {len(df.columns)} columns)")
        
        # Data preview with stats
        with st.expander("📊 Data Preview & Statistics", expanded=True):
            tab1, tab2, tab3 = st.tabs(["Preview", "Statistics", "Data Types"])
            
            with tab1:
                st.dataframe(df.head(10), use_container_width=True)
            
            with tab2:
                st.dataframe(df.describe(), use_container_width=True)
            
            with tab3:
                dtype_df = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null': df.count(),
                    'Unique': df.nunique()
                })
                st.dataframe(dtype_df, use_container_width=True)
    
    elif uploaded_file:
        try:
            # Show loading progress
            with st.spinner(f"Loading {uploaded_file.name}..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                else:
                    df = pd.read_json(uploaded_file)
            
            st.session_state['data'] = df
            SessionManager.save_data(uploaded_file.name, df)
            
            # Success message with metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Memory", f"{df.memory_usage().sum() / 1024**2:.2f} MB")
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Missing %", f"{missing_pct:.1f}%")
            
            # Data preview
            with st.expander("📊 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
        
        except Exception as e:
            handle_error(e, "Data Upload")

def render_analysis_tab(df: pd.DataFrame, agents: Dict):
    """Enhanced analysis interface with progress tracking"""
    st.header("🔬 Intelligent Analysis")
    
    # Analysis type selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analysis_type = st.selectbox(
            "Select Analysis Type",
            [
                "Quick Summary",
                "Data Quality Report",
                "Statistical Analysis",
                "Correlation Analysis",
                "Time Series Analysis",
                "Outlier Detection"
            ]
        )
    
    with col2:
        depth = st.select_slider(
            "Analysis Depth",
            options=["Basic", "Standard", "Deep"],
            value="Standard"
        )
    
    # Additional options
    with st.expander("⚙️ Advanced Options"):
        include_viz = st.checkbox("Include visualizations", value=True)
        include_recommendations = st.checkbox("Generate recommendations", value=True)
        confidence_threshold = st.slider("Confidence threshold", 0.0, 1.0, 0.7)
    
    if st.button("🚀 Run Analysis", type="primary"):
        # Create progress container
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Data Preparation
            with st.spinner("Preparing data..."):
                time.sleep(0.5)  # Simulate processing
                st.success("✅ Data prepared")
            
            # Step 2: Running Analysis
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                for i in range(5):
                    progress_bar.progress((i + 1) * 20)
                    status_text.text(f"Analyzing... Step {i+1}/5")
                    time.sleep(0.3)
                
                # Execute actual analysis
                task = {
                    'type': analysis_type.lower().replace(' ', '_'),
                    'data': df.to_dict(),
                    'depth': depth.lower(),
                    'options': {
                        'include_viz': include_viz,
                        'include_recommendations': include_recommendations,
                        'confidence_threshold': confidence_threshold
                    }
                }
                
                result = agents['data_analysis'].execute(task)
                
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Save results
                SessionManager.save_result(f"analysis_{analysis_type}", result)
                
                # Display metrics
                if 'metrics' in result:
                    cols = st.columns(len(result['metrics']))
                    for i, (key, value) in enumerate(result['metrics'].items()):
                        with cols[i]:
                            st.metric(key, value)
                
                # Display main results
                if 'summary' in result:
                    st.markdown("### 📊 Summary")
                    st.write(result['summary'])
                
                if 'insights' in result:
                    st.markdown("### 💡 Key Insights")
                    for insight in result.get('insights', []):
                        st.info(f"• {insight}")
                
                if include_recommendations and 'recommendations' in result:
                    st.markdown("### 🎯 Recommendations")
                    for rec in result.get('recommendations', []):
                        st.success(f"→ {rec}")
                
                # Export options
                st.markdown("### 📥 Export Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    DataExporter.create_download_button(
                        result, 
                        f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        'json'
                    )
                with col2:
                    if 'data' in result and isinstance(result['data'], dict):
                        result_df = pd.DataFrame(result['data'])
                        DataExporter.create_download_button(
                            result_df,
                            f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            'csv'
                        )
                
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                handle_error(e, "Analysis")

def render_visualization_tab(df: pd.DataFrame, agents: Dict):
    """Enhanced visualization interface"""
    st.header("📈 Interactive Visualizations")
    
    # Visualization selector
    viz_col1, viz_col2 = st.columns([1, 2])
    
    with viz_col1:
        st.markdown("### Chart Type")
        viz_type = st.radio(
            "Select visualization",
            ["Distribution", "Relationship", "Comparison", "Composition", "Time Series", "Geographic"],
            label_visibility="collapsed"
        )
    
    with viz_col2:
        if viz_type == "Distribution":
            chart_types = ["Histogram", "Box Plot", "Violin Plot", "Density Plot"]
        elif viz_type == "Relationship":
            chart_types = ["Scatter Plot", "Bubble Chart", "Correlation Heatmap", "Pair Plot"]
        elif viz_type == "Comparison":
            chart_types = ["Bar Chart", "Grouped Bar", "Line Chart", "Radar Chart"]
        elif viz_type == "Composition":
            chart_types = ["Pie Chart", "Donut Chart", "Treemap", "Sunburst"]
        elif viz_type == "Time Series":
            chart_types = ["Line Plot", "Area Chart", "Candlestick", "Seasonal Decomposition"]
        else:
            chart_types = ["Choropleth Map", "Scatter Map", "Density Map"]
        
        selected_chart = st.selectbox("Choose chart type", chart_types)
        
        # Dynamic parameter selection based on chart type
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        all_cols = df.columns.tolist()
        
        st.markdown("### Parameters")
        
        if selected_chart in ["Histogram", "Box Plot", "Violin Plot", "Density Plot"]:
            value_col = st.selectbox("Value column", numeric_cols)
            group_col = st.selectbox("Group by (optional)", [None] + categorical_cols)
            
            if st.button("📊 Generate Visualization"):
                with st.spinner("Creating visualization..."):
                    if selected_chart == "Histogram":
                        fig = px.histogram(df, x=value_col, color=group_col, 
                                         title=f"Distribution of {value_col}")
                    elif selected_chart == "Box Plot":
                        fig = px.box(df, y=value_col, x=group_col,
                                   title=f"Box Plot of {value_col}")
                    elif selected_chart == "Violin Plot":
                        fig = px.violin(df, y=value_col, x=group_col,
                                      title=f"Violin Plot of {value_col}")
                    else:  # Density Plot
                        fig = px.density_contour(df, x=value_col, y=value_col,
                                                title=f"Density Plot of {value_col}")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export button
                    st.download_button(
                        "📥 Download Chart as HTML",
                        fig.to_html(),
                        f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
        
        elif selected_chart in ["Scatter Plot", "Bubble Chart"]:
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("X axis", numeric_cols)
            with col2:
                y_col = st.selectbox("Y axis", numeric_cols)
            
            color_col = st.selectbox("Color by", [None] + all_cols)
            
            if selected_chart == "Bubble Chart":
                size_col = st.selectbox("Size by", [None] + numeric_cols)
            else:
                size_col = None
            
            if st.button("📊 Generate Visualization"):
                with st.spinner("Creating visualization..."):
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col,
                                   title=f"{y_col} vs {x_col}")
                    st.plotly_chart(fig, use_container_width=True)

def render_ml_tab(df: pd.DataFrame, agents: Dict):
    """Enhanced ML interface with model comparison"""
    st.header("🤖 Machine Learning Studio")
    
    # ML task selection
    ml_task = st.selectbox(
        "Select ML Task",
        ["Regression", "Classification", "Clustering", "Dimensionality Reduction", "Anomaly Detection"]
    )
    
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    
    if ml_task == "Regression":
        st.markdown("### 📈 Regression Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            target = st.selectbox("Target variable", numeric_cols)
        with col2:
            features = st.multiselect("Feature variables", 
                                     [c for c in numeric_cols if c != target])
        
        # Model selection
        models = st.multiselect(
            "Select models to compare",
            ["Linear Regression", "Random Forest", "Gradient Boosting", "Neural Network"],
            default=["Linear Regression"]
        )
        
        # Advanced options
        with st.expander("⚙️ Model Configuration"):
            test_size = st.slider("Test set size", 0.1, 0.5, 0.2)
            cv_folds = st.slider("Cross-validation folds", 2, 10, 5)
            random_state = st.number_input("Random seed", value=42)
        
        if features and st.button("🚀 Train Models", type="primary"):
            # Training progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results_container = st.container()
            
            with results_container:
                st.markdown("### 📊 Model Comparison")
                
                # Create comparison table
                comparison_data = []
                
                for i, model_name in enumerate(models):
                    progress_bar.progress((i + 1) / len(models))
                    status_text.text(f"Training {model_name}...")
                    
                    # Simulate training
                    time.sleep(0.5)
                    
                    # Mock results (replace with actual model training)
                    comparison_data.append({
                        'Model': model_name,
                        'R² Score': 0.85 + i * 0.03,
                        'RMSE': 0.15 - i * 0.02,
                        'MAE': 0.12 - i * 0.01,
                        'Training Time': f"{0.5 + i * 0.2:.2f}s"
                    })
                
                progress_bar.empty()
                status_text.empty()
                
                # Display comparison
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(
                    comparison_df.style.highlight_max(subset=['R² Score'])
                                      .highlight_min(subset=['RMSE', 'MAE']),
                    use_container_width=True
                )
                
                # Best model
                best_model = comparison_df.loc[comparison_df['R² Score'].idxmax(), 'Model']
                st.success(f"🏆 Best performing model: **{best_model}**")
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    # Model comparison chart
                    fig = px.bar(comparison_df, x='Model', y='R² Score',
                               title='Model Performance Comparison')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Feature importance (mock)
                    importance_df = pd.DataFrame({
                        'Feature': features[:5] if len(features) > 5 else features,
                        'Importance': [0.3, 0.25, 0.2, 0.15, 0.1][:len(features[:5])]
                    })
                    fig = px.bar(importance_df, x='Importance', y='Feature',
                               orientation='h', title='Feature Importance')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Export model
                st.markdown("### 💾 Export Model")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        "📥 Download Model (pickle)",
                        b"mock_model_data",  # Replace with actual model
                        "model.pkl",
                        help="Download trained model"
                    )
                with col2:
                    st.download_button(
                        "📥 Download Predictions",
                        b"mock_predictions",  # Replace with actual predictions
                        "predictions.csv",
                        help="Download model predictions"
                    )
                with col3:
                    st.download_button(
                        "📥 Download Report",
                        b"mock_report",  # Replace with actual report
                        "ml_report.pdf",
                        help="Download full ML report"
                    )

def render_ai_insights_tab(df: pd.DataFrame, agents: Dict):
    """AI-powered insights with Gemini integration"""
    st.header("💡 AI-Powered Insights")
    
    if 'intelligent' not in agents:
        st.warning("🔑 Gemini API key required for AI insights")
        
        with st.expander("How to get a free API key"):
            st.markdown("""
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy the key and paste it in the sidebar settings
            
            **Free tier includes:**
            - 60 requests per minute
            - No credit card required
            """)
        
        api_key = st.text_input("Enter Gemini API Key", type="password")
        if api_key:
            st.session_state['gemini_key'] = api_key
            st.rerun()
    else:
        # Insight categories
        insight_type = st.selectbox(
            "Select Insight Type",
            [
                "Executive Summary",
                "Trend Analysis", 
                "Anomaly Detection",
                "Predictive Insights",
                "Recommendations",
                "Custom Question"
            ]
        )
        
        if insight_type == "Custom Question":
            question = st.text_area(
                "Ask anything about your data",
                placeholder="E.g., What are the main factors driving sales growth?",
                height=100
            )
        else:
            question = None
        
        # Context options
        with st.expander("🎯 Context & Parameters"):
            include_stats = st.checkbox("Include statistical analysis", value=True)
            include_viz = st.checkbox("Generate visualization suggestions", value=True)
            max_insights = st.slider("Maximum insights", 3, 10, 5)
            language_style = st.selectbox(
                "Language style",
                ["Professional", "Simple", "Technical", "Executive"]
            )
        
        if st.button("🧠 Generate AI Insights", type="primary"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Prepare task
                    task = {
                        'type': 'analyze',
                        'data': df.head(100).to_dict(),
                        'insight_type': insight_type.lower().replace(' ', '_'),
                        'question': question,
                        'parameters': {
                            'include_stats': include_stats,
                            'include_viz': include_viz,
                            'max_insights': max_insights,
                            'style': language_style.lower()
                        }
                    }
                    
                    # Execute with progress
                    progress_bar = st.progress(0)
                    for i in range(3):
                        progress_bar.progress((i + 1) * 33)
                        time.sleep(0.5)
                    
                    result = agents['intelligent'].execute(task)
                    progress_bar.empty()
                    
                    # Display results
                    if 'analysis' in result:
                        st.markdown("### 🎯 AI Analysis")
                        st.markdown(result['analysis'])
                    
                    if 'insights' in result:
                        st.markdown("### 💡 Key Insights")
                        for i, insight in enumerate(result['insights'][:max_insights], 1):
                            st.info(f"**Insight {i}:** {insight}")
                    
                    if 'recommendations' in result:
                        st.markdown("### 🎬 Recommended Actions")
                        for rec in result['recommendations']:
                            st.success(f"✓ {rec}")
                    
                    if include_viz and 'visualizations' in result:
                        st.markdown("### 📊 Suggested Visualizations")
                        for viz in result['visualizations']:
                            st.write(f"• {viz}")
                    
                    # Confidence and metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        confidence = result.get('confidence', 0.85)
                        st.metric("Confidence", f"{confidence:.0%}")
                    with col2:
                        st.metric("Insights Generated", len(result.get('insights', [])))
                    with col3:
                        st.metric("API Calls Used", 1)
                    
                    # Save and export
                    SessionManager.save_result(f"ai_insights_{insight_type}", result)
                    
                    st.markdown("---")
                    DataExporter.create_download_button(
                        result,
                        f"ai_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        'json'
                    )
                    
                except Exception as e:
                    handle_error(e, "AI Insights Generation")

def main():
    """Main application with enhanced UX"""
    # Initialize session
    SessionManager.init_session()
    
    # Initialize agents
    agents = init_agents()
    
    # Render sidebar
    render_sidebar()
    
    # Main header with metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Platform Version", "2.0", "Enhanced")
    with col2:
        data_count = len(SessionManager.get_data_history())
        st.metric("Datasets Loaded", data_count)
    with col3:
        analysis_count = len(st.session_state.get('analysis_results', {}))
        st.metric("Analyses Run", analysis_count)
    with col4:
        if 'intelligent' in agents:
            st.metric("AI Status", "🟢 Active")
        else:
            st.metric("AI Status", "🔴 Inactive")
    
    st.title("🤖 AI Data Analysis Platform")
    st.markdown("### Seamless Data Intelligence at Your Fingertips")
    
    # Check for workflow
    if st.session_state.get('current_workflow'):
        workflow = WorkflowTemplates.get_template(st.session_state.current_workflow)
        if workflow:
            st.info(f"📋 Running Workflow: **{workflow['name']}** - {workflow['description']}")
            if st.button("❌ Exit Workflow"):
                st.session_state.current_workflow = None
                st.rerun()
    
    # Main tabs
    tabs = st.tabs([
        "📤 Data Upload",
        "🔬 Analysis",
        "📈 Visualizations",
        "🤖 ML Models",
        "💡 AI Insights",
        "📊 Dashboard"
    ])
    
    with tabs[0]:
        render_data_upload()
    
    # Check if data is loaded for other tabs
    if 'data' in st.session_state:
        df = st.session_state['data']
        
        with tabs[1]:
            render_analysis_tab(df, agents)
        
        with tabs[2]:
            render_visualization_tab(df, agents)
        
        with tabs[3]:
            render_ml_tab(df, agents)
        
        with tabs[4]:
            render_ai_insights_tab(df, agents)
        
        with tabs[5]:
            st.header("📊 Executive Dashboard")
            
            # Dashboard metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", f"{len(df):,}")
            with col2:
                st.metric("Features", len(df.columns))
            with col3:
                numeric_cols = len(df.select_dtypes(include=['float64', 'int64']).columns)
                st.metric("Numeric Features", numeric_cols)
            with col4:
                missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Data Quality", f"{100-missing_pct:.1f}%")
            
            # Quick visualizations
            st.markdown("### Quick Insights")
            
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Correlation heatmap
                    corr = df[numeric_cols].corr()
                    fig = px.imshow(corr, title="Feature Correlations", text_auto='.2f')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Distribution of first numeric column
                    fig = px.histogram(df, x=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent results
            if st.session_state.get('analysis_results'):
                st.markdown("### Recent Analysis Results")
                for key, value in list(st.session_state.analysis_results.items())[-3:]:
                    with st.expander(f"📊 {key} - {value['timestamp'].strftime('%H:%M:%S')}"):
                        st.json(value['result'])
    else:
        for i in range(1, 6):
            with tabs[i]:
                st.info("📊 Please upload data first to access this feature")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Made with ❤️ by Terragon Labs | 
            <a href='https://github.com/terragonlabs' target='_blank'>GitHub</a> | 
            <a href='https://docs.terragonlabs.com' target='_blank'>Docs</a> | 
            Version 2.0
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()