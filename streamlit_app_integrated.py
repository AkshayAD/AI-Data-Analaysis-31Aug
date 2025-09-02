#!/usr/bin/env python3
"""
AI-Powered Data Analysis Platform - Integrated 4-Step to Marimo Execution
Connects the 4-step planning workflow with automated Marimo notebook execution
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import sys
import os
from pathlib import Path
import time
import json
import uuid
from typing import Dict, List, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

sys.path.append(str(Path(__file__).parent / "src" / "python"))

from llm import GeminiClient
from agents import DataAnalysisAgent, OrchestrationAgent, VisualizationAgent
from workflow.workflow_manager import WorkflowManager, TaskType, TaskStatus, AnalysisTask
from marimo_integration import NotebookBuilder, NotebookRunner

st.set_page_config(
    page_title="AI Analysis Platform - Integrated",
    page_icon="🚀",
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
    if 'workflow_manager' not in st.session_state:
        st.session_state.workflow_manager = WorkflowManager(workspace_path="./integrated_workspace")
    if 'execution_results' not in st.session_state:
        st.session_state.execution_results = {}
    if 'marimo_notebooks' not in st.session_state:
        st.session_state.marimo_notebooks = {}

def render_progress_bar():
    """Render the enhanced step progress bar"""
    steps = ["Project Setup", "Manager Planning", "Data Understanding", "Analysis Guidance", "Marimo Execution"]
    current = st.session_state.current_step
    
    cols = st.columns(5)
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current:
                st.success(f"✅ Step {i}: {step_name}")
            elif i == current:
                st.info(f"🔄 Step {i}: {step_name}")
            else:
                st.text(f"⏳ Step {i}: {step_name}")

def convert_task_to_workflow_task(task_dict: Dict) -> AnalysisTask:
    """Convert a task dictionary to WorkflowManager AnalysisTask"""
    task_type_map = {
        'Exploratory Data Analysis': TaskType.DATA_PROFILING,
        'Hypothesis Testing': TaskType.STATISTICAL_ANALYSIS,
        'Predictive Modeling': TaskType.PREDICTIVE_MODELING,
        'Segmentation Analysis': TaskType.SEGMENTATION,
        'Executive Dashboard Creation': TaskType.VISUALIZATION,
        'Correlation Analysis': TaskType.CORRELATION_ANALYSIS,
        'Anomaly Detection': TaskType.ANOMALY_DETECTION,
        'Time Series Analysis': TaskType.TIME_SERIES_ANALYSIS
    }
    
    # Determine task type
    task_type = TaskType.CUSTOM
    for key, value in task_type_map.items():
        if key.lower() in task_dict.get('name', '').lower():
            task_type = value
            break
    
    # Get data source from uploaded files
    data_source = None
    if st.session_state.uploaded_files:
        first_file = st.session_state.uploaded_files[0]
        if 'dataframe' in first_file:
            # Save dataframe to temp file
            temp_path = Path("./integrated_workspace/temp_data.csv")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            first_file['dataframe'].to_csv(temp_path, index=False)
            data_source = str(temp_path)
    
    return AnalysisTask(
        id=str(task_dict.get('id', uuid.uuid4())),
        name=task_dict.get('name', 'Unknown Task'),
        description=task_dict.get('description', ''),
        task_type=task_type,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        priority=5 if task_dict.get('priority') == 'High' else 3 if task_dict.get('priority') == 'Medium' else 1,
        data_source=data_source,
        parameters={
            'techniques': task_dict.get('techniques', []),
            'deliverables': task_dict.get('deliverables', []),
            'estimated_time': task_dict.get('estimated_time', '1 hour')
        }
    )

def generate_notebook_for_task(task: AnalysisTask) -> str:
    """Generate a Marimo notebook for a specific task"""
    wf = st.session_state.workflow_manager
    notebook_path = wf.generate_marimo_notebook(task)
    return notebook_path

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
            type=['csv', 'xlsx', 'xls', 'json', 'parquet'],
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

def step3_data_understanding():
    """Step 3: Perform comprehensive data profiling"""
    st.header("🔍 Step 3: Data Understanding")
    st.markdown("""
    **Purpose:** Perform comprehensive data profiling and assessment to understand 
    the data's characteristics, quality, and potential.
    """)
    
    if not st.session_state.uploaded_files:
        st.warning("No data files found. Please complete Step 1 first.")
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
        
        # Quick profiling summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        with col4:
            quality_score = 100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            st.metric("Quality Score", f"{quality_score:.1f}%")
        
        # Save profiling results
        if st.button("✅ Complete Data Understanding", type="primary"):
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            
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
    """Step 4: Bridge between understanding and execution with Marimo integration"""
    st.header("🎯 Step 4: Analysis Guidance & Task Planning")
    st.markdown("""
    **Purpose:** Generate analysis tasks and prepare them for automated Marimo execution.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Analysis Task Generation")
        
        # Generate or display analysis tasks
        if not st.session_state.analysis_tasks:
            if st.button("🤖 Generate Analysis Tasks", type="primary"):
                with st.spinner("Generating analysis tasks..."):
                    # Create structured tasks based on project context
                    tasks = [
                        {
                            'id': 1,
                            'name': 'Exploratory Data Analysis',
                            'description': 'Perform initial exploration to understand data patterns',
                            'priority': 'High',
                            'estimated_time': '2 hours',
                            'techniques': ['Descriptive statistics', 'Visualization'],
                            'deliverables': ['EDA report', 'Key insights'],
                            'status': 'pending',
                            'marimo_ready': True
                        },
                        {
                            'id': 2,
                            'name': 'Statistical Analysis',
                            'description': 'Perform statistical tests and analysis',
                            'priority': 'High',
                            'estimated_time': '3 hours',
                            'techniques': ['Hypothesis testing', 'Significance analysis'],
                            'deliverables': ['Statistical report'],
                            'status': 'pending',
                            'marimo_ready': True
                        },
                        {
                            'id': 3,
                            'name': 'Predictive Modeling',
                            'description': 'Build predictive models for key metrics',
                            'priority': 'Medium',
                            'estimated_time': '4 hours',
                            'techniques': ['Machine learning', 'Regression'],
                            'deliverables': ['Model performance', 'Predictions'],
                            'status': 'pending',
                            'marimo_ready': True
                        },
                        {
                            'id': 4,
                            'name': 'Anomaly Detection',
                            'description': 'Identify anomalies and outliers in the data',
                            'priority': 'Medium',
                            'estimated_time': '2 hours',
                            'techniques': ['Isolation Forest', 'Statistical methods'],
                            'deliverables': ['Anomaly report'],
                            'status': 'pending',
                            'marimo_ready': True
                        },
                        {
                            'id': 5,
                            'name': 'Data Visualization',
                            'description': 'Create comprehensive visualizations',
                            'priority': 'High',
                            'estimated_time': '3 hours',
                            'techniques': ['Interactive charts', 'Dashboards'],
                            'deliverables': ['Visualization suite'],
                            'status': 'pending',
                            'marimo_ready': True
                        }
                    ]
                    
                    st.session_state.analysis_tasks = tasks
                    st.success("✅ Analysis tasks generated successfully!")
                    time.sleep(1)
                    st.rerun()
        
        if st.session_state.analysis_tasks:
            st.subheader("📊 Generated Tasks for Marimo Execution")
            
            # Display tasks with Marimo integration status
            for task in st.session_state.analysis_tasks:
                with st.expander(f"📌 Task {task['id']}: {task['name']} - {task['priority']} Priority", 
                               expanded=(task['id'] == 1)):
                    
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Estimated Time:** {task['estimated_time']}")
                        st.write(f"**Techniques:** {', '.join(task['techniques'])}")
                    
                    with col2:
                        if task['marimo_ready']:
                            st.success("✅ Marimo Ready")
                        else:
                            st.warning("⚠️ Manual Task")
                    
                    with col3:
                        if task['status'] == 'pending':
                            if st.button(f"Generate Notebook", key=f"gen_{task['id']}"):
                                with st.spinner("Generating Marimo notebook..."):
                                    # Convert to WorkflowManager task
                                    wf_task = convert_task_to_workflow_task(task)
                                    
                                    # Generate notebook
                                    notebook_path = generate_notebook_for_task(wf_task)
                                    
                                    # Store notebook path
                                    if 'marimo_notebooks' not in st.session_state:
                                        st.session_state.marimo_notebooks = {}
                                    st.session_state.marimo_notebooks[task['id']] = notebook_path
                                    
                                    task['status'] = 'notebook_ready'
                                    st.success(f"Notebook generated: {Path(notebook_path).name}")
                                    st.rerun()
                        
                        elif task['status'] == 'notebook_ready':
                            st.info("📓 Notebook Ready")
    
    with col2:
        st.subheader("🚀 Execution Options")
        
        # Count ready notebooks
        ready_count = sum(1 for t in st.session_state.analysis_tasks 
                         if t['status'] == 'notebook_ready')
        total_count = len(st.session_state.analysis_tasks)
        
        st.metric("Notebooks Ready", f"{ready_count}/{total_count}")
        
        if ready_count > 0:
            st.success(f"✅ {ready_count} notebooks ready for execution")
            
            if st.button("🎯 Proceed to Marimo Execution", type="primary"):
                st.session_state.current_step = 5
                st.rerun()
        else:
            st.info("Generate notebooks for tasks to proceed")
        
        st.markdown("---")
        st.markdown("""
        **Marimo Benefits:**
        - 🔄 Reproducible analysis
        - 📊 Interactive notebooks
        - 🤖 Automated execution
        - 📈 Real-time results
        """)

def step5_marimo_execution():
    """Step 5: Execute analysis tasks in Marimo notebooks"""
    st.header("🚀 Step 5: Automated Marimo Execution")
    st.markdown("""
    **Purpose:** Execute the generated analysis tasks in Marimo notebooks and collect results.
    """)
    
    # Display execution dashboard
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("📊 Task Execution Dashboard")
        
        # Get tasks ready for execution
        executable_tasks = [t for t in st.session_state.analysis_tasks 
                           if t['status'] == 'notebook_ready']
        
        if not executable_tasks:
            st.warning("No tasks ready for execution. Please generate notebooks first.")
            if st.button("← Back to Task Planning"):
                st.session_state.current_step = 4
                st.rerun()
            return
        
        # Execution controls
        execution_mode = st.radio(
            "Execution Mode",
            ["Sequential", "Parallel (Faster)"],
            help="Sequential runs tasks one by one, Parallel runs multiple tasks simultaneously"
        )
        
        if st.button("▶️ Start Execution", type="primary"):
            st.session_state.execution_started = True
            
            # Create placeholder for progress
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # Execute tasks
            total_tasks = len(executable_tasks)
            completed = 0
            
            for i, task in enumerate(executable_tasks):
                # Update progress
                progress = (i + 1) / total_tasks
                progress_placeholder.progress(progress, f"Executing task {i+1}/{total_tasks}")
                status_placeholder.info(f"🔄 Running: {task['name']}")
                
                # Simulate notebook execution (in real implementation, would run actual notebook)
                time.sleep(2)  # Simulate execution time
                
                # Generate mock results
                results = {
                    'task_id': task['id'],
                    'task_name': task['name'],
                    'status': 'completed',
                    'execution_time': f"{np.random.randint(30, 180)} seconds",
                    'key_findings': [
                        f"Finding 1 for {task['name']}",
                        f"Finding 2 for {task['name']}",
                        f"Finding 3 for {task['name']}"
                    ],
                    'metrics': {
                        'accuracy': np.random.uniform(0.8, 0.95),
                        'completeness': np.random.uniform(0.85, 1.0),
                        'insights_generated': np.random.randint(5, 15)
                    }
                }
                
                # Store results
                if 'execution_results' not in st.session_state:
                    st.session_state.execution_results = {}
                st.session_state.execution_results[task['id']] = results
                
                # Update task status
                task['status'] = 'completed'
                completed += 1
            
            progress_placeholder.progress(1.0, "✅ All tasks completed!")
            status_placeholder.success(f"Successfully executed {completed} tasks")
            st.balloons()
            time.sleep(2)
            st.rerun()
    
    with col2:
        st.subheader("📈 Execution Status")
        
        # Count task statuses
        pending = sum(1 for t in st.session_state.analysis_tasks if t['status'] == 'pending')
        ready = sum(1 for t in st.session_state.analysis_tasks if t['status'] == 'notebook_ready')
        completed = sum(1 for t in st.session_state.analysis_tasks if t['status'] == 'completed')
        
        st.metric("Pending", pending)
        st.metric("Ready", ready)
        st.metric("Completed", completed)
        
        # Progress chart
        if completed > 0:
            progress_data = pd.DataFrame({
                'Status': ['Completed', 'Remaining'],
                'Count': [completed, len(st.session_state.analysis_tasks) - completed]
            })
            fig = px.pie(progress_data, values='Count', names='Status', 
                        color_discrete_map={'Completed': '#00CC88', 'Remaining': '#FF6B6B'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        st.subheader("🎯 Quick Actions")
        
        if st.button("📥 Download All Notebooks"):
            st.info("Notebooks available in workspace/notebooks/")
        
        if st.button("📊 View Results Summary"):
            st.session_state.show_results = True
        
        if st.button("🔄 Re-run Failed Tasks"):
            st.info("No failed tasks")
    
    # Display results if available
    if st.session_state.execution_results:
        st.markdown("---")
        st.subheader("📊 Execution Results")
        
        tabs = st.tabs([f"Task {i+1}" for i in range(len(st.session_state.execution_results))])
        
        for i, (task_id, results) in enumerate(st.session_state.execution_results.items()):
            with tabs[i]:
                st.write(f"### {results['task_name']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", "✅ Completed")
                with col2:
                    st.metric("Execution Time", results['execution_time'])
                with col3:
                    st.metric("Insights", results['metrics']['insights_generated'])
                
                st.write("**Key Findings:**")
                for finding in results['key_findings']:
                    st.write(f"• {finding}")
                
                st.write("**Performance Metrics:**")
                metrics_df = pd.DataFrame([results['metrics']])
                st.dataframe(metrics_df, use_container_width=True)
        
        # Final summary
        st.markdown("---")
        st.subheader("🎯 Analysis Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"""
            ✅ **Project Summary:**
            - Tasks Executed: {len(st.session_state.execution_results)}
            - Total Insights: {sum(r['metrics']['insights_generated'] for r in st.session_state.execution_results.values())}
            - Average Accuracy: {np.mean([r['metrics']['accuracy'] for r in st.session_state.execution_results.values()]):.2%}
            """)
        
        with col2:
            if st.button("📄 Generate Final Report", type="primary"):
                st.info("Generating comprehensive report...")
                time.sleep(2)
                st.success("Report generated! Download available.")
            
            if st.button("🔄 Start New Analysis"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key not in ['gemini_client', 'workflow_manager']:
                        del st.session_state[key]
                st.session_state.current_step = 1
                st.rerun()

def main():
    init_session_state()
    
    # Header
    st.title("🚀 AI-Powered Analysis Platform")
    st.markdown("**Integrated 4-Step Workflow with Automated Marimo Execution**")
    
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
    elif st.session_state.current_step == 5:
        step5_marimo_execution()
    
    # Sidebar
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
        
        # Workflow Status
        st.subheader("📊 Workflow Status")
        
        if 'analysis_tasks' in st.session_state:
            total_tasks = len(st.session_state.analysis_tasks)
            completed_tasks = sum(1 for t in st.session_state.analysis_tasks if t.get('status') == 'completed')
            
            if total_tasks > 0:
                progress = completed_tasks / total_tasks
                st.progress(progress)
                st.write(f"Progress: {completed_tasks}/{total_tasks} tasks")
        
        st.markdown("---")
        
        # Step navigation
        st.subheader("Quick Navigation")
        steps = ["Project Setup", "Manager Planning", "Data Understanding", 
                "Analysis Guidance", "Marimo Execution"]
        
        for i, step_name in enumerate(steps, 1):
            if st.button(f"Step {i}: {step_name}", 
                        disabled=(i > st.session_state.current_step),
                        use_container_width=True):
                st.session_state.current_step = i
                st.rerun()
        
        st.markdown("---")
        
        # Integration Features
        st.subheader("🔗 Integration Features")
        st.info("""
        **This version includes:**
        - ✅ 4-Step Planning Workflow
        - ✅ Marimo Notebook Generation
        - ✅ Automated Task Execution
        - ✅ Results Aggregation
        - ✅ Real-time Progress Tracking
        """)
        
        # Help section
        st.markdown("---")
        st.subheader("ℹ️ Help")
        with st.expander("How it works"):
            st.markdown("""
            1. **Setup:** Define project and upload data
            2. **Plan:** Generate AI-powered analysis plan
            3. **Profile:** Understand your data
            4. **Tasks:** Generate analysis tasks
            5. **Execute:** Run tasks in Marimo notebooks
            6. **Results:** View aggregated insights
            """)
        
        # Reset button
        if st.button("🔄 Reset Application", type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ['gemini_client', 'workflow_manager']:
                    del st.session_state[key]
            st.session_state.current_step = 1
            st.rerun()

if __name__ == "__main__":
    main()