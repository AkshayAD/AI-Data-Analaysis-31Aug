#!/usr/bin/env python3
"""
AI Data Analysis Platform - Enterprise Edition
Complete integration of all features with human-in-the-loop workflows
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import sys
import os
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src/python to path
sys.path.append(str(Path(__file__).parent / "src" / "python"))

# Import all the developed components
try:
    from auth.authentication import AuthenticationManager, UserRole
    from workflow.workflow_manager import WorkflowManager, TaskType, TaskStatus
    from execution.task_executor import TaskExecutor
    from reporting.report_generator import ReportGenerator
    from marimo_integration.notebook_generator import NotebookGenerator
    from agents import DataAnalysisAgent, MLAgent, VisualizationAgent
    from llm import GeminiClient
    from agents.intelligent_agent import IntelligentAgent
except ImportError as e:
    logger.warning(f"Import error: {e}. Using fallback implementations.")
    # Fallback implementations will be created below

st.set_page_config(
    page_title="AI Data Analysis Platform - Enterprise",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2e5c87 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: #28a745;
        color: white;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-left: 1rem;
    }
    
    .task-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    
    .approval-needed {
        border-left: 4px solid #ffc107;
        background: #fff9e6;
    }
    
    .approved {
        border-left: 4px solid #28a745;
        background: #f0f8f0;
    }
    
    .in-progress {
        border-left: 4px solid #007bff;
        background: #f0f7ff;
    }
    
    .metrics-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        flex: 1;
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'user_role': None,
        'user_info': None,
        'current_plan': None,
        'active_tasks': [],
        'notifications': [],
        'workflow_manager': None,
        'task_executor': None,
        'report_generator': None,
        'auth_manager': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Fallback implementations for missing components
class FallbackAuthManager:
    """Fallback authentication manager"""
    def __init__(self):
        self.demo_users = {
            'manager@company.com': {'password': 'manager123', 'role': 'manager', 'name': 'Sarah Manager'},
            'analyst@company.com': {'password': 'analyst123', 'role': 'senior_analyst', 'name': 'Alex Analyst'},
            'associate@company.com': {'password': 'associate123', 'role': 'analyst', 'name': 'Jordan Associate'},
            'demo@company.com': {'password': 'demo123', 'role': 'manager', 'name': 'Demo User'}
        }
    
    def authenticate(self, email, password):
        """Authenticate user"""
        if email in self.demo_users and self.demo_users[email]['password'] == password:
            return self.demo_users[email]
        return None
    
    def get_user_info(self, email):
        """Get user information"""
        return self.demo_users.get(email)

class FallbackWorkflowManager:
    """Fallback workflow manager"""
    def __init__(self):
        self.plans = {}
        self.tasks = {}
    
    def create_plan(self, name, objectives, data_sources=None, auto_generate_tasks=True):
        """Create analysis plan"""
        plan_id = str(uuid.uuid4())
        plan = {
            'id': plan_id,
            'name': name,
            'objectives': objectives,
            'data_sources': data_sources or [],
            'auto_generate_tasks': auto_generate_tasks,
            'status': 'draft',
            'created_at': datetime.now(),
            'tasks': []
        }
        
        if auto_generate_tasks:
            plan['tasks'] = self._generate_tasks_from_objectives(objectives)
        
        self.plans[plan_id] = plan
        return plan
    
    def _generate_tasks_from_objectives(self, objectives):
        """Auto-generate tasks from objectives"""
        base_tasks = [
            {'type': 'data_profiling', 'name': 'Data Quality Assessment', 'priority': 'high'},
            {'type': 'statistical_analysis', 'name': 'Statistical Analysis', 'priority': 'medium'},
            {'type': 'visualization', 'name': 'Data Visualization', 'priority': 'medium'}
        ]
        
        # Add objective-specific tasks
        additional_tasks = []
        for obj in objectives:
            obj_lower = obj.lower()
            if 'trend' in obj_lower or 'time' in obj_lower:
                additional_tasks.append({'type': 'time_series', 'name': 'Time Series Analysis', 'priority': 'high'})
            if 'predict' in obj_lower or 'forecast' in obj_lower:
                additional_tasks.append({'type': 'predictive_modeling', 'name': 'Predictive Modeling', 'priority': 'high'})
            if 'segment' in obj_lower or 'cluster' in obj_lower:
                additional_tasks.append({'type': 'segmentation', 'name': 'Customer Segmentation', 'priority': 'medium'})
            if 'anomaly' in obj_lower or 'outlier' in obj_lower:
                additional_tasks.append({'type': 'anomaly_detection', 'name': 'Anomaly Detection', 'priority': 'medium'})
        
        all_tasks = base_tasks + additional_tasks
        
        # Add IDs and metadata
        for i, task in enumerate(all_tasks):
            task.update({
                'id': str(uuid.uuid4()),
                'status': 'pending',
                'assigned_to': None,
                'created_at': datetime.now(),
                'estimated_duration': '2-4 hours'
            })
        
        return all_tasks
    
    def approve_plan(self, plan_id):
        """Approve a plan for execution"""
        if plan_id in self.plans:
            self.plans[plan_id]['status'] = 'approved'
            self.plans[plan_id]['approved_at'] = datetime.now()
            return True
        return False

class FallbackTaskExecutor:
    """Fallback task executor"""
    def execute_task(self, task, data=None):
        """Execute analysis task"""
        # Simulate task execution
        return {
            'status': 'success',
            'results': {
                'summary': f"Analysis completed for {task.get('name', 'Unknown Task')}",
                'insights': ['Key insight 1', 'Key insight 2'],
                'confidence': 0.85
            },
            'execution_time': '2.3 seconds'
        }

class FallbackReportGenerator:
    """Fallback report generator"""
    def generate_executive_report(self, plan, results):
        """Generate executive report"""
        return {
            'title': f"Executive Report: {plan['name']}",
            'summary': 'Analysis completed successfully with high confidence.',
            'key_findings': ['Finding 1', 'Finding 2', 'Finding 3'],
            'recommendations': ['Recommendation 1', 'Recommendation 2'],
            'generated_at': datetime.now().isoformat()
        }

# Initialize enterprise integration
@st.cache_resource
def init_enterprise_integration(gemini_api_key=None):
    """Initialize the enterprise integration system"""
    try:
        return get_enterprise_integration(gemini_api_key=gemini_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize enterprise integration: {e}")
        # Return a fallback implementation
        from integration.enterprise_integration import EnterpriseIntegration
        return EnterpriseIntegration(gemini_api_key=gemini_api_key)

def render_login_page():
    """Render login page"""
    st.markdown('<div class="main-header"><h1>🏢 AI Data Analysis Platform - Enterprise</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            st.markdown("**Demo Accounts:**")
            st.markdown("""
            - **Manager**: `manager@company.com` / `manager123`
            - **Senior Analyst**: `analyst@company.com` / `analyst123`
            - **Associate**: `associate@company.com` / `associate123`
            - **Demo User**: `demo@company.com` / `demo123`
            """)
            
            if st.form_submit_button("Login", use_container_width=True):
                if email and password:
                    # Initialize enterprise integration with API key if provided
                    gemini_key = st.session_state.get('gemini_api_key')
                    enterprise_integration = init_enterprise_integration(gemini_key)
                    
                    user_info = enterprise_integration.auth_manager.authenticate(email, password)
                    
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user_role = user_info['role']
                        st.session_state.user_info = user_info
                        st.session_state.user_email = email
                        st.session_state.enterprise_integration = enterprise_integration
                        st.success(f"Welcome, {user_info['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                else:
                    st.error("Please enter email and password")

def render_manager_dashboard():
    """Render manager dashboard"""
    st.markdown(f'<div class="main-header"><h1>📊 Manager Dashboard</h1><span class="role-badge">Manager</span></div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select Page", [
            "Overview",
            "Create Plan",
            "Active Plans", 
            "Approval Queue",
            "Team Dashboard",
            "Reports"
        ])
    
    if page == "Overview":
        render_manager_overview()
    elif page == "Create Plan":
        render_plan_creation()
    elif page == "Active Plans":
        render_active_plans()
    elif page == "Approval Queue":
        render_approval_queue()
    elif page == "Team Dashboard":
        render_team_dashboard()
    elif page == "Reports":
        render_reports_dashboard()

def render_manager_overview():
    """Render manager overview page"""
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Plans", 3, delta=1)
    with col2:
        st.metric("Pending Approvals", 5, delta=-2)
    with col3:
        st.metric("Team Utilization", "85%", delta="5%")
    with col4:
        st.metric("Avg Completion Time", "2.3 days", delta="-0.5 days")
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    activity_data = [
        {"time": "2 hours ago", "activity": "Q4 Sales Analysis - Completed", "user": "Alex Analyst"},
        {"time": "4 hours ago", "activity": "Customer Segmentation - In Progress", "user": "Jordan Associate"},
        {"time": "6 hours ago", "activity": "Revenue Forecast - Approved", "user": "Sarah Manager"},
        {"time": "1 day ago", "activity": "Market Analysis - Started", "user": "Alex Analyst"}
    ]
    
    for activity in activity_data:
        with st.container():
            st.markdown(f"**{activity['time']}** - {activity['activity']} (*{activity['user']}*)")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🆕 Create New Plan", use_container_width=True):
            st.session_state.sidebar_page = "Create Plan"
            st.rerun()
    
    with col2:
        if st.button("✅ Review Approvals", use_container_width=True):
            st.session_state.sidebar_page = "Approval Queue"
            st.rerun()
    
    with col3:
        if st.button("📊 View Reports", use_container_width=True):
            st.session_state.sidebar_page = "Reports"
            st.rerun()

def render_plan_creation():
    """Render plan creation interface"""
    st.markdown("### 🆕 Create Analysis Plan")
    
    with st.form("create_plan_form"):
        plan_name = st.text_input("Plan Name", placeholder="e.g., Q4 Sales Analysis")
        
        st.markdown("**Business Objectives:**")
        objectives = []
        
        # Dynamic objective input
        if 'objective_count' not in st.session_state:
            st.session_state.objective_count = 1
        
        for i in range(st.session_state.objective_count):
            obj = st.text_input(f"Objective {i+1}", key=f"objective_{i}", 
                              placeholder="e.g., Identify revenue trends")
            if obj:
                objectives.append(obj)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("+ Add Objective"):
                st.session_state.objective_count += 1
                st.rerun()
        
        # Data sources
        st.markdown("**Data Sources:**")
        uploaded_files = st.file_uploader("Upload datasets", accept_multiple_files=True, type=['csv', 'xlsx'])
        
        # Configuration options
        st.markdown("**Configuration:**")
        auto_generate = st.checkbox("Auto-generate tasks from objectives", value=True)
        auto_assign = st.checkbox("Auto-assign to team based on skills", value=True)
        
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        deadline = st.date_input("Target Completion", value=datetime.now() + timedelta(days=7))
        
        # Submit plan
        if st.form_submit_button("Create Plan", use_container_width=True):
            if plan_name and objectives:
                # Create plan using enterprise integration
                enterprise_integration = st.session_state.enterprise_integration
                user_email = st.session_state.user_email
                
                result = enterprise_integration.create_analysis_plan(
                    user_email=user_email,
                    plan_name=plan_name,
                    objectives=objectives,
                    data_sources=[f.name for f in uploaded_files] if uploaded_files else []
                )
                
                if 'error' in result:
                    st.error(result['error'])
                else:
                    plan = result['plan']
                    st.session_state.current_plan = plan
                    st.success(f"Plan '{plan_name}' created successfully and sent for approval!")
                    
                    # Show generated tasks for review
                    if plan.get('tasks'):
                        st.markdown("### 🤖 Auto-Generated Tasks")
                        
                        for i, task in enumerate(plan['tasks']):
                            with st.expander(f"Task {i+1}: {task['name']}"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write(f"**Type:** {task.get('type', 'N/A')}")
                                with col2:
                                    st.write(f"**Priority:** {task.get('priority', 'N/A')}")
                                with col3:
                                    st.write(f"**Duration:** {task.get('estimated_hours', 'N/A')} hours")
                                
                                # Show dependencies if any
                                deps = task.get('dependencies', [])
                                if deps:
                                    st.write(f"**Dependencies:** {', '.join(deps)}")
                        
                        st.info(f"📋 Plan created with {len(plan['tasks'])} tasks. Waiting for manager approval to begin execution.")
                        
                        # Show approval status
                        if result.get('status') == 'awaiting_approval':
                            st.warning("⏳ Plan is pending approval. You will be notified once approved.")
            else:
                st.error("Please enter plan name and at least one objective")

def render_active_plans():
    """Render active plans interface"""
    st.markdown("### 📋 Active Plans")
    
    # Mock active plans data
    plans = [
        {
            'name': 'Q4 Sales Analysis',
            'status': 'In Progress',
            'progress': 75,
            'tasks_total': 8,
            'tasks_complete': 6,
            'assigned_to': ['Alex Analyst', 'Jordan Associate'],
            'deadline': '2024-12-31'
        },
        {
            'name': 'Customer Retention Study',
            'status': 'Planning',
            'progress': 10,
            'tasks_total': 6,
            'tasks_complete': 0,
            'assigned_to': ['Alex Analyst'],
            'deadline': '2025-01-15'
        }
    ]
    
    for plan in plans:
        with st.container():
            st.markdown(f"""
            <div class="task-card in-progress">
                <h4>{plan['name']}</h4>
                <p><strong>Status:</strong> {plan['status']} | <strong>Progress:</strong> {plan['progress']}%</p>
                <p><strong>Tasks:</strong> {plan['tasks_complete']}/{plan['tasks_total']} complete</p>
                <p><strong>Assigned to:</strong> {', '.join(plan['assigned_to'])}</p>
                <p><strong>Deadline:</strong> {plan['deadline']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Progress bar
            st.progress(plan['progress'] / 100)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button(f"View Details", key=f"view_{plan['name']}")
            with col2:
                st.button(f"Monitor", key=f"monitor_{plan['name']}")
            with col3:
                st.button(f"Edit", key=f"edit_{plan['name']}")
            with col4:
                st.button(f"Reports", key=f"reports_{plan['name']}")

def render_approval_queue():
    """Render approval queue interface"""
    st.markdown("### ✅ Approval Queue")
    
    # Get real approval queue from enterprise integration
    enterprise_integration = st.session_state.enterprise_integration
    user_role = st.session_state.user_role
    
    approvals = enterprise_integration.get_approval_queue(user_role=user_role)
    
    if not approvals:
        st.info("No pending approvals at this time.")
        return
    
    st.markdown(f"**{len(approvals)} items awaiting approval**")
    
    for approval in approvals:
        with st.container():
            approval_type = approval.get('type', 'Unknown')
            title = approval.get('title', 'No Title')
            submitter = approval.get('submitter', 'Unknown')
            submitted_at = approval.get('submitted_at', 'Unknown')
            
            st.markdown(f"""
            <div class="task-card approval-needed">
                <h4>{approval_type.title()}: {title}</h4>
                <p><strong>From:</strong> {submitter} | <strong>Submitted:</strong> {submitted_at}</p>
                <p><strong>Status:</strong> {approval.get('status', 'Pending')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show content preview for plan approvals
            if approval_type == 'plan':
                plan_content = approval.get('content', {})
                objectives = plan_content.get('objectives', [])
                tasks = plan_content.get('tasks', [])
                
                with st.expander(f"📋 Plan Details: {len(tasks)} tasks"):
                    st.markdown("**Objectives:**")
                    for i, obj in enumerate(objectives, 1):
                        st.markdown(f"{i}. {obj}")
                    
                    st.markdown("**Generated Tasks:**")
                    for task in tasks[:5]:  # Show first 5 tasks
                        st.markdown(f"• {task.get('name', 'Unnamed Task')} ({task.get('type', 'unknown')})")
                    
                    if len(tasks) > 5:
                        st.markdown(f"... and {len(tasks) - 5} more tasks")
            
            col1, col2, col3, col4 = st.columns(4)
            
            approval_id = approval.get('id')
            user_email = st.session_state.user_email
            
            with col1:
                if st.button("👁️ Review", key=f"review_{approval_id}"):
                    st.json(approval.get('content', {}))
            
            with col2:
                if st.button("✅ Approve", key=f"approve_{approval_id}"):
                    if approval_type == 'plan':
                        result = enterprise_integration.approve_plan(
                            approval_request_id=approval_id,
                            approver_email=user_email
                        )
                        if 'error' in result:
                            st.error(result['error'])
                        else:
                            st.success(f"✅ Plan approved! {len(result.get('task_assignments', []))} tasks assigned to team.")
                            st.rerun()
                    else:
                        st.success(f"Approved: {title}")
            
            with col3:
                if st.button("❌ Reject", key=f"reject_{approval_id}"):
                    st.error(f"Rejected: {title}")
            
            with col4:
                if st.button("💬 Comment", key=f"comment_{approval_id}"):
                    comment = st.text_input("Add comment:", key=f"comment_text_{approval_id}")
                    if comment:
                        st.success(f"Comment added: {comment}")
            
            st.markdown("---")

def render_team_dashboard():
    """Render team performance dashboard"""
    st.markdown("### 👥 Team Dashboard")
    
    # Team metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Team Members", 5)
    with col2:
        st.metric("Active Tasks", 12)
    with col3:
        st.metric("Avg Quality Score", "87%", delta="3%")
    with col4:
        st.metric("On-Time Delivery", "94%", delta="2%")
    
    # Team member performance
    st.markdown("### 📊 Team Performance")
    
    team_data = {
        'Member': ['Alex Analyst', 'Jordan Associate', 'Sam Senior', 'Riley Research', 'Casey Code'],
        'Active Tasks': [3, 2, 4, 1, 2],
        'Completed': [15, 8, 22, 5, 11],
        'Quality Score': [92, 78, 95, 85, 88],
        'Specialization': ['Time Series', 'Visualization', 'ML Models', 'Statistics', 'Data Engineering']
    }
    
    df = pd.DataFrame(team_data)
    
    # Create performance chart
    fig = px.scatter(df, x='Completed', y='Quality Score', 
                    size='Active Tasks', hover_name='Member',
                    title="Team Performance: Completed Tasks vs Quality Score")
    st.plotly_chart(fig, use_container_width=True)
    
    # Team table
    st.dataframe(df, use_container_width=True)

def render_reports_dashboard():
    """Render reports dashboard"""
    st.markdown("### 📊 Reports Dashboard")
    
    # Report filters
    col1, col2, col3 = st.columns(3)
    with col1:
        time_period = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days"])
    with col2:
        report_type = st.selectbox("Report Type", ["All", "Executive Summary", "Technical", "Performance"])
    with col3:
        status_filter = st.selectbox("Status", ["All", "Completed", "Draft", "Under Review"])
    
    # Available reports
    reports = [
        {
            'title': 'Q4 Sales Analysis - Executive Summary',
            'type': 'Executive Summary',
            'status': 'Completed',
            'generated': '2024-12-30',
            'confidence': 94,
            'downloads': 23
        },
        {
            'title': 'Customer Segmentation Technical Report',
            'type': 'Technical',
            'status': 'Under Review', 
            'generated': '2024-12-29',
            'confidence': 87,
            'downloads': 8
        },
        {
            'title': 'Team Performance Analysis',
            'type': 'Performance',
            'status': 'Completed',
            'generated': '2024-12-28',
            'confidence': 91,
            'downloads': 15
        }
    ]
    
    for report in reports:
        with st.container():
            st.markdown(f"""
            <div class="task-card approved">
                <h4>{report['title']}</h4>
                <p><strong>Type:</strong> {report['type']} | <strong>Status:</strong> {report['status']}</p>
                <p><strong>Generated:</strong> {report['generated']} | <strong>Confidence:</strong> {report['confidence']}%</p>
                <p><strong>Downloads:</strong> {report['downloads']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("📄 View", key=f"view_report_{report['title']}")
            with col2:
                st.button("📥 Download", key=f"download_{report['title']}")
            with col3:
                st.button("📤 Share", key=f"share_{report['title']}")
            with col4:
                st.button("📊 Analytics", key=f"analytics_{report['title']}")

def render_analyst_workspace():
    """Render analyst workspace"""
    st.markdown(f'<div class="main-header"><h1>🔬 Analyst Workspace</h1><span class="role-badge">Analyst</span></div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select Page", [
            "My Tasks",
            "Data Explorer",
            "Analysis Tools",
            "Marimo Notebooks", 
            "Collaboration",
            "Submissions"
        ])
    
    if page == "My Tasks":
        render_analyst_tasks()
    elif page == "Data Explorer":
        render_data_explorer()
    elif page == "Analysis Tools":
        render_analysis_tools()
    elif page == "Marimo Notebooks":
        render_marimo_interface()
    elif page == "Collaboration":
        render_collaboration()
    elif page == "Submissions":
        render_submissions()

def render_analyst_tasks():
    """Render analyst tasks interface"""
    st.markdown("### 📋 My Tasks")
    
    # Get real tasks from enterprise integration
    enterprise_integration = st.session_state.enterprise_integration
    user_email = st.session_state.user_email
    
    user_tasks = enterprise_integration.get_user_tasks(user_email)
    
    if not user_tasks:
        st.info("No tasks assigned at this time. New tasks will appear here once plans are approved.")
        return
    
    # Task filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["All", "Assigned", "In Progress", "Review"])
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with col3:
        type_filter = st.selectbox("Type", ["All", "Analysis", "Modeling", "Visualization"])
    
    # Display user tasks
    st.markdown(f"**{len(user_tasks)} tasks assigned to you**")
    
    for user_task in user_tasks:
        task = user_task['task']
        plan_name = user_task['plan_name']
        
        # Apply filters
        if status_filter != "All" and task.get('status', '').value != status_filter.upper().replace(' ', '_'):
            continue
        if priority_filter != "All" and task.get('priority', '').title() != priority_filter:
            continue
    
    for user_task in user_tasks:
        task = user_task['task']
        plan_name = user_task['plan_name']
        
        with st.container():
            # Task header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"#### {task['name']}")
                st.markdown(f"**Plan:** {plan_name} | **Type:** {task.get('type', 'N/A')} | **Priority:** {task.get('priority', 'N/A')}")
            with col2:
                status_color = {"ASSIGNED": "🟡", "IN_PROGRESS": "🔵", "COMPLETED": "🟢", "PENDING": "⚪"}
                task_status = task.get('status', 'PENDING')
                if hasattr(task_status, 'value'):
                    task_status = task_status.value
                st.markdown(f"**Status:** {status_color.get(task_status, '⚪')} {task_status.replace('_', ' ').title()}")
            
            # Task details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"⏱️ **Estimated:** {task.get('estimated_hours', 'N/A')} hours")
            with col2:
                created_at = task.get('created_at', 'N/A')
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d')
                st.markdown(f"📅 **Created:** {created_at}")
            with col3:
                notebook_path = task.get('notebook_path')
                if notebook_path:
                    st.markdown("📓 **Notebook:** Ready")
                else:
                    st.markdown("📓 **Notebook:** Generating...")
            
            # Show task description
            if task.get('description'):
                st.markdown(f"**Description:** {task['description']}")
            
            # Show dependencies
            deps = task.get('dependencies', [])
            if deps:
                st.markdown(f"**Dependencies:** {', '.join(deps)}")
            
            # Action buttons
            col1, col2, col3, col4, col5 = st.columns(5)
            
            task_id = task.get('id')
            is_assigned = task_status == 'ASSIGNED'
            is_in_progress = task_status == 'IN_PROGRESS'
            
            with col1:
                if st.button("▶️ Start", key=f"start_{task_id}", disabled=not is_assigned):
                    # Start task execution
                    result = enterprise_integration.execute_task(
                        task_id=task_id,
                        user_email=user_email
                    )
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success(f"Started task: {task['name']}")
                        st.rerun()
            
            with col2:
                if st.button("📓 Notebook", key=f"notebook_{task_id}", disabled=not notebook_path):
                    st.session_state.current_task = task
                    st.info(f"Opening Marimo notebook: {notebook_path}")
            
            with col3:
                if st.button("📊 Data", key=f"data_{task_id}"):
                    st.info("Opening data explorer...")
            
            with col4:
                if st.button("💬 Chat", key=f"chat_{task_id}"):
                    st.info("Opening collaboration chat...")
            
            with col5:
                if st.button("✅ Submit", key=f"submit_{task_id}", disabled=not is_in_progress):
                    # Execute and submit task
                    result = enterprise_integration.execute_task(
                        task_id=task_id,
                        user_email=user_email
                    )
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        st.success(f"Task submitted: {result.get('message', 'Success!')}")
                        st.rerun()
            
            st.markdown("---")

def render_data_explorer():
    """Render data explorer interface"""
    st.markdown("### 📊 Data Explorer")
    
    # File upload
    uploaded_file = st.file_uploader("Upload dataset", type=['csv', 'xlsx'])
    
    # Sample data option
    use_sample = st.checkbox("Use sample data")
    
    if use_sample:
        # Generate sample sales data
        import numpy as np
        dates = pd.date_range('2024-01-01', periods=365, freq='D')
        sample_data = pd.DataFrame({
            'date': dates,
            'sales': 1000 + np.random.normal(0, 100, 365) + np.sin(np.arange(365) * 2 * np.pi / 365) * 200,
            'customers': 50 + np.random.normal(0, 10, 365),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 365),
            'product': np.random.choice(['A', 'B', 'C', 'D'], 365)
        })
        st.session_state.data = sample_data
        
    elif uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.data = df
    
    # Display data if available
    if 'data' in st.session_state:
        df = st.session_state.data
        
        # Data overview
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric("Missing Values", df.isnull().sum().sum())
        with col4:
            st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Data preview
        st.markdown("#### Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Quick insights
        st.markdown("#### Quick Insights")
        
        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            st.markdown("**Numeric Columns Summary:**")
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        # Missing values chart
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            st.markdown("**Missing Values by Column:**")
            fig = px.bar(x=missing_data.index, y=missing_data.values, 
                        title="Missing Values by Column")
            st.plotly_chart(fig, use_container_width=True)
        
        # Data types
        st.markdown("**Data Types:**")
        type_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.astype(str),
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum()
        })
        st.dataframe(type_df, use_container_width=True)

def render_analysis_tools():
    """Render analysis tools interface"""
    st.markdown("### 🛠️ Analysis Tools")
    
    if 'data' not in st.session_state:
        st.warning("Please upload data in the Data Explorer first")
        return
    
    df = st.session_state.data
    
    # Tool selection
    analysis_type = st.selectbox("Select Analysis Tool", [
        "Statistical Analysis",
        "Time Series Analysis", 
        "Correlation Analysis",
        "Anomaly Detection",
        "Clustering",
        "Predictive Modeling"
    ])
    
    if analysis_type == "Statistical Analysis":
        st.markdown("#### 📈 Statistical Analysis")
        
        # Column selection
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        selected_cols = st.multiselect("Select columns", numeric_cols, default=list(numeric_cols[:3]))
        
        if selected_cols and st.button("Run Analysis"):
            # Descriptive statistics
            st.markdown("**Descriptive Statistics:**")
            st.dataframe(df[selected_cols].describe())
            
            # Distribution plots
            for col in selected_cols:
                fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                st.plotly_chart(fig, use_container_width=True)
    
    elif analysis_type == "Time Series Analysis":
        st.markdown("#### 📊 Time Series Analysis")
        
        # Date column selection
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].head())
                    date_cols.append(col)
                except:
                    pass
        
        if date_cols:
            date_col = st.selectbox("Select date column", date_cols)
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            value_col = st.selectbox("Select value column", numeric_cols)
            
            if st.button("Run Time Series Analysis"):
                # Convert to datetime and sort
                df_ts = df.copy()
                df_ts[date_col] = pd.to_datetime(df_ts[date_col])
                df_ts = df_ts.sort_values(date_col)
                
                # Time series plot
                fig = px.line(df_ts, x=date_col, y=value_col, 
                             title=f"Time Series: {value_col} over {date_col}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Basic trend analysis
                if len(df_ts) > 1:
                    first_value = df_ts[value_col].iloc[0]
                    last_value = df_ts[value_col].iloc[-1]
                    change = ((last_value - first_value) / first_value) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("First Value", f"{first_value:.2f}")
                    with col2:
                        st.metric("Last Value", f"{last_value:.2f}")
                    with col3:
                        st.metric("Total Change", f"{change:.1f}%")
        else:
            st.info("No date columns detected in the data")

def render_marimo_interface():
    """Render Marimo notebook interface"""
    st.markdown("### 📓 Marimo Notebooks")
    
    # Current task notebook
    if 'current_task' in st.session_state:
        task = st.session_state.current_task
        
        st.markdown(f"#### Current Task: {task['name']}")
        st.markdown(f"**Type:** {task['type']} | **Plan:** {task['plan']}")
        
        # Notebook status
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Notebook Status", "Ready")
        with col2:
            st.metric("Cells", "8")
        with col3:
            st.metric("Execution Time", "~3 min")
        
        # Mock notebook preview
        st.markdown("#### 📝 Notebook Preview")
        
        notebook_cells = [
            {"title": "Import Libraries", "content": "import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt", "status": "ready"},
            {"title": "Load Data", "content": "df = pd.read_csv('data.csv')\nprint(f'Loaded {len(df)} rows')", "status": "ready"},
            {"title": "Data Preprocessing", "content": "# Handle missing values\ndf = df.dropna()\n# Convert dates\ndf['date'] = pd.to_datetime(df['date'])", "status": "ready"},
            {"title": "Analysis", "content": f"# {task['type']} analysis code would be here", "status": "ready"},
            {"title": "Visualization", "content": "# Create plots and charts", "status": "ready"},
            {"title": "Results", "content": "# Export results and insights", "status": "ready"}
        ]
        
        for i, cell in enumerate(notebook_cells):
            with st.expander(f"Cell {i+1}: {cell['title']}"):
                st.code(cell['content'], language='python')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.button(f"▶️ Run", key=f"run_cell_{i}")
                with col2:
                    st.button(f"✏️ Edit", key=f"edit_cell_{i}")
                with col3:
                    st.write(f"Status: {cell['status']}")
        
        # Notebook actions
        st.markdown("#### Notebook Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("▶️ Run All Cells"):
                st.success("Running all cells... (This would execute the actual notebook)")
        
        with col2:
            if st.button("💾 Save Results"):
                st.success("Results saved!")
        
        with col3:
            if st.button("📊 Generate Report"):
                st.success("Report generated!")
        
        with col4:
            if st.button("✅ Submit Task"):
                st.success("Task submitted for review!")
    
    else:
        st.info("No active task selected. Go to 'My Tasks' to select a task with a notebook.")
        
        # Available notebook templates
        st.markdown("### 📚 Available Notebook Templates")
        
        templates = [
            {"name": "Data Profiling", "description": "Complete data quality assessment", "cells": 6},
            {"name": "Statistical Analysis", "description": "Descriptive statistics and hypothesis testing", "cells": 8},
            {"name": "Time Series", "description": "Trend analysis and forecasting", "cells": 10},
            {"name": "Machine Learning", "description": "Model training and evaluation", "cells": 12},
            {"name": "Visualization", "description": "Charts and dashboards", "cells": 7},
            {"name": "Custom Analysis", "description": "Blank template for custom work", "cells": 4}
        ]
        
        for template in templates:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
                with col1:
                    st.markdown(f"**{template['name']}**")
                with col2:
                    st.markdown(template['description'])
                with col3:
                    st.markdown(f"{template['cells']} cells")
                with col4:
                    st.button("Create", key=f"create_{template['name']}")

def render_collaboration():
    """Render collaboration interface"""
    st.markdown("### 💬 Collaboration")
    
    # Team chat
    st.markdown("#### Team Chat")
    
    # Mock chat messages
    messages = [
        {"user": "Alex Analyst", "time": "10:30 AM", "message": "I'm seeing some interesting patterns in the Q4 sales data"},
        {"user": "Jordan Associate", "time": "10:32 AM", "message": "Can you share the preliminary charts?"},
        {"user": "Sarah Manager", "time": "10:35 AM", "message": "Great work team! Let's discuss the findings in our 2 PM meeting"},
        {"user": "Alex Analyst", "time": "10:38 AM", "message": "I'll have the full analysis ready by then"}
    ]
    
    # Chat display
    for msg in messages:
        st.markdown(f"**{msg['user']}** _{msg['time']}_")
        st.markdown(f"> {msg['message']}")
        st.markdown("---")
    
    # New message input
    new_message = st.text_area("Type your message...")
    if st.button("Send Message"):
        if new_message:
            st.success("Message sent!")
        else:
            st.error("Please enter a message")
    
    # Active collaborations
    st.markdown("#### 🤝 Active Collaborations")
    
    collabs = [
        {"project": "Q4 Sales Analysis", "collaborators": ["Alex Analyst", "Jordan Associate"], "status": "Active"},
        {"project": "Customer Segmentation", "collaborators": ["Alex Analyst", "Sam Senior"], "status": "Planning"},
        {"project": "Revenue Forecast", "collaborators": ["Jordan Associate", "Riley Research"], "status": "Review"}
    ]
    
    for collab in collabs:
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{collab['project']}**")
            with col2:
                st.markdown(f"Collaborators: {', '.join(collab['collaborators'])}")
            with col3:
                st.markdown(f"Status: {collab['status']}")

def render_submissions():
    """Render submissions interface"""
    st.markdown("### 📤 My Submissions")
    
    # Submission history
    submissions = [
        {
            "task": "Time Series Analysis - Q4 Sales",
            "submitted": "2024-12-30 14:30",
            "status": "Under Review",
            "reviewer": "Sarah Manager",
            "confidence": 85,
            "feedback": None
        },
        {
            "task": "Customer Segmentation - Demographics",
            "submitted": "2024-12-29 16:45",
            "status": "Approved",
            "reviewer": "Sam Senior",
            "confidence": 92,
            "feedback": "Excellent analysis with clear insights"
        },
        {
            "task": "Data Quality Assessment",
            "submitted": "2024-12-28 11:20",
            "status": "Needs Revision",
            "reviewer": "Sarah Manager",
            "confidence": 70,
            "feedback": "Please include additional validation checks"
        }
    ]
    
    for sub in submissions:
        status_colors = {
            "Under Review": "🟡",
            "Approved": "🟢", 
            "Needs Revision": "🔴",
            "Draft": "⚪"
        }
        
        with st.container():
            # Submission header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"#### {sub['task']}")
            with col2:
                st.markdown(f"{status_colors.get(sub['status'], '⚪')} **{sub['status']}**")
            
            # Submission details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"📅 **Submitted:** {sub['submitted']}")
            with col2:
                st.markdown(f"👤 **Reviewer:** {sub['reviewer']}")
            with col3:
                st.markdown(f"📊 **Confidence:** {sub['confidence']}%")
            
            # Feedback
            if sub['feedback']:
                st.markdown(f"💬 **Feedback:** {sub['feedback']}")
            
            # Actions
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button("👁️ View Details", key=f"view_{sub['task']}")
            with col2:
                if sub['status'] == "Needs Revision":
                    st.button("✏️ Revise", key=f"revise_{sub['task']}")
                else:
                    st.button("📊 View Results", key=f"results_{sub['task']}")
            with col3:
                st.button("💬 Message Reviewer", key=f"message_{sub['task']}")
            
            st.markdown("---")

def render_associate_portal():
    """Render associate portal (simplified interface)"""
    st.markdown(f'<div class="main-header"><h1>🎯 Associate Portal</h1><span class="role-badge">Associate</span></div>', unsafe_allow_html=True)
    
    # Simplified navigation
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.radio("Select Page", [
            "My Tasks",
            "Notebooks",
            "Help & Training"
        ])
    
    if page == "My Tasks":
        render_associate_tasks()
    elif page == "Notebooks":
        render_associate_notebooks()
    elif page == "Help & Training":
        render_help_training()

def render_associate_tasks():
    """Render associate tasks (simplified)"""
    st.markdown("### 📋 My Assigned Tasks")
    
    # Simplified task list
    tasks = [
        {
            "name": "Data Quality Check - Sales Data",
            "description": "Check the uploaded sales data for missing values, duplicates, and outliers",
            "status": "Ready to Start",
            "estimated_time": "2 hours",
            "notebook_available": True,
            "instructions": "Use the auto-generated notebook to perform quality checks"
        },
        {
            "name": "Basic Visualization - Revenue Trends",
            "description": "Create charts showing revenue trends over the past quarter",
            "status": "In Progress", 
            "estimated_time": "3 hours",
            "notebook_available": True,
            "instructions": "Follow the notebook cells to generate required charts"
        }
    ]
    
    for task in tasks:
        with st.container():
            # Task card
            st.markdown(f"""
            <div class="task-card {'in-progress' if task['status'] == 'In Progress' else 'approval-needed'}">
                <h4>{task['name']}</h4>
                <p>{task['description']}</p>
                <p><strong>Status:</strong> {task['status']} | <strong>Estimated Time:</strong> {task['estimated_time']}</p>
                <p><strong>Instructions:</strong> {task['instructions']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Simple action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📓 Open Notebook", key=f"notebook_{task['name']}", 
                           disabled=not task['notebook_available']):
                    st.success("Opening your personalized notebook...")
            
            with col2:
                if st.button("❓ Get Help", key=f"help_{task['name']}"):
                    st.info("Help documentation and tutorials available in Help & Training")
            
            with col3:
                if task['status'] == "In Progress":
                    if st.button("✅ Submit Work", key=f"submit_{task['name']}"):
                        st.success("Work submitted for review!")
                else:
                    if st.button("▶️ Start Task", key=f"start_{task['name']}"):
                        st.success("Task started! Notebook is ready.")

def render_associate_notebooks():
    """Render associate notebooks (simplified)"""
    st.markdown("### 📓 My Notebooks")
    
    st.info("""
    **For Associates:** Your notebooks are pre-configured with all the code you need. 
    Simply follow the instructions in each cell and run them in order.
    """)
    
    # Available notebooks
    notebooks = [
        {
            "name": "Data Quality Assessment",
            "task": "Data Quality Check - Sales Data", 
            "status": "Ready",
            "cells": 5,
            "description": "Step-by-step data quality checks"
        },
        {
            "name": "Basic Charts and Graphs",
            "task": "Basic Visualization - Revenue Trends",
            "status": "In Progress",
            "cells": 6,
            "description": "Generate charts with pre-written code"
        }
    ]
    
    for nb in notebooks:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            
            with col1:
                st.markdown(f"**{nb['name']}**")
                st.markdown(f"*{nb['description']}*")
            
            with col2:
                st.markdown(f"Task: {nb['task']}")
            
            with col3:
                st.markdown(f"Status: {nb['status']}")
                st.markdown(f"Cells: {nb['cells']}")
            
            with col4:
                if st.button("Open", key=f"open_{nb['name']}"):
                    st.success("Opening simplified notebook interface...")

def render_help_training():
    """Render help and training materials"""
    st.markdown("### 📚 Help & Training")
    
    # Training modules
    st.markdown("#### 🎓 Training Modules")
    
    modules = [
        {"title": "Getting Started", "duration": "15 min", "status": "completed"},
        {"title": "Using Marimo Notebooks", "duration": "20 min", "status": "completed"},
        {"title": "Data Quality Basics", "duration": "25 min", "status": "in_progress"}, 
        {"title": "Creating Charts", "duration": "30 min", "status": "not_started"},
        {"title": "Submitting Your Work", "duration": "10 min", "status": "not_started"}
    ]
    
    for module in modules:
        status_icons = {"completed": "✅", "in_progress": "⏳", "not_started": "⭕"}
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"{status_icons[module['status']]} {module['title']}")
        with col2:
            st.markdown(module['duration'])
        with col3:
            st.markdown(module['status'].replace('_', ' ').title())
        with col4:
            if module['status'] != "completed":
                st.button("Start", key=f"start_{module['title']}")
            else:
                st.button("Review", key=f"review_{module['title']}")
    
    # Quick help
    st.markdown("#### ❓ Quick Help")
    
    with st.expander("How do I start a task?"):
        st.markdown("""
        1. Go to 'My Tasks' 
        2. Click 'Start Task' on any ready task
        3. Open the associated notebook
        4. Follow the instructions in each cell
        """)
    
    with st.expander("How do I use the notebooks?"):
        st.markdown("""
        1. Click 'Open Notebook' for your task
        2. Read the instructions in each cell
        3. Click 'Run' to execute the code
        4. Review the results
        5. Move to the next cell
        """)
    
    with st.expander("What if I get stuck?"):
        st.markdown("""
        1. Check the training modules above
        2. Use the 'Get Help' button on your task
        3. Ask in the team chat
        4. Contact your supervisor
        """)
    
    # Contact information
    st.markdown("#### 📞 Support Contacts")
    st.markdown("""
    - **Technical Issues:** tech-support@company.com
    - **Training Questions:** training@company.com  
    - **Your Supervisor:** supervisor@company.com
    """)

def main():
    """Main application logic"""
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Render appropriate interface based on user role
    user_role = st.session_state.user_role
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Logout"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # User info
        user_info = st.session_state.user_info
        st.markdown(f"**Logged in as:**")
        st.markdown(f"{user_info['name']}")
        st.markdown(f"*{user_role.replace('_', ' ').title()}*")
    
    # Route to appropriate dashboard
    if user_role == 'manager':
        render_manager_dashboard()
    elif user_role in ['senior_analyst', 'analyst']:
        render_analyst_workspace()
    elif user_role == 'associate':
        render_associate_portal()
    else:
        st.error(f"Unknown user role: {user_role}")

if __name__ == "__main__":
    main()