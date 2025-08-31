"""
AI Data Analysis Platform - Unified Version (No Authentication)
Direct access to all features with role switching capability
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import sys
import time
from typing import Dict, List, Optional
import uuid
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from workflow.workflow_manager import WorkflowManager
from agents import DataAnalysisAgent, VisualizationAgent, MLAgent
from execution.task_executor import TaskExecutor
from reporting.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'overview'  # Start with overview
        st.session_state.workflow_manager = WorkflowManager()
        st.session_state.task_executor = TaskExecutor()
        st.session_state.report_generator = ReportGenerator()
        st.session_state.active_plans = {}
        st.session_state.task_results = {}
        st.session_state.uploaded_data = {}
        st.session_state.plan_reports = {}
        st.session_state.current_user = 'Manager'  # Default user type
        st.session_state.assigned_tasks = []  # Tasks for associates

init_session_state()

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6 0%, #e0e2e6 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .view-selector {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .task-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .workflow-step {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="main-header">🚀 AI Data Analysis Platform</div>', unsafe_allow_html=True)

# Sidebar for navigation and view selection
with st.sidebar:
    st.markdown("## 🎯 Navigation")
    
    # View selector
    view_options = {
        'overview': '📊 Overview',
        'create_plan': '➕ Create Analysis Plan',
        'manage_plans': '📋 Manage Plans',
        'execute_tasks': '⚡ Execute Tasks',
        'view_results': '📈 View Results',
        'generate_reports': '📄 Generate Reports',
        'team_view': '👥 Team & Resources'
    }
    
    selected_view = st.selectbox(
        "Select View",
        options=list(view_options.keys()),
        format_func=lambda x: view_options[x],
        key='view_selector'
    )
    
    st.session_state.current_view = selected_view
    
    # Quick role switcher
    st.markdown("---")
    st.markdown("### 👤 Current Role")
    role = st.radio(
        "Switch Role",
        options=["Manager", "Analyst", "Associate"],
        key='role_selector'
    )
    st.session_state.current_user = role
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    st.metric("Active Plans", len(st.session_state.active_plans))
    st.metric("Completed Tasks", len(st.session_state.task_results))
    st.metric("Pending Tasks", len(st.session_state.assigned_tasks))

# Main content area based on selected view
if st.session_state.current_view == 'overview':
    st.markdown("## 📊 Platform Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Plans",
            len(st.session_state.active_plans),
            delta="+2 this week"
        )
    
    with col2:
        completed = len([t for t in st.session_state.task_results.values() 
                        if t.get('status') == 'success'])
        st.metric("Completed Analyses", completed, delta="+5 today")
    
    with col3:
        pending = len(st.session_state.assigned_tasks)
        st.metric("Pending Tasks", pending, delta="-3 today")
    
    with col4:
        reports = len(st.session_state.plan_reports)
        st.metric("Reports Generated", reports, delta="+1 today")
    
    # Workflow visualization
    st.markdown("### 🔄 Analysis Workflow")
    
    workflow_steps = [
        ("1️⃣ Create Plan", "Define objectives and upload data"),
        ("2️⃣ Generate Tasks", "AI auto-generates analysis tasks"),
        ("3️⃣ Execute Analysis", "Run ML-powered analysis"),
        ("4️⃣ Review Results", "Examine insights and findings"),
        ("5️⃣ Generate Report", "Create executive summary")
    ]
    
    cols = st.columns(5)
    for i, (step, desc) in enumerate(workflow_steps):
        with cols[i]:
            st.markdown(f"""
            <div class="workflow-step">
                <strong>{step}</strong><br>
                <small>{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("### 📅 Recent Activity")
    
    activities = [
        {"time": "Just now", "action": "System ready", "icon": "✅"},
        {"time": "2 min ago", "action": "Report generated for Q4 Analysis", "icon": "📄"},
        {"time": "5 min ago", "action": "Task completed: Statistical Analysis", "icon": "✔️"},
        {"time": "10 min ago", "action": "New plan created: Sales Forecast", "icon": "📋"},
    ]
    
    for activity in activities:
        st.markdown(f"{activity['icon']} **{activity['time']}**: {activity['action']}")

elif st.session_state.current_view == 'create_plan':
    st.markdown("## ➕ Create Analysis Plan")
    st.markdown("Define your analysis objectives and the AI will generate appropriate tasks")
    
    with st.form("create_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            plan_name = st.text_input(
                "Plan Name",
                placeholder="Q4 Sales Analysis",
                help="Give your analysis plan a descriptive name"
            )
            
            objectives = st.text_area(
                "Business Objectives",
                placeholder="- Analyze Q4 sales performance\n- Identify top products\n- Predict Q1 trends",
                height=150,
                help="List your analysis objectives. The AI will generate tasks based on these."
            )
            
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        with col2:
            deadline = st.date_input("Target Completion", min_value=datetime.now().date())
            
            data_source = st.selectbox(
                "Data Source",
                ["Upload New", "Use Sample Data", "Connect Database"]
            )
            
            if data_source == "Upload New":
                uploaded_file = st.file_uploader(
                    "Upload Data File",
                    type=['csv', 'xlsx'],
                    help="Upload your data file for analysis"
                )
            else:
                uploaded_file = None
            
            auto_execute = st.checkbox(
                "Auto-execute tasks after creation",
                value=True,
                help="Automatically start analysis after plan creation"
            )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            parallel_execution = st.checkbox("Enable parallel task execution", value=True)
            quality_threshold = st.slider("Quality threshold", 0.0, 1.0, 0.7)
            max_iterations = st.number_input("Max iterations", min_value=1, max_value=10, value=3)
        
        submitted = st.form_submit_button("🚀 Create Plan", use_container_width=True)
        
        if submitted:
            if plan_name and objectives:
                # Create unique plan ID
                plan_id = str(uuid.uuid4())
                
                # Process uploaded data
                data = None
                data_id = None
                if uploaded_file:
                    if uploaded_file.name.endswith('.csv'):
                        data = pd.read_csv(uploaded_file)
                    else:
                        data = pd.read_excel(uploaded_file)
                    
                    data_id = str(uuid.uuid4())
                    st.session_state.uploaded_data[data_id] = data
                    
                    st.success(f"✅ Data uploaded: {data.shape[0]} rows, {data.shape[1]} columns")
                elif data_source == "Use Sample Data":
                    # Create sample data
                    data = pd.DataFrame({
                        'Date': pd.date_range('2024-01-01', periods=100),
                        'Sales': np.random.randint(1000, 5000, 100),
                        'Product': np.random.choice(['A', 'B', 'C'], 100),
                        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100)
                    })
                    data_id = str(uuid.uuid4())
                    st.session_state.uploaded_data[data_id] = data
                    st.info("📊 Using sample sales data for demonstration")
                
                # Parse objectives
                obj_list = [obj.strip() for obj in objectives.split('\n') if obj.strip()]
                
                # Generate tasks using WorkflowManager
                with st.spinner("🤖 AI is generating analysis tasks..."):
                    tasks = st.session_state.workflow_manager.generate_analysis_tasks(
                        objectives=obj_list,
                        data_info={
                            'source': data_source,
                            'shape': data.shape if data is not None else None,
                            'columns': list(data.columns) if data is not None else None
                        } if data is not None else None
                    )
                
                # Create plan
                plan = {
                    'id': plan_id,
                    'name': plan_name,
                    'objectives': obj_list,
                    'priority': priority,
                    'deadline': deadline.isoformat(),
                    'data_source': data_source,
                    'data_id': data_id,
                    'tasks': tasks,
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'auto_execute': auto_execute
                }
                
                st.session_state.active_plans[plan_id] = plan
                
                # Add tasks to assigned tasks
                st.session_state.assigned_tasks.extend(tasks)
                
                st.success(f"✅ Plan '{plan_name}' created successfully!")
                st.info(f"🎯 Generated {len(tasks)} analysis tasks")
                
                # Show generated tasks
                st.markdown("### 📋 Generated Tasks:")
                for i, task in enumerate(tasks, 1):
                    task_type = task.get('type', 'analysis')
                    icon = {
                        'data_profiling': '🔍',
                        'statistical_analysis': '📊',
                        'predictive_modeling': '🔮',
                        'visualization': '📈',
                        'reporting': '📄'
                    }.get(task_type, '📌')
                    
                    st.markdown(f"{i}. {icon} **{task['name']}**")
                    st.caption(f"   {task.get('description', '')}")
                
                # Auto-execute if enabled
                if auto_execute and data is not None:
                    st.markdown("---")
                    st.info("🚀 Auto-executing tasks...")
                    execute_tasks_automatically(plan_id, tasks, data)
            else:
                st.error("Please provide plan name and objectives")

elif st.session_state.current_view == 'manage_plans':
    st.markdown("## 📋 Manage Analysis Plans")
    
    if not st.session_state.active_plans:
        st.info("No active plans. Create a new plan to get started!")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Active", "Completed"])
        with col2:
            priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
        with col3:
            sort_by = st.selectbox("Sort By", ["Created Date", "Priority", "Progress"])
        
        # Display plans
        for plan_id, plan in st.session_state.active_plans.items():
            with st.expander(f"📊 {plan['name']} - {plan['status'].title()}", expanded=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Created:** {plan['created_at'][:10]}")
                    st.markdown(f"**Priority:** {plan['priority']}")
                    st.markdown(f"**Objectives:**")
                    for obj in plan['objectives']:
                        st.markdown(f"  • {obj}")
                
                with col2:
                    # Progress calculation
                    total_tasks = len(plan['tasks'])
                    completed = len([t for t in plan['tasks'] 
                                   if any(r.get('task_id') == t['id'] 
                                         for r in st.session_state.task_results.values())])
                    progress = (completed / total_tasks * 100) if total_tasks > 0 else 0
                    
                    st.metric("Progress", f"{progress:.0f}%")
                    st.progress(progress / 100)
                
                with col3:
                    # Action buttons
                    if st.button(f"📊 View Details", key=f"details_{plan_id}"):
                        st.session_state.current_view = 'view_results'
                        st.rerun()
                    
                    if st.button(f"⚡ Execute Tasks", key=f"exec_{plan_id}"):
                        st.session_state.current_view = 'execute_tasks'
                        st.rerun()
                    
                    if st.button(f"📄 Generate Report", key=f"report_{plan_id}"):
                        generate_plan_report(plan_id)

elif st.session_state.current_view == 'execute_tasks':
    st.markdown("## ⚡ Execute Analysis Tasks")
    
    # Get all pending tasks
    pending_tasks = []
    for plan in st.session_state.active_plans.values():
        for task in plan['tasks']:
            if task['id'] not in [r.get('task_id') for r in st.session_state.task_results.values()]:
                pending_tasks.append({
                    'plan_name': plan['name'],
                    'plan_id': plan['id'],
                    **task
                })
    
    if not pending_tasks:
        st.success("✅ All tasks have been completed!")
    else:
        st.info(f"📋 {len(pending_tasks)} tasks pending execution")
        
        # Batch execution option
        if st.button("🚀 Execute All Pending Tasks", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, task in enumerate(pending_tasks):
                status_text.text(f"Executing: {task['name']}")
                progress_bar.progress((i + 1) / len(pending_tasks))
                
                # Get associated data
                plan = st.session_state.active_plans.get(task['plan_id'])
                data_id = plan.get('data_id') if plan else None
                data = st.session_state.uploaded_data.get(data_id) if data_id else None
                
                if data is not None:
                    # Execute task
                    result = st.session_state.task_executor.execute_task(task, data)
                    st.session_state.task_results[task['id']] = result
                    
                    if result.get('status') == 'success':
                        st.success(f"✅ {task['name']} completed")
                    else:
                        st.error(f"❌ {task['name']} failed")
                
                time.sleep(0.5)  # Brief pause for UI
            
            status_text.text("All tasks completed!")
            st.balloons()
        
        # Individual task execution
        st.markdown("### 📋 Individual Tasks")
        
        for task in pending_tasks[:5]:  # Show first 5 tasks
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{task['name']}**")
                    st.caption(f"Plan: {task['plan_name']} | Type: {task.get('type', 'analysis')}")
                
                with col2:
                    st.markdown(f"Priority: {task.get('priority', 'medium').title()}")
                
                with col3:
                    if st.button("▶️ Execute", key=f"exec_task_{task['id']}"):
                        with st.spinner(f"Executing {task['name']}..."):
                            # Get data and execute
                            plan = st.session_state.active_plans.get(task['plan_id'])
                            data_id = plan.get('data_id') if plan else None
                            data = st.session_state.uploaded_data.get(data_id)
                            
                            if data is not None:
                                result = st.session_state.task_executor.execute_task(task, data)
                                st.session_state.task_results[task['id']] = result
                                
                                if result.get('status') == 'success':
                                    st.success("Task completed successfully!")
                                    st.rerun()

elif st.session_state.current_view == 'view_results':
    st.markdown("## 📈 Analysis Results")
    
    if not st.session_state.task_results:
        st.info("No results yet. Execute some tasks first!")
    else:
        # Group results by plan
        results_by_plan = {}
        for plan_id, plan in st.session_state.active_plans.items():
            plan_results = []
            for task in plan['tasks']:
                if task['id'] in st.session_state.task_results:
                    plan_results.append(st.session_state.task_results[task['id']])
            if plan_results:
                results_by_plan[plan['name']] = plan_results
        
        # Display results for each plan
        for plan_name, results in results_by_plan.items():
            st.markdown(f"### 📊 {plan_name}")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_confidence = np.mean([r.get('confidence', 0) for r in results])
                st.metric("Avg Confidence", f"{avg_confidence*100:.0f}%")
            with col2:
                avg_quality = np.mean([r.get('quality_score', 0) for r in results])
                st.metric("Avg Quality", f"{avg_quality*100:.0f}%")
            with col3:
                success_rate = len([r for r in results if r.get('status') == 'success']) / len(results)
                st.metric("Success Rate", f"{success_rate*100:.0f}%")
            
            # Individual task results
            for result in results:
                with st.expander(f"📌 {result.get('task_name', 'Task')} - {result.get('status', 'unknown').title()}"):
                    if result.get('status') == 'success' and 'results' in result:
                        task_data = result['results']
                        
                        # Display insights
                        if 'insights' in task_data and task_data['insights']:
                            st.markdown("**💡 Key Insights:**")
                            for insight in task_data['insights']:
                                st.markdown(f"• {insight}")
                        
                        # Display metrics
                        if 'metrics' in task_data:
                            st.markdown("**📊 Metrics:**")
                            st.json(task_data['metrics'])
                        
                        # Display statistics
                        if 'statistics' in task_data:
                            st.markdown("**📈 Statistics:**")
                            st.json(task_data['statistics'])

elif st.session_state.current_view == 'generate_reports':
    st.markdown("## 📄 Generate Reports")
    
    # Select plan for report
    plan_options = {plan_id: plan['name'] for plan_id, plan in st.session_state.active_plans.items()}
    
    if plan_options:
        selected_plan_id = st.selectbox(
            "Select Plan for Report",
            options=list(plan_options.keys()),
            format_func=lambda x: plan_options[x]
        )
        
        if st.button("📄 Generate Executive Report", use_container_width=True):
            generate_plan_report(selected_plan_id)
        
        # Display existing reports
        if st.session_state.plan_reports:
            st.markdown("### 📚 Generated Reports")
            
            for plan_id, report in st.session_state.plan_reports.items():
                if plan_id in plan_options:
                    with st.expander(f"📄 {plan_options[plan_id]} Report"):
                        # Display report sections
                        for section_key, section in report.get('sections', {}).items():
                            st.markdown(f"### {section['title']}")
                            st.markdown(section['content'])
                        
                        # Download options
                        col1, col2 = st.columns(2)
                        with col1:
                            html_report = st.session_state.report_generator.export_report_to_html(report)
                            st.download_button(
                                label="📥 Download HTML",
                                data=html_report,
                                file_name=f"report_{plan_options[plan_id].replace(' ', '_')}.html",
                                mime="text/html",
                                key=f"html_{plan_id}"
                            )
                        with col2:
                            st.download_button(
                                label="📥 Download JSON",
                                data=json.dumps(report, indent=2),
                                file_name=f"report_{plan_options[plan_id].replace(' ', '_')}.json",
                                mime="application/json",
                                key=f"json_{plan_id}"
                            )
    else:
        st.info("No plans available. Create a plan first!")

elif st.session_state.current_view == 'team_view':
    st.markdown("## 👥 Team & Resources")
    
    # Team simulation
    team_members = [
        {"name": "Sarah Johnson", "role": "Manager", "status": "Active", "tasks": 0},
        {"name": "Mike Chen", "role": "Senior Analyst", "status": "Active", "tasks": 3},
        {"name": "Emily Davis", "role": "Analyst", "status": "Active", "tasks": 2},
        {"name": "David Kim", "role": "Associate", "status": "Away", "tasks": 1},
    ]
    
    # Display team
    st.markdown("### Team Members")
    
    df_team = pd.DataFrame(team_members)
    st.dataframe(df_team, use_container_width=True)
    
    # Workload distribution
    st.markdown("### 📊 Workload Distribution")
    
    fig = px.bar(df_team, x='name', y='tasks', color='role',
                 title="Current Task Assignment")
    st.plotly_chart(fig, use_container_width=True)
    
    # Resource utilization
    st.markdown("### 💻 Resource Utilization")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU Usage", "45%", delta="-5%")
    with col2:
        st.metric("Memory Usage", "2.3 GB", delta="+0.2 GB")
    with col3:
        st.metric("Active Processes", "8", delta="0")

# Helper Functions
def execute_tasks_automatically(plan_id, tasks, data):
    """Execute tasks automatically after plan creation"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, task in enumerate(tasks):
        status_text.text(f"Executing: {task['name']}")
        progress_bar.progress((i + 1) / len(tasks))
        
        # Execute task
        result = st.session_state.task_executor.execute_task(task, data)
        st.session_state.task_results[task['id']] = result
        
        time.sleep(0.5)  # Brief pause for UI
    
    status_text.text("✅ All tasks completed!")
    st.success(f"Successfully executed {len(tasks)} tasks")

def generate_plan_report(plan_id):
    """Generate report for a plan"""
    plan = st.session_state.active_plans.get(plan_id)
    if not plan:
        st.error("Plan not found")
        return
    
    # Get task results
    plan_task_ids = [task['id'] for task in plan.get('tasks', [])]
    plan_task_results = [st.session_state.task_results.get(tid) 
                         for tid in plan_task_ids 
                         if tid in st.session_state.task_results]
    
    if not plan_task_results:
        st.warning("No completed tasks found. Execute tasks first.")
        return
    
    with st.spinner("Generating report..."):
        # Aggregate results
        aggregated = st.session_state.report_generator.aggregate_plan_results(plan, plan_task_results)
        
        # Generate report
        report = st.session_state.report_generator.generate_executive_report(aggregated)
        
        # Store report
        st.session_state.plan_reports[plan_id] = report
        
        st.success("✅ Report generated successfully!")
        st.markdown(f"### {report['title']}")
        
        # Display key sections
        for section_key, section in list(report['sections'].items())[:3]:
            st.markdown(f"**{section['title']}**")
            st.markdown(section['content'][:500] + "...")  # Show preview
        
        st.info("View the full report in the 'Generate Reports' section")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        AI Data Analysis Platform | No Login Required | Direct Access to All Features
    </div>
    """,
    unsafe_allow_html=True
)