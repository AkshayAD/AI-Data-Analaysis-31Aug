#!/usr/bin/env python3
"""
Streamlit Web Application for AI Data Analysis Team
Free deployment on Streamlit Cloud (https://streamlit.io/cloud)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import io
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src" / "python"))

from agents import DataAnalysisAgent, OrchestrationAgent, VisualizationAgent, MLAgent
from agents.intelligent_agent import IntelligentAgent
from llm import GeminiClient

st.set_page_config(
    page_title="AI Data Analysis Team",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def init_agents():
    """Initialize agents once and cache them"""
    agents = {
        'data_analysis': DataAnalysisAgent(),
        'orchestrator': OrchestrationAgent(),
        'visualization': VisualizationAgent(),
        'ml': MLAgent()
    }
    
    if 'GEMINI_API_KEY' in st.secrets:
        try:
            llm_client = GeminiClient(api_key=st.secrets['GEMINI_API_KEY'])
            agents['intelligent'] = IntelligentAgent(llm_client=llm_client)
        except Exception as e:
            st.warning(f"Gemini API not configured: {e}")
    
    return agents

def main():
    st.title("🤖 AI Data Analysis Team")
    st.markdown("### Free AI-Powered Data Analysis Platform")
    
    with st.sidebar:
        st.header("Configuration")
        
        gemini_key = st.text_input(
            "Gemini API Key (optional)",
            type="password",
            help="Enter your Gemini API key for intelligent insights"
        )
        
        if gemini_key:
            st.session_state['gemini_key'] = gemini_key
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app provides:
        - 📊 Data Analysis
        - 📈 Visualizations
        - 🤖 ML Predictions
        - 💡 AI Insights (with Gemini)
        
        **Free Hosting Options:**
        - Streamlit Cloud (recommended)
        - Hugging Face Spaces
        - Render (with limitations)
        """)
    
    tabs = st.tabs(["📤 Upload Data", "📊 Analysis", "📈 Visualizations", "🤖 ML Models", "💡 AI Insights"])
    
    with tabs[0]:
        st.header("Upload Your Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload your dataset for analysis"
        )
        
        use_sample = st.checkbox("Use sample data instead")
        
        if use_sample:
            sample_data = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=30),
                'sales': [100 + i*5 + (i%7)*10 for i in range(30)],
                'customers': [50 + i*2 + (i%5)*5 for i in range(30)],
                'region': ['North', 'South', 'East', 'West'] * 7 + ['North', 'South'],
                'product': ['A', 'B', 'C'] * 10
            })
            st.session_state['data'] = sample_data
            st.success("Sample data loaded!")
            st.dataframe(sample_data.head())
        
        elif uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state['data'] = df
            st.success(f"Uploaded {uploaded_file.name}")
            st.dataframe(df.head())
    
    with tabs[1]:
        st.header("Data Analysis")
        
        if 'data' not in st.session_state:
            st.warning("Please upload data first")
        else:
            df = st.session_state['data']
            agents = init_agents()
            
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Summary Statistics", "Data Quality", "Correlation Analysis"]
            )
            
            if st.button("Run Analysis"):
                with st.spinner("Analyzing..."):
                    if analysis_type == "Summary Statistics":
                        st.subheader("Summary Statistics")
                        st.write(df.describe())
                        
                        task = {
                            'type': 'summary',
                            'data': df.to_dict()
                        }
                        result = agents['data_analysis'].execute(task)
                        
                        if 'summary' in result:
                            st.json(result['summary'])
                    
                    elif analysis_type == "Data Quality":
                        st.subheader("Data Quality Report")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Rows", len(df))
                        with col2:
                            st.metric("Total Columns", len(df.columns))
                        with col3:
                            st.metric("Missing Values", df.isnull().sum().sum())
                        
                        st.write("Missing Values by Column:")
                        missing = df.isnull().sum()
                        st.bar_chart(missing[missing > 0])
                    
                    elif analysis_type == "Correlation Analysis":
                        st.subheader("Correlation Matrix")
                        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                        if len(numeric_cols) > 1:
                            corr = df[numeric_cols].corr()
                            fig = px.imshow(corr, text_auto=True, aspect="auto")
                            st.plotly_chart(fig)
                        else:
                            st.info("Need at least 2 numeric columns for correlation")
    
    with tabs[2]:
        st.header("Visualizations")
        
        if 'data' not in st.session_state:
            st.warning("Please upload data first")
        else:
            df = st.session_state['data']
            agents = init_agents()
            
            viz_type = st.selectbox(
                "Select Visualization",
                ["Histogram", "Scatter Plot", "Line Chart", "Box Plot", "Bar Chart"]
            )
            
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            all_cols = df.columns.tolist()
            
            if viz_type == "Histogram":
                column = st.selectbox("Select column", numeric_cols)
                if st.button("Generate"):
                    fig = px.histogram(df, x=column, title=f"Distribution of {column}")
                    st.plotly_chart(fig)
            
            elif viz_type == "Scatter Plot":
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X axis", numeric_cols)
                with col2:
                    y_col = st.selectbox("Y axis", numeric_cols)
                
                color_col = st.selectbox("Color by (optional)", [None] + all_cols)
                
                if st.button("Generate"):
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                                   title=f"{y_col} vs {x_col}")
                    st.plotly_chart(fig)
            
            elif viz_type == "Line Chart":
                if 'date' in df.columns or df.index.name == 'date':
                    x_col = 'date' if 'date' in df.columns else df.index.name
                    y_col = st.selectbox("Y axis", numeric_cols)
                    
                    if st.button("Generate"):
                        fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over time")
                        st.plotly_chart(fig)
                else:
                    st.info("Line charts work best with time series data")
            
            elif viz_type == "Box Plot":
                value_col = st.selectbox("Value column", numeric_cols)
                group_col = st.selectbox("Group by (optional)", [None] + all_cols)
                
                if st.button("Generate"):
                    if group_col:
                        fig = px.box(df, x=group_col, y=value_col,
                                   title=f"{value_col} by {group_col}")
                    else:
                        fig = px.box(df, y=value_col, title=f"Distribution of {value_col}")
                    st.plotly_chart(fig)
            
            elif viz_type == "Bar Chart":
                if len(all_cols) > 0:
                    category_col = st.selectbox("Category", all_cols)
                    value_col = st.selectbox("Values", numeric_cols) if numeric_cols else None
                    
                    if st.button("Generate"):
                        if value_col:
                            grouped = df.groupby(category_col)[value_col].mean().reset_index()
                            fig = px.bar(grouped, x=category_col, y=value_col,
                                       title=f"Average {value_col} by {category_col}")
                        else:
                            counts = df[category_col].value_counts().reset_index()
                            fig = px.bar(counts, x='index', y=category_col,
                                       title=f"Count of {category_col}")
                        st.plotly_chart(fig)
    
    with tabs[3]:
        st.header("Machine Learning Models")
        
        if 'data' not in st.session_state:
            st.warning("Please upload data first")
        else:
            df = st.session_state['data']
            agents = init_agents()
            
            ml_task = st.selectbox(
                "Select ML Task",
                ["Linear Regression", "Classification", "Clustering", "Time Series Forecast"]
            )
            
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            if ml_task == "Linear Regression":
                if len(numeric_cols) >= 2:
                    target = st.selectbox("Target variable", numeric_cols)
                    features = st.multiselect("Feature variables", 
                                            [c for c in numeric_cols if c != target])
                    
                    if features and st.button("Train Model"):
                        with st.spinner("Training model..."):
                            task = {
                                'type': 'regression',
                                'data': df[features + [target]].to_dict(),
                                'target': target,
                                'features': features
                            }
                            result = agents['ml'].execute(task)
                            
                            if 'metrics' in result:
                                st.success("Model trained successfully!")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("R² Score", f"{result['metrics'].get('r2', 0):.3f}")
                                with col2:
                                    st.metric("RMSE", f"{result['metrics'].get('rmse', 0):.3f}")
                                
                                if 'predictions' in result:
                                    st.line_chart(pd.DataFrame({
                                        'Actual': result['actual'][:50],
                                        'Predicted': result['predictions'][:50]
                                    }))
                else:
                    st.info("Need at least 2 numeric columns for regression")
            
            elif ml_task == "Clustering":
                if len(numeric_cols) >= 2:
                    features = st.multiselect("Select features for clustering", numeric_cols)
                    n_clusters = st.slider("Number of clusters", 2, 10, 3)
                    
                    if features and st.button("Run Clustering"):
                        with st.spinner("Clustering..."):
                            task = {
                                'type': 'clustering',
                                'data': df[features].to_dict(),
                                'n_clusters': n_clusters
                            }
                            result = agents['ml'].execute(task)
                            
                            if 'clusters' in result:
                                st.success("Clustering complete!")
                                df_clustered = df.copy()
                                df_clustered['Cluster'] = result['clusters']
                                
                                if len(features) == 2:
                                    fig = px.scatter(df_clustered, x=features[0], y=features[1],
                                                   color='Cluster', title="Clustering Results")
                                    st.plotly_chart(fig)
                                
                                st.write("Cluster distribution:")
                                st.bar_chart(df_clustered['Cluster'].value_counts())
                else:
                    st.info("Select at least 2 numeric features for clustering")
    
    with tabs[4]:
        st.header("AI-Powered Insights")
        
        if 'data' not in st.session_state:
            st.warning("Please upload data first")
        elif 'gemini_key' not in st.session_state and 'GEMINI_API_KEY' not in st.secrets:
            st.info("Enter your Gemini API key in the sidebar to enable AI insights")
            st.markdown("""
            ### How to get a free Gemini API key:
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy and paste it in the sidebar
            
            **Note:** Free tier includes 60 requests per minute
            """)
        else:
            df = st.session_state['data']
            
            insight_type = st.selectbox(
                "Select Insight Type",
                ["Executive Summary", "Trend Analysis", "Anomaly Detection", 
                 "Recommendations", "Custom Question"]
            )
            
            if insight_type == "Custom Question":
                question = st.text_area("Ask a question about your data")
            else:
                question = None
            
            if st.button("Generate Insights"):
                with st.spinner("Generating AI insights..."):
                    try:
                        api_key = st.session_state.get('gemini_key') or st.secrets.get('GEMINI_API_KEY')
                        llm_client = GeminiClient(api_key=api_key)
                        intelligent_agent = IntelligentAgent(llm_client=llm_client)
                        
                        task = {
                            'type': 'analyze',
                            'data': df.head(100).to_dict(),
                            'insight_type': insight_type.lower().replace(' ', '_'),
                            'question': question
                        }
                        
                        result = intelligent_agent.execute(task)
                        
                        if 'analysis' in result:
                            st.markdown("### AI Analysis")
                            st.markdown(result['analysis'])
                        
                        if 'recommendations' in result:
                            st.markdown("### Recommendations")
                            for rec in result['recommendations']:
                                st.markdown(f"- {rec}")
                        
                        if 'confidence' in result:
                            st.metric("Confidence Score", f"{result['confidence']:.2f}")
                    
                    except Exception as e:
                        st.error(f"Error generating insights: {e}")
    
    st.markdown("---")
    st.markdown("""
    ### Deployment Instructions
    
    **Option 1: Streamlit Cloud (Recommended - 100% Free)**
    1. Push this code to GitHub
    2. Go to [share.streamlit.io](https://share.streamlit.io)
    3. Connect your GitHub repo
    4. Deploy with one click
    5. Add GEMINI_API_KEY in Streamlit secrets (optional)
    
    **Option 2: Local Development**
    ```bash
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```
    
    **Option 3: Hugging Face Spaces (Free)**
    1. Create a Space on Hugging Face
    2. Choose Streamlit SDK
    3. Push this code
    4. Auto-deploys
    """)

if __name__ == "__main__":
    main()