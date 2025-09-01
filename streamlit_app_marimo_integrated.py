"""
AI Data Analysis Platform with Marimo Integration
Follows the conversation flow from AI-Data-Analysis-Team with marimo execution
"""

import streamlit as st
import pandas as pd
import os
import sys
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import tempfile

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from ai_personas import AITeamOrchestrator, ManagerPersona, AnalystPersona, AssociatePersona
from marimo_integration.notebook_builder import NotebookBuilder
from marimo_integration.notebook_runner import NotebookRunner
from reporting.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Team - Marimo Edition",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'current_step': 0,
        'project_initialized': False,
        'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
        'project_name': '',
        'problem_statement': '',
        'data_context': '',
        'dataframes': {},
        'data_profiles': {},
        'conversation_history': [],
        'manager_plan': None,
        'analyst_summary': None,
        'associate_guidance': None,
        'analysis_tasks': [],
        'task_results': [],
        'final_report': None,
        'marimo_notebooks': {},
        'gemini_model': 'gemini-2.0-flash-exp',
        'ai_team': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def add_to_conversation(persona: str, content: str):
    """Add message to conversation history"""
    st.session_state.conversation_history.append({
        'persona': persona,
        'content': content,
        'timestamp': datetime.now().isoformat()
    })

def process_uploaded_file(uploaded_file) -> tuple:
    """Process uploaded CSV/Excel file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, None, None
            
        # Create profile
        profile = {
            'columns': list(df.columns),
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict(),
            'missing': df.isnull().sum().to_dict(),
            'summary': df.describe().to_dict() if not df.empty else {}
        }
        
        return df, profile, None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None, None, None

def display_setup_step():
    """Step 1: Project Setup"""
    st.title("🚀 Start New Analysis Project")
    
    with st.form("project_setup_form"):
        st.subheader("1. Project Details")
        project_name = st.text_input(
            "Project Name", 
            value=st.session_state.get("project_name", ""),
            placeholder="My Analysis Project"
        )
        
        problem_statement = st.text_area(
            "Problem Statement / Goal",
            value=st.session_state.get("problem_statement", ""),
            placeholder="What insights are you looking for? What business problem are you solving?",
            height=100
        )
        
        data_context = st.text_area(
            "Data Context (Optional)",
            value=st.session_state.get("data_context", ""),
            placeholder="Background information about your data...",
            height=80
        )
        
        st.subheader("2. Upload Data")
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            key="file_uploader"
        )
        
        submit_button = st.form_submit_button("🚀 Start Analysis", type="primary")
        
        if submit_button:
            if not st.session_state.gemini_api_key:
                st.error("⚠️ Please enter your Gemini API Key in the sidebar first!")
            elif not project_name or not problem_statement or not uploaded_files:
                st.error("⚠️ Project Name, Problem Statement, and at least one Data File are required.")
            else:
                # Process files
                with st.spinner("Processing uploaded files..."):
                    st.session_state.dataframes = {}
                    st.session_state.data_profiles = {}
                    
                    for uploaded_file in uploaded_files:
                        df, profile, _ = process_uploaded_file(uploaded_file)
                        if df is not None:
                            st.session_state.dataframes[uploaded_file.name] = df
                            st.session_state.data_profiles[uploaded_file.name] = profile
                    
                    if st.session_state.dataframes:
                        # Initialize AI team
                        st.session_state.ai_team = AITeamOrchestrator(
                            st.session_state.gemini_api_key,
                            st.session_state.gemini_model
                        )
                        
                        # Save project details
                        st.session_state.project_name = project_name
                        st.session_state.problem_statement = problem_statement
                        st.session_state.data_context = data_context
                        st.session_state.project_initialized = True
                        st.session_state.current_step = 1
                        
                        # Add to conversation
                        file_summary = "\\n".join([
                            f"- {name}: {df.shape[0]} rows, {df.shape[1]} columns"
                            for name, df in st.session_state.dataframes.items()
                        ])
                        add_to_conversation(
                            "user",
                            f"Project: {project_name}\\nProblem: {problem_statement}\\nFiles:\\n{file_summary}"
                        )
                        
                        st.success("✅ Project initialized successfully!")
                        st.rerun()
                    else:
                        st.error("⚠️ No valid data files could be processed.")
    
    # Display summary if initialized
    if st.session_state.project_initialized:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Project:** {st.session_state.project_name}")
            st.info(f"**Files:** {len(st.session_state.dataframes)} loaded")
        with col2:
            if st.button("▶️ Continue to Planning", type="primary"):
                st.session_state.current_step = 1
                st.rerun()

def display_manager_planning_step():
    """Step 2: Manager Planning"""
    st.title("👔 AI Manager - Strategic Planning")
    
    if not st.session_state.ai_team:
        st.error("AI Team not initialized. Please complete setup first.")
        return
    
    # Generate plan if not exists
    if st.session_state.manager_plan is None:
        with st.spinner("🤔 AI Manager is creating the analysis plan..."):
            # Prepare file info
            file_info = "\\n".join([
                f"- {name}: {df.shape[0]} rows, {df.shape[1]} columns\\n  Columns: {', '.join(df.columns[:5])}..."
                for name, df in st.session_state.dataframes.items()
            ])
            
            # Get plan from Manager
            plan = st.session_state.ai_team.manager.create_analysis_plan(
                st.session_state.project_name,
                st.session_state.problem_statement,
                st.session_state.data_context,
                file_info
            )
            
            if plan and not plan.startswith("Error"):
                st.session_state.manager_plan = plan
                add_to_conversation("manager", f"Analysis Plan:\\n{plan}")
                st.rerun()
            else:
                st.error(f"Failed to generate plan: {plan}")
    
    # Display plan
    if st.session_state.manager_plan:
        st.markdown("### 📋 Strategic Analysis Plan")
        with st.container():
            st.markdown(st.session_state.manager_plan)
        
        st.divider()
        
        # Feedback section
        with st.expander("💬 Provide Feedback"):
            feedback = st.text_area("Your feedback on the plan:", key="manager_feedback")
            if st.button("Send Feedback"):
                if feedback:
                    with st.spinner("Revising plan..."):
                        # This would call manager to revise
                        st.success("Feedback received!")
        
        # Navigation
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("◀️ Back"):
                st.session_state.current_step = 0
                st.rerun()
        with col3:
            if st.button("▶️ Continue to Data Analysis", type="primary"):
                st.session_state.current_step = 2
                st.rerun()

def display_data_understanding_step():
    """Step 3: Data Understanding"""
    st.title("📊 AI Analyst - Data Understanding")
    
    if not st.session_state.ai_team or not st.session_state.manager_plan:
        st.error("Please complete previous steps first.")
        return
    
    # Generate summary if not exists
    if st.session_state.analyst_summary is None:
        with st.spinner("🔍 AI Analyst is examining your data..."):
            summary = st.session_state.ai_team.analyst.analyze_data_profile(
                st.session_state.data_profiles,
                st.session_state.manager_plan
            )
            
            if summary and not summary.startswith("Error"):
                st.session_state.analyst_summary = summary
                add_to_conversation("analyst", f"Data Analysis:\\n{summary}")
                st.rerun()
            else:
                st.error(f"Failed to analyze data: {summary}")
    
    # Display analysis
    if st.session_state.analyst_summary:
        st.markdown("### 📈 Data Assessment")
        with st.container():
            st.markdown(st.session_state.analyst_summary)
        
        # Show data preview
        st.divider()
        st.subheader("📋 Data Preview")
        
        tabs = st.tabs(list(st.session_state.dataframes.keys()))
        for i, (name, df) in enumerate(st.session_state.dataframes.items()):
            with tabs[i]:
                st.dataframe(df.head(10), use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Rows", df.shape[0])
                with col2:
                    st.metric("Columns", df.shape[1])
                with col3:
                    st.metric("Missing Values", df.isnull().sum().sum())
        
        # Navigation
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("◀️ Back"):
                st.session_state.current_step = 1
                st.rerun()
        with col3:
            if st.button("▶️ Generate Analysis Tasks", type="primary"):
                st.session_state.current_step = 3
                st.rerun()

def display_analysis_guidance_step():
    """Step 4: Analysis Guidance and Task Generation"""
    st.title("🎯 AI Associate - Analysis Tasks")
    
    if not st.session_state.ai_team or not st.session_state.analyst_summary:
        st.error("Please complete previous steps first.")
        return
    
    # Generate tasks if not exists
    if not st.session_state.analysis_tasks:
        with st.spinner("🧠 AI Associate is generating analysis tasks..."):
            tasks = st.session_state.ai_team.associate.generate_analysis_tasks(
                st.session_state.problem_statement,
                st.session_state.manager_plan,
                st.session_state.analyst_summary
            )
            
            if tasks:
                st.session_state.analysis_tasks = tasks
                st.session_state.associate_guidance = "\\n\\n".join(tasks)
                add_to_conversation("associate", f"Generated {len(tasks)} analysis tasks")
                st.rerun()
            else:
                st.error("Failed to generate tasks")
    
    # Display tasks
    if st.session_state.analysis_tasks:
        st.markdown("### 📝 Analysis Tasks")
        
        # Show tasks in expandable cards
        for i, task in enumerate(st.session_state.analysis_tasks, 1):
            with st.expander(f"Task {i}", expanded=i <= 3):
                st.markdown(task)
                
                # Task selection
                if st.button(f"Select Task {i}", key=f"select_task_{i}"):
                    st.session_state[f'selected_task_{i}'] = True
        
        st.divider()
        
        # Task execution options
        st.subheader("⚙️ Execution Options")
        
        col1, col2 = st.columns(2)
        with col1:
            execution_mode = st.radio(
                "Execution Mode",
                ["Automated with Marimo", "Manual Review"],
                help="Choose how to execute the analysis tasks"
            )
        
        with col2:
            selected_count = sum([
                st.session_state.get(f'selected_task_{i}', False) 
                for i in range(1, len(st.session_state.analysis_tasks) + 1)
            ])
            st.metric("Selected Tasks", selected_count)
        
        # Navigation
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("◀️ Back"):
                st.session_state.current_step = 2
                st.rerun()
        with col3:
            if st.button("▶️ Execute Analysis", type="primary"):
                if execution_mode == "Automated with Marimo":
                    st.session_state.current_step = 4
                else:
                    st.session_state.current_step = 5
                st.rerun()

def display_marimo_execution_step():
    """Step 5: Marimo Execution"""
    st.title("🚀 Automated Analysis with Marimo")
    
    if not st.session_state.analysis_tasks:
        st.error("No analysis tasks available.")
        return
    
    # Progress tracking
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        st.markdown("### 📊 Execution Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # Execute selected tasks
    selected_tasks = [
        (i, task) for i, task in enumerate(st.session_state.analysis_tasks, 1)
        if st.session_state.get(f'selected_task_{i}', False)
    ]
    
    if not selected_tasks:
        selected_tasks = [(i, task) for i, task in enumerate(st.session_state.analysis_tasks[:3], 1)]
    
    total_tasks = len(selected_tasks)
    task_results = []
    
    with status_container:
        st.markdown("### 🔄 Execution Status")
        
        for idx, (task_num, task) in enumerate(selected_tasks):
            with st.expander(f"Task {task_num}: Executing...", expanded=True):
                status_text.text(f"Processing task {idx + 1} of {total_tasks}...")
                progress_bar.progress((idx + 1) / total_tasks)
                
                # Get code from analyst
                with st.spinner(f"Generating code for task {task_num}..."):
                    task_result = st.session_state.ai_team.analyst.execute_analysis_task(
                        task,
                        json.dumps(st.session_state.data_profiles)
                    )
                    
                    if task_result and task_result.get('code'):
                        st.code(task_result['code'], language='python')
                        
                        # Create marimo notebook
                        notebook_id = f"task_{task_num}_{uuid.uuid4().hex[:8]}"
                        notebook_path = create_marimo_notebook(
                            task_result['code'],
                            task,
                            notebook_id
                        )
                        
                        if notebook_path:
                            st.success(f"✅ Marimo notebook created: {notebook_id}")
                            st.session_state.marimo_notebooks[notebook_id] = notebook_path
                            
                            # Execute notebook
                            with st.spinner("Executing in Marimo..."):
                                execution_result = execute_marimo_notebook(notebook_path)
                                if execution_result:
                                    task_result['execution'] = execution_result
                                    st.success("✅ Execution completed")
                                else:
                                    st.warning("⚠️ Execution completed with warnings")
                        
                        task_results.append(task_result)
                    else:
                        st.error(f"Failed to generate code for task {task_num}")
        
        st.session_state.task_results = task_results
        progress_bar.progress(1.0)
        status_text.text("All tasks completed!")
    
    # Show results summary
    if task_results:
        st.divider()
        st.markdown("### 📈 Results Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tasks Completed", len(task_results))
        with col2:
            st.metric("Notebooks Created", len(st.session_state.marimo_notebooks))
        with col3:
            st.metric("Success Rate", f"{len(task_results)/total_tasks*100:.0f}%")
        
        # Option to view notebooks
        if st.session_state.marimo_notebooks:
            st.markdown("### 📓 View Notebooks")
            for notebook_id, path in st.session_state.marimo_notebooks.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"📓 {notebook_id}")
                with col2:
                    if st.button("Open", key=f"open_{notebook_id}"):
                        # This would open the marimo notebook
                        st.info(f"Opening {notebook_id} in new tab...")
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀️ Back"):
            st.session_state.current_step = 3
            st.rerun()
    with col3:
        if st.button("▶️ Generate Report", type="primary"):
            st.session_state.current_step = 5
            st.rerun()

def display_final_report_step():
    """Step 6: Final Report"""
    st.title("📑 Final Analysis Report")
    
    if not st.session_state.ai_team:
        st.error("Analysis not completed.")
        return
    
    # Generate report if not exists
    if st.session_state.final_report is None:
        with st.spinner("📝 Generating comprehensive report..."):
            # Get review from associate
            if st.session_state.task_results:
                review = st.session_state.ai_team.associate.review_analysis(
                    st.session_state.task_results
                )
                add_to_conversation("associate", f"Review: {review[:200]}...")
            
            # Generate final report from manager
            report = st.session_state.ai_team.manager.create_final_report(
                st.session_state.task_results,
                st.session_state.problem_statement
            )
            
            if report and not report.startswith("Error"):
                st.session_state.final_report = report
                add_to_conversation("manager", "Generated final report")
                st.rerun()
            else:
                st.error("Failed to generate report")
    
    # Display report
    if st.session_state.final_report:
        # Report header
        st.markdown(f"### {st.session_state.project_name}")
        st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        st.divider()
        
        # Main report content
        with st.container():
            st.markdown(st.session_state.final_report)
        
        # Additional sections
        st.divider()
        
        # Analysis artifacts
        with st.expander("📊 Analysis Artifacts"):
            st.markdown("**Completed Tasks:**")
            for i, task in enumerate(st.session_state.analysis_tasks[:len(st.session_state.task_results)], 1):
                st.markdown(f"{i}. {task.split(':')[1] if ':' in task else task[:100]}")
            
            st.markdown("**Marimo Notebooks:**")
            for notebook_id in st.session_state.marimo_notebooks:
                st.markdown(f"- 📓 {notebook_id}")
        
        # Conversation history
        with st.expander("💬 Analysis Conversation"):
            for entry in st.session_state.conversation_history[-10:]:
                persona = entry['persona'].title()
                st.markdown(f"**{persona}:** {entry['content'][:200]}...")
        
        # Export options
        st.divider()
        st.markdown("### 💾 Export Options")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Export as PDF"):
                st.info("Generating PDF report...")
        with col2:
            if st.button("📊 Export Notebooks"):
                st.info("Preparing notebook archive...")
        with col3:
            if st.button("💾 Save Project"):
                save_project_state()
                st.success("Project saved!")
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("◀️ Back"):
            st.session_state.current_step = 4
            st.rerun()
    with col2:
        if st.button("🏠 New Analysis"):
            reset_session()
            st.rerun()

def create_marimo_notebook(code: str, task_description: str, notebook_id: str) -> str:
    """Create a marimo notebook for the given code"""
    try:
        # Prepare notebook content
        notebook_content = f'''
import marimo as mo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Task: {task_description}
# Generated: {datetime.now().isoformat()}

# Load data
{generate_data_loading_code()}

# Analysis Code
{code}

# Display results
mo.md("## Analysis Results")
'''
        
        # Save notebook
        notebook_path = f"marimo_notebooks/{notebook_id}.py"
        os.makedirs("marimo_notebooks", exist_ok=True)
        
        with open(notebook_path, 'w') as f:
            f.write(notebook_content)
        
        return notebook_path
    except Exception as e:
        st.error(f"Error creating notebook: {e}")
        return None

def generate_data_loading_code() -> str:
    """Generate code to load data in marimo notebook"""
    code_lines = []
    for name, df in st.session_state.dataframes.items():
        # Save dataframe to temp file
        temp_path = f"/tmp/{name}"
        df.to_csv(temp_path, index=False)
        code_lines.append(f"df_{name.replace('.', '_')} = pd.read_csv('{temp_path}')")
    
    return "\\n".join(code_lines)

def execute_marimo_notebook(notebook_path: str) -> Dict:
    """Execute a marimo notebook and return results"""
    try:
        # Run marimo notebook
        result = subprocess.run(
            ["marimo", "run", notebook_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def save_project_state():
    """Save current project state"""
    project_data = {
        "project_name": st.session_state.project_name,
        "problem_statement": st.session_state.problem_statement,
        "timestamp": datetime.now().isoformat(),
        "manager_plan": st.session_state.manager_plan,
        "analyst_summary": st.session_state.analyst_summary,
        "tasks": st.session_state.analysis_tasks,
        "results": st.session_state.task_results,
        "final_report": st.session_state.final_report
    }
    
    # Save to file
    filename = f"projects/{st.session_state.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("projects", exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(project_data, f, indent=2, default=str)
    
    return filename

def reset_session():
    """Reset session state"""
    for key in list(st.session_state.keys()):
        if key not in ['gemini_api_key', 'gemini_model']:
            del st.session_state[key]
    init_session_state()

# Main Application
def main():
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 AI Analysis Team")
        st.markdown("---")
        
        # API Key
        api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Enter your Google Gemini API key"
        )
        if api_key != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_key
            if api_key and st.session_state.ai_team:
                # Reconfigure AI team with new key
                st.session_state.ai_team = AITeamOrchestrator(api_key, st.session_state.gemini_model)
        
        # Model selection
        model = st.selectbox(
            "Model",
            ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            index=0
        )
        st.session_state.gemini_model = model
        
        st.markdown("---")
        
        # Navigation
        if st.session_state.project_initialized:
            st.markdown("### 📍 Navigation")
            steps = [
                "1️⃣ Project Setup",
                "2️⃣ Manager Planning", 
                "3️⃣ Data Understanding",
                "4️⃣ Task Generation",
                "5️⃣ Marimo Execution",
                "6️⃣ Final Report"
            ]
            
            for i, step in enumerate(steps):
                if i == st.session_state.current_step:
                    st.markdown(f"**▶️ {step}**")
                else:
                    if st.button(step, key=f"nav_{i}"):
                        st.session_state.current_step = i
                        st.rerun()
        
        st.markdown("---")
        
        # AI Team Info
        st.markdown("### 👥 AI Team")
        st.markdown("**👔 Manager:** Strategic Planning")
        st.markdown("**📊 Analyst:** Data Analysis")
        st.markdown("**🎯 Associate:** Task Generation")
        
        st.markdown("---")
        
        # Actions
        if st.session_state.project_initialized:
            if st.button("🔄 Reset Project"):
                reset_session()
                st.rerun()
            
            if st.button("💾 Save State"):
                save_project_state()
                st.success("Saved!")
    
    # Main content area
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar to begin.")
        st.stop()
    
    # Display current step
    steps = [
        display_setup_step,
        display_manager_planning_step,
        display_data_understanding_step,
        display_analysis_guidance_step,
        display_marimo_execution_step,
        display_final_report_step
    ]
    
    if st.session_state.current_step < len(steps):
        steps[st.session_state.current_step]()
    else:
        st.error("Invalid step")

if __name__ == "__main__":
    main()