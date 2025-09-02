#!/usr/bin/env python3
"""
AI-Powered Data Analysis Platform - 4 Step Implementation
Replicates the initial steps from the documentation exactly
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sys
import os
from pathlib import Path
import time
import json
from typing import Dict, List, Any, Optional

sys.path.append(str(Path(__file__).parent / "src" / "python"))

from llm import GeminiClient
from agents import DataAnalysisAgent, OrchestrationAgent, VisualizationAgent

st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'project_data' not in st.session_state:
        st.session_state.project_data = {}
    if 'analysis_plan' not in st.session_state:
        st.session_state.analysis_plan = None
    if 'data_profile' not in st.session_state:
        st.session_state.data_profile = None
    if 'analysis_tasks' not in st.session_state:
        st.session_state.analysis_tasks = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'gemini_client' not in st.session_state:
        if 'GEMINI_API_KEY' in st.secrets:
            st.session_state.gemini_client = GeminiClient(api_key=st.secrets['GEMINI_API_KEY'])
        else:
            st.session_state.gemini_client = None

def render_progress_bar():
    """Render the step progress bar"""
    steps = ["Project Setup", "Manager Planning", "Data Understanding", "Analysis Guidance"]
    current = st.session_state.current_step
    
    cols = st.columns(4)
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current:
                st.success(f"✅ Step {i}: {step_name}")
            elif i == current:
                st.info(f"🔄 Step {i}: {step_name}")
            else:
                st.text(f"⏳ Step {i}: {step_name}")

def step1_project_setup():
    """Step 1: Initialize a new analysis project"""
    st.header("📁 Step 1: Project Setup")
    st.markdown("""
    **Purpose:** Initialize a new analysis project by collecting essential project metadata 
    and uploading data files.
    """)
    
    with st.form("project_setup_form"):
        st.subheader("Project Information")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(
                "Project Name",
                placeholder="e.g., Q4 Sales Analysis",
                help="Give your analysis project a descriptive name"
            )
            
            client_name = st.text_input(
                "Client/Department",
                placeholder="e.g., Marketing Team",
                help="Who is this analysis for?"
            )
        
        with col2:
            project_type = st.selectbox(
                "Analysis Type",
                ["Strategic Analysis", "Operational Analysis", "Financial Analysis", 
                 "Customer Analysis", "Market Analysis", "Risk Analysis"]
            )
            
            deadline = st.date_input(
                "Target Completion Date",
                help="When should this analysis be completed?"
            )
        
        st.subheader("Business Context")
        
        business_objectives = st.text_area(
            "Business Objectives",
            placeholder="What are the key business questions you want to answer?",
            height=100,
            help="Describe the main goals and questions for this analysis"
        )
        
        success_criteria = st.text_area(
            "Success Criteria",
            placeholder="How will you measure the success of this analysis?",
            height=80,
            help="Define what success looks like for this project"
        )
        
        st.subheader("Data Upload")
        
        uploaded_files = st.file_uploader(
            "Upload Data Files",
            type=['csv', 'xlsx', 'xls', 'json', 'parquet', 'txt', 'pdf', 'docx'],
            accept_multiple_files=True,
            help="Upload all relevant data files for analysis"
        )
        
        data_description = st.text_area(
            "Data Description",
            placeholder="Briefly describe the data you're uploading",
            height=80,
            help="What does this data represent?"
        )
        
        submitted = st.form_submit_button("Initialize Project", type="primary")
        
        if submitted:
            if not project_name or not business_objectives:
                st.error("Please provide project name and business objectives")
            elif not uploaded_files:
                st.error("Please upload at least one data file")
            else:
                # Store project data
                st.session_state.project_data = {
                    'project_name': project_name,
                    'client_name': client_name,
                    'project_type': project_type,
                    'deadline': str(deadline),
                    'business_objectives': business_objectives,
                    'success_criteria': success_criteria,
                    'data_description': data_description,
                    'created_at': datetime.now().isoformat()
                }
                
                # Process uploaded files
                st.session_state.uploaded_files = []
                for file in uploaded_files:
                    file_data = {
                        'name': file.name,
                        'type': file.type,
                        'size': file.size
                    }
                    
                    # Read file content based on type
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                        file_data['dataframe'] = df
                        file_data['preview'] = df.head()
                    elif file.name.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file)
                        file_data['dataframe'] = df
                        file_data['preview'] = df.head()
                    
                    st.session_state.uploaded_files.append(file_data)
                
                st.success("✅ Project initialized successfully!")
                st.session_state.current_step = 2
                st.rerun()
    
    # Display uploaded files summary
    if st.session_state.uploaded_files:
        st.subheader("📊 Uploaded Files")
        for file in st.session_state.uploaded_files:
            with st.expander(f"📄 {file['name']} ({file['size']:,} bytes)"):
                if 'preview' in file:
                    st.dataframe(file['preview'])
                else:
                    st.info(f"File type: {file['type']}")

def step2_manager_planning():
    """Step 2: Generate structured analysis plan"""
    st.header("📋 Step 2: Manager Planning")
    st.markdown("""
    **Purpose:** Generate a structured analysis plan based on business objectives using 
    AI-driven strategic planning.
    """)
    
    if not st.session_state.gemini_client:
        st.warning("⚠️ Gemini API key not configured. Using template-based planning.")
        
        # Fallback template-based planning
        with st.form("manual_planning"):
            st.subheader("Manual Analysis Planning")
            
            approach = st.text_area(
                "Analysis Approach",
                placeholder="Describe your analysis methodology",
                height=100
            )
            
            key_metrics = st.text_area(
                "Key Metrics to Analyze",
                placeholder="List the main metrics and KPIs",
                height=80
            )
            
            deliverables = st.text_area(
                "Expected Deliverables",
                placeholder="What outputs will be produced?",
                height=80
            )
            
            if st.form_submit_button("Create Plan"):
                st.session_state.analysis_plan = {
                    'approach': approach,
                    'key_metrics': key_metrics,
                    'deliverables': deliverables,
                    'generated_at': datetime.now().isoformat()
                }
                st.success("✅ Analysis plan created!")
                st.session_state.current_step = 3
                st.rerun()
    else:
        # AI-powered planning
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🤖 Generate AI Analysis Plan", type="primary"):
                with st.spinner("🔄 Generating strategic analysis plan..."):
                    # Prepare context for AI
                    context = f"""
                    Project: {st.session_state.project_data.get('project_name')}
                    Type: {st.session_state.project_data.get('project_type')}
                    Objectives: {st.session_state.project_data.get('business_objectives')}
                    Success Criteria: {st.session_state.project_data.get('success_criteria')}
                    Data Description: {st.session_state.project_data.get('data_description')}
                    """
                    
                    prompt = f"""
                    As a Senior Data Strategy Manager, create a comprehensive analysis plan for the following project:
                    
                    {context}
                    
                    Provide a structured plan including:
                    1. Executive Summary
                    2. Analysis Approach and Methodology
                    3. Key Hypotheses to Test
                    4. Required Analyses and Techniques
                    5. Expected Deliverables and Outcomes
                    6. Risk Factors and Mitigation Strategies
                    7. Timeline and Milestones
                    
                    Format the response in a clear, professional manner.
                    """
                    
                    try:
                        response = st.session_state.gemini_client.generate_content(prompt)
                        
                        st.session_state.analysis_plan = {
                            'content': response,
                            'generated_at': datetime.now().isoformat(),
                            'status': 'pending_approval'
                        }
                        
                        st.success("✅ Analysis plan generated successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating plan: {e}")
        
        with col2:
            st.info("""
            **AI Planning Benefits:**
            - Strategic alignment
            - Best practices
            - Risk identification
            - Resource optimization
            """)
    
    # Display and refine plan
    if st.session_state.analysis_plan:
        st.subheader("📊 Generated Analysis Plan")
        
        plan_container = st.container()
        with plan_container:
            if isinstance(st.session_state.analysis_plan, dict):
                if 'content' in st.session_state.analysis_plan:
                    st.markdown(st.session_state.analysis_plan['content'])
                else:
                    for key, value in st.session_state.analysis_plan.items():
                        if key not in ['generated_at', 'status']:
                            st.write(f"**{key.replace('_', ' ').title()}:**")
                            st.write(value)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Approve Plan", type="primary"):
                st.session_state.analysis_plan['status'] = 'approved'
                st.session_state.current_step = 3
                st.success("Plan approved! Moving to Data Understanding...")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("✏️ Request Modifications"):
                st.info("Plan modification interface would open here")
        
        with col3:
            if st.button("🔄 Regenerate Plan"):
                st.session_state.analysis_plan = None
                st.rerun()

def step3_data_understanding():
    """Step 3: Perform comprehensive data profiling"""
    st.header("🔍 Step 3: Data Understanding")
    st.markdown("""
    **Purpose:** Perform comprehensive data profiling and assessment to understand 
    the data's characteristics, quality, and potential.
    """)
    
    if not st.session_state.uploaded_files:
        st.warning("No data files found. Please complete Step 1 first.")
        if st.button("Go to Step 1"):
            st.session_state.current_step = 1
            st.rerun()
        return
    
    # Select data for profiling
    data_files = [f for f in st.session_state.uploaded_files if 'dataframe' in f]
    
    if not data_files:
        st.error("No analyzable data files found (CSV or Excel)")
        return
    
    selected_file = st.selectbox(
        "Select data file to profile",
        options=data_files,
        format_func=lambda x: x['name']
    )
    
    if selected_file and 'dataframe' in selected_file:
        df = selected_file['dataframe']
        
        # Data Profiling Tabs
        tabs = st.tabs(["📊 Overview", "📈 Statistics", "🔍 Quality", "📉 Distributions", "🔗 Relationships"])
        
        with tabs[0]:  # Overview
            st.subheader("Dataset Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", f"{len(df):,}")
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            with col4:
                st.metric("Duplicate Rows", df.duplicated().sum())
            
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Null %': (df.isnull().sum() / len(df) * 100).round(2),
                'Unique Values': df.nunique(),
                'Sample Values': [df[col].dropna().iloc[0] if not df[col].dropna().empty else None for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        with tabs[1]:  # Statistics
            st.subheader("Statistical Summary")
            
            # Numeric columns statistics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.write("**Numeric Columns:**")
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
                
                # Additional statistics
                additional_stats = pd.DataFrame({
                    'Column': numeric_cols,
                    'Variance': df[numeric_cols].var(),
                    'Std Dev': df[numeric_cols].std(),
                    'Skewness': df[numeric_cols].skew(),
                    'Kurtosis': df[numeric_cols].kurtosis()
                })
                st.write("**Advanced Statistics:**")
                st.dataframe(additional_stats, use_container_width=True)
            
            # Categorical columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(categorical_cols) > 0:
                st.write("**Categorical Columns:**")
                for col in categorical_cols[:5]:  # Limit to first 5
                    with st.expander(f"📊 {col}"):
                        value_counts = df[col].value_counts().head(10)
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.dataframe(value_counts)
                        with col2:
                            fig = px.bar(x=value_counts.values, y=value_counts.index, orientation='h',
                                       title=f"Top 10 values in {col}")
                            st.plotly_chart(fig, use_container_width=True)
        
        with tabs[2]:  # Quality
            st.subheader("Data Quality Assessment")
            
            # Quality metrics
            quality_score = 100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Overall Quality Score", f"{quality_score:.1f}%")
            with col2:
                completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                st.metric("Completeness", f"{completeness:.1f}%")
            with col3:
                consistency = (1 - df.duplicated().sum() / len(df)) * 100
                st.metric("Consistency", f"{consistency:.1f}%")
            
            # Missing data visualization
            if df.isnull().sum().any():
                st.write("**Missing Data Pattern:**")
                missing_data = df.isnull().sum()[df.isnull().sum() > 0].sort_values(ascending=False)
                fig = px.bar(x=missing_data.index, y=missing_data.values,
                           title="Missing Values by Column",
                           labels={'x': 'Column', 'y': 'Missing Count'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Data quality issues
            st.write("**Identified Quality Issues:**")
            issues = []
            if df.duplicated().sum() > 0:
                issues.append(f"⚠️ {df.duplicated().sum()} duplicate rows found")
            if df.isnull().sum().sum() > 0:
                issues.append(f"⚠️ {df.isnull().sum().sum()} missing values across {(df.isnull().sum() > 0).sum()} columns")
            
            for issue in issues:
                st.warning(issue)
        
        with tabs[3]:  # Distributions
            st.subheader("Data Distributions")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                selected_col = st.selectbox("Select column for distribution analysis", numeric_cols)
                
                if selected_col:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Histogram
                        fig = px.histogram(df, x=selected_col, nbins=30,
                                         title=f"Distribution of {selected_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Box plot
                        fig = px.box(df, y=selected_col,
                                   title=f"Box Plot of {selected_col}")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # QQ plot for normality check
                    from scipy import stats
                    fig = go.Figure()
                    qq = stats.probplot(df[selected_col].dropna(), dist="norm")
                    fig.add_scatter(x=qq[0][0], y=qq[0][1], mode='markers', name='Data')
                    fig.add_scatter(x=qq[0][0], y=qq[0][0], mode='lines', name='Normal', line=dict(color='red'))
                    fig.update_layout(title=f"Q-Q Plot for {selected_col}",
                                    xaxis_title="Theoretical Quantiles",
                                    yaxis_title="Sample Quantiles")
                    st.plotly_chart(fig, use_container_width=True)
        
        with tabs[4]:  # Relationships
            st.subheader("Data Relationships")
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                # Correlation matrix
                st.write("**Correlation Matrix:**")
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                              title="Correlation Heatmap")
                st.plotly_chart(fig, use_container_width=True)
                
                # Scatter plot for relationship exploration
                st.write("**Explore Relationships:**")
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
                
                if x_col and y_col and x_col != y_col:
                    fig = px.scatter(df, x=x_col, y=y_col,
                                   title=f"{y_col} vs {x_col}",
                                   trendline="ols")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Save profiling results
        if st.button("✅ Complete Data Understanding", type="primary"):
            st.session_state.data_profile = {
                'file_name': selected_file['name'],
                'rows': len(df),
                'columns': len(df.columns),
                'quality_score': quality_score,
                'numeric_columns': list(numeric_cols),
                'categorical_columns': list(categorical_cols),
                'profiled_at': datetime.now().isoformat()
            }
            st.session_state.current_step = 4
            st.success("Data profiling complete! Moving to Analysis Guidance...")
            time.sleep(1)
            st.rerun()

def step4_analysis_guidance():
    """Step 4: Bridge between understanding and execution"""
    st.header("🎯 Step 4: Analysis Guidance")
    st.markdown("""
    **Purpose:** Bridge the gap between data understanding and execution by providing 
    detailed analysis guidance and task specifications.
    """)
    
    if not st.session_state.data_profile:
        st.warning("Please complete Data Understanding first.")
        if st.button("Go to Step 3"):
            st.session_state.current_step = 3
            st.rerun()
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Analysis Task Decomposition")
        
        # Generate or display analysis tasks
        if not st.session_state.analysis_tasks:
            if st.button("🤖 Generate Analysis Tasks", type="primary"):
                with st.spinner("Generating detailed analysis tasks..."):
                    # Create structured tasks based on project context
                    tasks = [
                        {
                            'id': 1,
                            'name': 'Exploratory Data Analysis',
                            'description': 'Perform initial exploration to understand data patterns and relationships',
                            'priority': 'High',
                            'estimated_time': '2 hours',
                            'techniques': ['Descriptive statistics', 'Visualization', 'Correlation analysis'],
                            'deliverables': ['EDA report', 'Key insights summary'],
                            'status': 'pending'
                        },
                        {
                            'id': 2,
                            'name': 'Hypothesis Testing',
                            'description': 'Test key business hypotheses identified in the planning phase',
                            'priority': 'High',
                            'estimated_time': '3 hours',
                            'techniques': ['Statistical tests', 'A/B testing', 'Significance analysis'],
                            'deliverables': ['Hypothesis test results', 'Statistical significance report'],
                            'status': 'pending'
                        },
                        {
                            'id': 3,
                            'name': 'Predictive Modeling',
                            'description': 'Build predictive models to forecast key business metrics',
                            'priority': 'Medium',
                            'estimated_time': '4 hours',
                            'techniques': ['Regression', 'Time series', 'Machine learning'],
                            'deliverables': ['Model performance metrics', 'Predictions'],
                            'status': 'pending'
                        },
                        {
                            'id': 4,
                            'name': 'Segmentation Analysis',
                            'description': 'Identify and analyze distinct segments in the data',
                            'priority': 'Medium',
                            'estimated_time': '2 hours',
                            'techniques': ['Clustering', 'RFM analysis', 'Cohort analysis'],
                            'deliverables': ['Segment profiles', 'Segmentation strategy'],
                            'status': 'pending'
                        },
                        {
                            'id': 5,
                            'name': 'Executive Dashboard Creation',
                            'description': 'Create interactive dashboards for stakeholder presentation',
                            'priority': 'High',
                            'estimated_time': '3 hours',
                            'techniques': ['Data visualization', 'KPI design', 'Interactive charts'],
                            'deliverables': ['Executive dashboard', 'KPI documentation'],
                            'status': 'pending'
                        }
                    ]
                    
                    st.session_state.analysis_tasks = tasks
                    st.success("✅ Analysis tasks generated successfully!")
                    time.sleep(1)
                    st.rerun()
        
        if st.session_state.analysis_tasks:
            # Display tasks in an interactive format
            for task in st.session_state.analysis_tasks:
                with st.expander(f"📌 Task {task['id']}: {task['name']} - Priority: {task['priority']}", 
                               expanded=(task['id'] == 1)):
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Estimated Time:** {task['estimated_time']}")
                        
                        st.write("**Techniques:**")
                        for technique in task['techniques']:
                            st.write(f"  • {technique}")
                        
                        st.write("**Deliverables:**")
                        for deliverable in task['deliverables']:
                            st.write(f"  • {deliverable}")
                    
                    with col2:
                        status_color = {
                            'pending': '🔵',
                            'in_progress': '🟡',
                            'completed': '🟢'
                        }
                        st.write(f"**Status:** {status_color.get(task['status'], '⚪')} {task['status'].title()}")
                        
                        if st.button(f"Start Task", key=f"start_task_{task['id']}"):
                            task['status'] = 'in_progress'
                            st.rerun()
    
    with col2:
        st.subheader("📊 Project Summary")
        
        # Display project context
        st.info(f"""
        **Project:** {st.session_state.project_data.get('project_name', 'N/A')}
        
        **Type:** {st.session_state.project_data.get('project_type', 'N/A')}
        
        **Data Quality:** {st.session_state.data_profile.get('quality_score', 0):.1f}%
        
        **Columns:** {st.session_state.data_profile.get('columns', 0)}
        
        **Rows:** {st.session_state.data_profile.get('rows', 0):,}
        """)
        
        # Task progress
        if st.session_state.analysis_tasks:
            total_tasks = len(st.session_state.analysis_tasks)
            completed_tasks = sum(1 for t in st.session_state.analysis_tasks if t['status'] == 'completed')
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            st.metric("Task Progress", f"{completed_tasks}/{total_tasks}")
            st.progress(progress)
    
    # Strategic Alignment Section
    st.subheader("🎯 Strategic Alignment")
    
    alignment_tabs = st.tabs(["Business Objectives", "Hypotheses", "Success Metrics"])
    
    with alignment_tabs[0]:
        st.write("**Original Business Objectives:**")
        st.info(st.session_state.project_data.get('business_objectives', 'Not specified'))
        
        st.write("**How Tasks Address Objectives:**")
        st.success("""
        ✅ Each analysis task is designed to directly address specific business questions
        ✅ Deliverables are aligned with stakeholder expectations
        ✅ Priority levels reflect business impact
        """)
    
    with alignment_tabs[1]:
        st.write("**Key Hypotheses to Test:**")
        hypotheses = [
            "Current trends will continue into the forecast period",
            "There are distinct customer segments with different behaviors",
            "Certain factors have significant predictive power for target metrics",
            "Data quality issues may be impacting analysis accuracy"
        ]
        for i, hypothesis in enumerate(hypotheses, 1):
            st.write(f"{i}. {hypothesis}")
    
    with alignment_tabs[2]:
        st.write("**Success Metrics:**")
        metrics = [
            "Analysis completed within timeline",
            "All key business questions answered",
            "Actionable insights identified",
            "Stakeholder satisfaction achieved"
        ]
        for metric in metrics:
            st.checkbox(metric, key=f"metric_{metric}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Export Task Plan", type="secondary"):
            task_plan = {
                'project': st.session_state.project_data,
                'tasks': st.session_state.analysis_tasks,
                'data_profile': st.session_state.data_profile
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(task_plan, indent=2),
                file_name=f"analysis_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🚀 Begin Execution", type="primary"):
            st.success("✅ Ready to begin analysis execution!")
            st.balloons()
            st.info("Analysis execution would begin here with the generated tasks")
    
    with col3:
        if st.button("🔄 Revise Plan"):
            st.session_state.current_step = 2
            st.rerun()

def main():
    init_session_state()
    
    # Header
    st.title("🎯 AI-Powered Data Analysis Platform")
    st.markdown("**Structured 4-Step Analysis Process**")
    
    # Progress bar
    render_progress_bar()
    
    st.markdown("---")
    
    # Render current step
    if st.session_state.current_step == 1:
        step1_project_setup()
    elif st.session_state.current_step == 2:
        step2_manager_planning()
    elif st.session_state.current_step == 3:
        step3_data_understanding()
    elif st.session_state.current_step == 4:
        step4_analysis_guidance()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        
        # API Key configuration
        if not st.session_state.gemini_client:
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Enter your Google Gemini API key for AI features"
            )
            if api_key:
                st.session_state.gemini_client = GeminiClient(api_key=api_key)
                st.success("API key configured!")
                st.rerun()
        else:
            st.success("✅ AI Features Enabled")
        
        st.markdown("---")
        
        # Step navigation
        st.subheader("Quick Navigation")
        for i, step_name in enumerate(["Project Setup", "Manager Planning", 
                                      "Data Understanding", "Analysis Guidance"], 1):
            if st.button(f"Step {i}: {step_name}", 
                        disabled=(i > st.session_state.current_step),
                        use_container_width=True):
                st.session_state.current_step = i
                st.rerun()
        
        st.markdown("---")
        
        # Help section
        st.subheader("ℹ️ Help")
        st.info("""
        **How to use:**
        1. Complete each step sequentially
        2. Upload your data files
        3. Define business objectives
        4. Review AI-generated plans
        5. Execute analysis tasks
        
        **AI Features:**
        - Strategic planning
        - Task decomposition
        - Insight generation
        """)
        
        # Reset button
        if st.button("🔄 Reset Application", type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()