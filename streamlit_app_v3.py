"""
AI Data Analysis Platform - Production Version
With Authentication, Role-Based Access, and Integrated Workflow
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

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from auth.authentication import auth_manager
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
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.session_token = None
        st.session_state.user = None
        st.session_state.workflow_manager = WorkflowManager()
        st.session_state.task_executor = TaskExecutor()
        st.session_state.report_generator = ReportGenerator()
        st.session_state.active_plans = {}
        st.session_state.task_results = {}
        st.session_state.uploaded_data = {}
        st.session_state.plan_reports = {}

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
    .role-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.9rem;
        display: inline-block;
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
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Authentication Functions
def login_page():
    """Display login page"""
    st.markdown('<div class="main-header">🔐 AI Data Analysis Platform</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Sign In")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if email and password:
                    session_token = auth_manager.authenticate(email, password)
                    if session_token:
                        st.session_state.authenticated = True
                        st.session_state.session_token = session_token
                        st.session_state.user = auth_manager.validate_session(session_token)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.warning("Please enter both email and password")
        
        # Demo credentials
        with st.expander("Demo Credentials"):
            st.markdown("""
            **Manager Account:**
            - Email: `manager@company.com`
            - Password: `manager123`
            
            **Analyst Account:**
            - Email: `analyst@company.com`
            - Password: `analyst123`
            
            **Associate Account:**
            - Email: `associate@company.com`
            - Password: `associate123`
            """)

def logout():
    """Logout user"""
    if st.session_state.session_token:
        auth_manager.logout(st.session_state.session_token)
    st.session_state.authenticated = False
    st.session_state.session_token = None
    st.session_state.user = None
    st.rerun()

# Manager Dashboard
def manager_dashboard():
    """Display manager dashboard"""
    user = st.session_state.user
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"## 👔 Manager Dashboard")
        st.markdown(f"Welcome back, **{user.name}**!")
    with col2:
        st.markdown(f'<span class="role-badge">{user.role.upper()}</span>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout"):
            logout()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "➕ Create Plan", "📋 Active Plans", 
        "👥 Team", "📈 Reports"
    ])
    
    with tab1:
        manager_overview()
    
    with tab2:
        create_plan_interface()
    
    with tab3:
        manage_active_plans()
    
    with tab4:
        team_management()
    
    with tab5:
        reports_dashboard()

def manager_overview():
    """Manager overview metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    active_plans = len(st.session_state.active_plans)
    team_members = len(auth_manager.get_team_members(st.session_state.user.team))
    completed_tasks = sum(len(plan.get('completed_tasks', [])) 
                          for plan in st.session_state.active_plans.values())
    pending_tasks = sum(len(plan.get('pending_tasks', [])) 
                       for plan in st.session_state.active_plans.values())
    
    with col1:
        st.metric("Active Plans", active_plans, delta="+2 this week")
    
    with col2:
        st.metric("Team Members", team_members, delta="Full capacity")
    
    with col3:
        st.metric("Completed Tasks", completed_tasks, delta="+5 today")
    
    with col4:
        st.metric("Pending Tasks", pending_tasks, delta="-3 today")
    
    # Recent activity
    st.markdown("### 📅 Recent Activity")
    
    activities = [
        {"time": "2 hours ago", "action": "Plan approved", "details": "Q4 Sales Analysis"},
        {"time": "3 hours ago", "action": "Task completed", "details": "Customer segmentation by Mike Chen"},
        {"time": "5 hours ago", "action": "New plan created", "details": "Marketing Campaign Analysis"},
        {"time": "Yesterday", "action": "Report generated", "details": "Monthly Performance Report"}
    ]
    
    for activity in activities[:5]:
        st.markdown(f"""
        <div class="task-card">
            <strong>{activity['time']}</strong>: {activity['action']}<br>
            <small>{activity['details']}</small>
        </div>
        """, unsafe_allow_html=True)

def create_plan_interface():
    """Interface for creating new analysis plans"""
    st.markdown("### 🎯 Create New Analysis Plan")
    
    with st.form("create_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            plan_name = st.text_input("Plan Name", placeholder="Q4 Sales Analysis")
            objectives = st.text_area("Business Objectives", 
                                     placeholder="- Identify revenue trends\n- Predict Q1 sales\n- Find top customers")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        with col2:
            deadline = st.date_input("Deadline", min_value=datetime.now().date())
            team_members = st.multiselect("Assign To", 
                                         options=[u.name for u in auth_manager.get_team_members(st.session_state.user.team)])
            data_source = st.selectbox("Data Source", ["Upload New", "Sales Database", "CRM System", "Marketing Data"])
        
        # File upload
        if data_source == "Upload New":
            uploaded_file = st.file_uploader("Upload Data File", type=['csv', 'xlsx'])
        else:
            uploaded_file = None
        
        # Advanced options
        with st.expander("Advanced Options"):
            auto_assign = st.checkbox("Auto-assign tasks based on skills", value=True)
            parallel_execution = st.checkbox("Enable parallel task execution", value=True)
            quality_checks = st.checkbox("Enable automated quality checks", value=True)
        
        submitted = st.form_submit_button("Create Plan", use_container_width=True)
        
        if submitted:
            if plan_name and objectives:
                # Process uploaded data
                data = None
                if uploaded_file:
                    if uploaded_file.name.endswith('.csv'):
                        data = pd.read_csv(uploaded_file)
                    else:
                        data = pd.read_excel(uploaded_file)
                    
                    # Store data
                    data_id = str(uuid.uuid4())
                    st.session_state.uploaded_data[data_id] = data
                
                # Create plan using WorkflowManager
                plan_id = str(uuid.uuid4())
                
                # Parse objectives
                obj_list = [obj.strip() for obj in objectives.split('\n') if obj.strip()]
                
                # Generate tasks
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
                    'assigned_to': team_members,
                    'data_source': data_source,
                    'data_id': data_id if uploaded_file else None,
                    'tasks': tasks,
                    'status': 'pending_approval',
                    'created_at': datetime.now().isoformat(),
                    'created_by': st.session_state.user.name,
                    'auto_assign': auto_assign,
                    'parallel_execution': parallel_execution,
                    'quality_checks': quality_checks
                }
                
                st.session_state.active_plans[plan_id] = plan
                
                st.success(f"✅ Plan '{plan_name}' created successfully!")
                st.info(f"Generated {len(tasks)} tasks for analysis")
                
                # Show task preview
                st.markdown("#### 📋 Generated Tasks:")
                for i, task in enumerate(tasks[:5], 1):
                    st.markdown(f"{i}. **{task['name']}** - {task.get('description', 'Analysis task')}")
                
                if len(tasks) > 5:
                    st.markdown(f"... and {len(tasks) - 5} more tasks")
            else:
                st.error("Please provide plan name and objectives")

def manage_active_plans():
    """Manage active analysis plans"""
    st.markdown("### 📋 Active Plans")
    
    if not st.session_state.active_plans:
        st.info("No active plans. Create a new plan to get started!")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending Approval", "In Progress", "Completed"])
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Created Date", "Deadline", "Priority", "Progress"])
    
    # Display plans
    for plan_id, plan in st.session_state.active_plans.items():
        with st.expander(f"📊 {plan['name']} - {plan['status'].replace('_', ' ').title()}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Created:** {plan['created_at'][:10]}")
                st.markdown(f"**Deadline:** {plan['deadline']}")
                st.markdown(f"**Priority:** {plan['priority']}")
                st.markdown(f"**Assigned To:** {', '.join(plan['assigned_to']) if plan['assigned_to'] else 'Unassigned'}")
            
            with col2:
                # Progress
                completed = len([t for t in plan['tasks'] if t.get('status') == 'completed'])
                total = len(plan['tasks'])
                progress = (completed / total * 100) if total > 0 else 0
                
                st.metric("Progress", f"{progress:.0f}%")
                st.progress(progress / 100)
            
            with col3:
                # Actions
                if plan['status'] == 'pending_approval':
                    if st.button(f"✅ Approve", key=f"approve_{plan_id}"):
                        plan['status'] = 'in_progress'
                        st.success("Plan approved and tasks assigned!")
                        
                        # Auto-assign tasks if enabled
                        if plan.get('auto_assign'):
                            for task in plan['tasks']:
                                # Find best analyst
                                analyst = auth_manager.find_best_analyst_for_task(
                                    task.get('required_skills', [])
                                )
                                if analyst:
                                    task['assigned_to'] = analyst.email
                                    auth_manager.assign_task_to_user(analyst.email, task['id'])
                        st.rerun()
                
                if st.button(f"📊 View Details", key=f"details_{plan_id}"):
                    view_plan_details(plan_id)
                
                if st.button(f"📄 Generate Report", key=f"report_{plan_id}"):
                    generate_plan_report(plan_id)

def team_management():
    """Team management interface"""
    st.markdown("### 👥 Team Management")
    
    team_members = auth_manager.get_team_members(st.session_state.user.team)
    
    # Team metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Team Size", len(team_members))
    with col2:
        analysts = len([m for m in team_members if m.role == 'analyst'])
        st.metric("Analysts", analysts)
    with col3:
        associates = len([m for m in team_members if m.role == 'associate'])
        st.metric("Associates", associates)
    
    # Team members table
    st.markdown("#### Team Members")
    
    members_data = []
    for member in team_members:
        workload = auth_manager.get_user_workload(member.email)
        members_data.append({
            'Name': member.name,
            'Role': member.role.title(),
            'Email': member.email,
            'Active Tasks': workload['active_tasks'],
            'Completed Tasks': workload['completed_tasks'],
            'Skills': ', '.join(member.skills[:3]) + ('...' if len(member.skills) > 3 else '')
        })
    
    df = pd.DataFrame(members_data)
    st.dataframe(df, use_container_width=True)
    
    # Workload visualization
    st.markdown("#### Workload Distribution")
    
    fig = px.bar(df, x='Name', y=['Active Tasks', 'Completed Tasks'],
                 title="Task Distribution by Team Member",
                 barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

def reports_dashboard():
    """Reports and analytics dashboard"""
    st.markdown("### 📈 Reports & Analytics")
    
    # Report types
    report_type = st.selectbox("Report Type", 
                               ["Executive Summary", "Detailed Analysis", 
                                "Team Performance", "Monthly Report"])
    
    # Date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", 
                                   value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    if st.button("Generate Report", use_container_width=True):
        with st.spinner("Generating report..."):
            time.sleep(2)  # Simulate processing
            
            st.success("Report generated successfully!")
            
            # Sample report content
            st.markdown("#### 📊 Executive Summary")
            st.markdown("""
            **Key Findings:**
            - Revenue increased by 15% compared to last quarter
            - Customer satisfaction score improved to 4.5/5
            - Identified 3 high-value customer segments
            - Predicted 20% growth for Q1 2025
            
            **Recommendations:**
            1. Focus marketing efforts on high-value segments
            2. Increase inventory for top-selling products
            3. Implement customer retention program
            """)
            
            # Sample visualization
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                y=[100, 110, 125, 120, 145, 165],
                mode='lines+markers',
                name='Revenue Trend'
            ))
            fig.update_layout(title="Revenue Growth Trend")
            st.plotly_chart(fig, use_container_width=True)

# Associate Dashboard
def associate_dashboard():
    """Display associate/analyst dashboard"""
    user = st.session_state.user
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"## 🔬 Analyst Dashboard")
        st.markdown(f"Welcome back, **{user.name}**!")
    with col2:
        st.markdown(f'<span class="role-badge">{user.role.upper()}</span>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Logout"):
            logout()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 My Tasks", "🚀 Execute Task", "📊 Completed", "🎯 Performance"
    ])
    
    with tab1:
        my_tasks_view()
    
    with tab2:
        execute_task_interface()
    
    with tab3:
        completed_tasks_view()
    
    with tab4:
        performance_metrics()

def my_tasks_view():
    """View assigned tasks"""
    st.markdown("### 📋 My Assigned Tasks")
    
    # Get user's tasks from plans
    user_tasks = []
    for plan in st.session_state.active_plans.values():
        for task in plan.get('tasks', []):
            if task.get('assigned_to') == st.session_state.user.email:
                user_tasks.append({
                    'plan_name': plan['name'],
                    'plan_id': plan['id'],
                    **task
                })
    
    if not user_tasks:
        st.info("No tasks assigned yet. Check back later!")
        return
    
    # Priority filter
    priority_filter = st.selectbox("Filter by Priority", 
                                  ["All", "High", "Medium", "Low"])
    
    # Display tasks
    for task in user_tasks:
        status = task.get('status', 'pending')
        priority = task.get('priority', 'medium')
        
        # Task card
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div class="task-card">
                    <h4>{task['name']}</h4>
                    <p><strong>Plan:</strong> {task['plan_name']}</p>
                    <p><strong>Type:</strong> {task.get('type', 'Analysis')}</p>
                    <p><strong>Description:</strong> {task.get('description', 'Perform analysis task')}</p>
                    <p><strong>Deadline:</strong> {task.get('deadline', 'No deadline')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**Status:** {status.title()}")
                st.markdown(f"**Priority:** {priority.title()}")
            
            with col3:
                if status == 'pending':
                    if st.button(f"▶️ Start", key=f"start_{task['id']}"):
                        task['status'] = 'in_progress'
                        st.success("Task started!")
                        st.rerun()
                elif status == 'in_progress':
                    if st.button(f"🎯 Execute", key=f"exec_{task['id']}"):
                        st.session_state.current_task = task
                        st.rerun()

def execute_task_interface():
    """Interface for executing analysis tasks"""
    st.markdown("### 🚀 Execute Analysis Task")
    
    if 'current_task' not in st.session_state or not st.session_state.current_task:
        st.info("Select a task from 'My Tasks' to execute")
        return
    
    task = st.session_state.current_task
    
    # Task details
    st.markdown(f"#### Task: {task['name']}")
    st.markdown(f"**Description:** {task.get('description', 'Analysis task')}")
    
    # Get associated data
    plan = st.session_state.active_plans.get(task['plan_id'])
    data_id = plan.get('data_id') if plan else None
    data = st.session_state.uploaded_data.get(data_id) if data_id else None
    
    if data is not None:
        st.markdown("#### 📊 Data Preview")
        st.dataframe(data.head(10), use_container_width=True)
        st.markdown(f"**Shape:** {data.shape[0]} rows × {data.shape[1]} columns")
    
    # Execution options
    col1, col2 = st.columns(2)
    with col1:
        execution_mode = st.selectbox("Execution Mode", 
                                     ["Automated (AI)", "Marimo Notebook", "Manual"])
    with col2:
        confidence_threshold = st.slider("Quality Threshold", 0.0, 1.0, 0.7)
    
    # Execute button
    if st.button("🎯 Execute Analysis", use_container_width=True):
        with st.spinner(f"Executing {task['name']}..."):
            # Use real task executor
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Show progress steps
            status_text.text("Initializing analysis engine...")
            progress_bar.progress(0.2)
            time.sleep(0.5)
            
            # Execute task with real data
            if data is not None:
                status_text.text("Running analysis...")
                progress_bar.progress(0.5)
                
                # Execute using TaskExecutor
                results = st.session_state.task_executor.execute_task(task, data)
                
                progress_bar.progress(0.8)
                status_text.text("Finalizing results...")
                time.sleep(0.5)
                
                progress_bar.progress(1.0)
            else:
                # Fallback if no data
                results = {
                    'task_id': task['id'],
                    'task_name': task['name'],
                    'status': 'completed',
                    'results': {'error': 'No data available for analysis'},
                    'confidence': 0.0,
                    'quality_score': 0.0,
                    'execution_time': '0.1 seconds',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Store results
            st.session_state.task_results[task['id']] = results
            
            # Update task status
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            
            # Update user's completed tasks
            auth_manager.complete_user_task(st.session_state.user.email, task['id'])
            
            if results.get('status') == 'success':
                st.success("✅ Task completed successfully!")
            elif results.get('status') == 'failed':
                st.error(f"❌ Task failed: {results.get('error', 'Unknown error')}")
            else:
                st.warning("⚠️ Task completed with warnings")
            
            # Display results
            st.markdown("#### 📊 Results")
            
            if results.get('status') == 'success':
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence", f"{results.get('confidence', 0)*100:.0f}%")
                with col2:
                    st.metric("Quality Score", f"{results.get('quality_score', 0)*100:.0f}%")
                with col3:
                    st.metric("Execution Time", results.get('execution_time', 'N/A'))
                
                # Display insights from actual results
                if 'results' in results and isinstance(results['results'], dict):
                    task_results = results['results']
                    
                    # Show insights
                    if 'insights' in task_results and task_results['insights']:
                        st.markdown("#### 💡 Key Insights")
                        for insight in task_results['insights']:
                            st.markdown(f"- {insight}")
                    
                    # Show statistics if available
                    if 'statistics' in task_results:
                        st.markdown("#### 📈 Statistics")
                        st.json(task_results['statistics'])
                    
                    # Show metrics if available
                    if 'metrics' in task_results:
                        st.markdown("#### 📊 Model Metrics")
                        metrics_df = pd.DataFrame([task_results['metrics']])
                        st.dataframe(metrics_df)
                    
                    # Show data profile if available
                    if 'shape' in task_results:
                        st.markdown("#### 📋 Data Profile")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Rows", task_results['shape']['rows'])
                            st.metric("Columns", task_results['shape']['columns'])
                        with col2:
                            if 'missing_values' in task_results:
                                total_missing = sum(task_results['missing_values'].values())
                                st.metric("Missing Values", total_missing)
                            if 'duplicates' in task_results:
                                st.metric("Duplicates", task_results['duplicates'])
                    
                    # Show correlations if available
                    if 'high_correlations' in task_results or 'strong_correlations' in task_results:
                        st.markdown("#### 🔗 Correlations")
                        corr_data = task_results.get('high_correlations') or task_results.get('strong_correlations', [])
                        if corr_data:
                            corr_df = pd.DataFrame(corr_data)
                            st.dataframe(corr_df)
            
            # Sample visualization
            if data is not None and len(data.columns) >= 2:
                fig = px.scatter(data.head(100), 
                               x=data.columns[0], 
                               y=data.columns[1],
                               title="Data Analysis Visualization")
                st.plotly_chart(fig, use_container_width=True)
            
            # Clear current task
            st.session_state.current_task = None

def completed_tasks_view():
    """View completed tasks"""
    st.markdown("### ✅ Completed Tasks")
    
    completed = []
    for task_id, result in st.session_state.task_results.items():
        completed.append(result)
    
    if not completed:
        st.info("No completed tasks yet. Start working on your assigned tasks!")
        return
    
    # Display completed tasks
    for result in completed:
        with st.expander(f"✅ {result['task_name']} - {result['timestamp'][:10]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Status:** {result['status'].title()}")
                st.markdown(f"**Confidence:** {result['confidence']*100:.0f}%")
                st.markdown(f"**Quality Score:** {result['metrics']['quality_score']*100:.0f}%")
                st.markdown(f"**Execution Time:** {result['execution_time']}")
            
            with col2:
                st.markdown("**Insights:**")
                for insight in result['insights']:
                    st.markdown(f"- {insight}")

def performance_metrics():
    """Display performance metrics for analyst"""
    st.markdown("### 🎯 My Performance")
    
    # Mock performance data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tasks Completed", 24, delta="+3 this week")
    
    with col2:
        st.metric("Avg Quality Score", "92%", delta="+2%")
    
    with col3:
        st.metric("Avg Execution Time", "3.2s", delta="-0.5s")
    
    with col4:
        st.metric("Success Rate", "98%", delta="+1%")
    
    # Performance trend
    st.markdown("#### 📈 Performance Trend")
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    performance_data = pd.DataFrame({
        'Date': dates,
        'Tasks': [5 + i//3 for i in range(30)],
        'Quality': [88 + (i % 10) for i in range(30)]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=performance_data['Date'], 
                            y=performance_data['Tasks'],
                            mode='lines+markers',
                            name='Tasks Completed',
                            yaxis='y'))
    fig.add_trace(go.Scatter(x=performance_data['Date'], 
                            y=performance_data['Quality'],
                            mode='lines',
                            name='Quality Score',
                            yaxis='y2'))
    
    fig.update_layout(
        title="Performance Over Time",
        yaxis=dict(title="Tasks"),
        yaxis2=dict(title="Quality %", overlaying='y', side='right'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Skills assessment
    st.markdown("#### 💪 Skills Assessment")
    
    skills = ['Python', 'SQL', 'Machine Learning', 'Data Visualization', 'Statistics']
    scores = [95, 88, 82, 90, 85]
    
    fig = go.Figure(data=[
        go.Bar(x=skills, y=scores, marker_color='lightblue')
    ])
    fig.update_layout(title="Skill Proficiency", yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)

# Helper functions
def view_plan_details(plan_id):
    """View detailed plan information"""
    plan = st.session_state.active_plans.get(plan_id)
    if plan:
        st.markdown(f"### Plan: {plan['name']}")
        st.json(plan)

def generate_plan_report(plan_id):
    """Generate report for a plan"""
    plan = st.session_state.active_plans.get(plan_id)
    if not plan:
        st.error("Plan not found")
        return
    
    # Get all task results for this plan
    plan_task_ids = [task['id'] for task in plan.get('tasks', [])]
    plan_task_results = [st.session_state.task_results.get(tid) 
                         for tid in plan_task_ids 
                         if tid in st.session_state.task_results]
    
    if not plan_task_results:
        st.warning("No completed tasks found for this plan. Execute tasks first.")
        return
    
    with st.spinner("Generating comprehensive report..."):
        # Aggregate results
        aggregated = st.session_state.report_generator.aggregate_plan_results(plan, plan_task_results)
        
        # Generate executive report
        report = st.session_state.report_generator.generate_executive_report(aggregated)
        
        # Store report
        st.session_state.plan_reports[plan_id] = report
        
        # Display report
        st.markdown(f"# {report['title']}")
        st.markdown(f"*Generated: {report['generated_at']}*")
        
        # Display each section
        for section_key, section in report['sections'].items():
            st.markdown(f"## {section['title']}")
            st.markdown(section['content'])
        
        # Download options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate HTML version
            html_report = st.session_state.report_generator.export_report_to_html(report)
            st.download_button(
                label="📥 Download HTML Report",
                data=html_report,
                file_name=f"report_{plan['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )
        
        with col2:
            # Generate JSON version
            st.download_button(
                label="📥 Download JSON Data",
                data=json.dumps(report, indent=2),
                file_name=f"report_{plan['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        st.success("✅ Report generated successfully!")

# Main app logic
def main():
    """Main application"""
    if not st.session_state.authenticated:
        login_page()
    else:
        # Validate session
        user = auth_manager.validate_session(st.session_state.session_token)
        if not user:
            st.session_state.authenticated = False
            st.session_state.session_token = None
            st.session_state.user = None
            st.rerun()
        
        # Route based on role
        if user.role == 'manager':
            manager_dashboard()
        elif user.role in ['analyst', 'associate']:
            associate_dashboard()
        else:
            st.error("Unknown user role")
            logout()

if __name__ == "__main__":
    main()