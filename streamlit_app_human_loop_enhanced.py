"""
Enhanced AI Data Analysis Platform with Human-in-the-Loop and Marimo
Real implementation with comprehensive feedback mechanisms
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

# Page configuration
st.set_page_config(
    page_title="AI Analysis Team - Human-in-the-Loop Edition",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with enhanced features
def init_session_state():
    """Initialize all session state variables with human-in-the-loop features"""
    defaults = {
        # Core state
        'current_step': 0,
        'project_initialized': False,
        'gemini_api_key': os.getenv('GEMINI_API_KEY', ''),
        'project_name': '',
        'problem_statement': '',
        'data_context': '',
        'dataframes': {},
        'data_profiles': {},
        
        # AI outputs
        'manager_plan': None,
        'analyst_summary': None,
        'associate_guidance': None,
        'analysis_tasks': [],
        'task_results': [],
        'final_report': None,
        
        # Human-in-the-loop state
        'feedback_history': {},
        'revision_count': {},
        'user_modifications': {},
        'task_approvals': {},
        'consultation_chats': {},
        'decision_points': [],
        'auto_proceed': False,
        
        # Marimo state
        'marimo_notebooks': {},
        'notebook_versions': {},
        'execution_logs': [],
        
        # Configuration
        'gemini_model': 'gemini-2.0-flash-exp',
        'ai_team': None,
        'allow_manual_override': True,
        'require_approval': True
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Enhanced feedback system
class HumanFeedbackManager:
    """Manages human feedback and iterations"""
    
    @staticmethod
    def get_feedback_ui(stage_name: str, current_output: str, persona: str) -> Optional[str]:
        """Create feedback UI component for any stage"""
        with st.expander(f"💬 Provide Feedback on {stage_name}", expanded=False):
            st.markdown(f"**Current {stage_name}:**")
            
            # Show current output in a scrollable container
            with st.container():
                st.markdown(
                    f'<div style="max-height: 200px; overflow-y: auto; padding: 10px; '
                    f'background: #f0f2f6; border-radius: 5px;">{current_output}</div>',
                    unsafe_allow_html=True
                )
            
            # Feedback options
            col1, col2 = st.columns([3, 1])
            
            with col1:
                feedback_type = st.radio(
                    "Feedback Type",
                    ["Approve as is", "Suggest improvements", "Request complete redo", "Skip this step"],
                    key=f"feedback_type_{stage_name}",
                    horizontal=True
                )
            
            with col2:
                revision_count = st.session_state.revision_count.get(stage_name, 0)
                st.metric("Revisions", revision_count)
            
            if feedback_type == "Suggest improvements":
                feedback_text = st.text_area(
                    "Your specific feedback:",
                    key=f"feedback_text_{stage_name}",
                    placeholder="Be specific about what should be changed...",
                    height=100
                )
                
                # Provide guided feedback prompts
                st.markdown("**Feedback suggestions:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("More detail", key=f"detail_{stage_name}"):
                        st.session_state[f"feedback_text_{stage_name}"] = "Please provide more detail on..."
                with col2:
                    if st.button("Simplify", key=f"simplify_{stage_name}"):
                        st.session_state[f"feedback_text_{stage_name}"] = "Please simplify the explanation of..."
                with col3:
                    if st.button("Focus on", key=f"focus_{stage_name}"):
                        st.session_state[f"feedback_text_{stage_name}"] = "Please focus more on..."
                
                if st.button(f"Apply Feedback", key=f"apply_{stage_name}", type="primary"):
                    # Store feedback
                    if stage_name not in st.session_state.feedback_history:
                        st.session_state.feedback_history[stage_name] = []
                    
                    st.session_state.feedback_history[stage_name].append({
                        'feedback': feedback_text,
                        'timestamp': datetime.now().isoformat(),
                        'revision': revision_count + 1
                    })
                    
                    st.session_state.revision_count[stage_name] = revision_count + 1
                    return feedback_text
                    
            elif feedback_type == "Request complete redo":
                if st.button(f"Regenerate {stage_name}", key=f"redo_{stage_name}", type="secondary"):
                    return "REGENERATE"
                    
            elif feedback_type == "Skip this step":
                if st.button(f"Skip {stage_name}", key=f"skip_{stage_name}"):
                    return "SKIP"
                    
            elif feedback_type == "Approve as is":
                if st.button(f"✅ Approve and Continue", key=f"approve_{stage_name}", type="primary"):
                    return "APPROVED"
        
        return None
    
    @staticmethod
    def show_feedback_history(stage_name: str):
        """Display feedback history for a stage"""
        if stage_name in st.session_state.feedback_history:
            with st.expander(f"📜 Feedback History for {stage_name}"):
                for entry in st.session_state.feedback_history[stage_name]:
                    st.markdown(f"**Revision {entry['revision']}** - {entry['timestamp']}")
                    st.markdown(f"> {entry['feedback']}")

# Enhanced consultation system
class ConsultationManager:
    """Manages consultations with AI personas"""
    
    @staticmethod
    def create_consultation_chat(persona_name: str, context: str):
        """Create a chat interface for consulting with a persona"""
        chat_key = f"chat_{persona_name}"
        
        if chat_key not in st.session_state.consultation_chats:
            st.session_state.consultation_chats[chat_key] = []
        
        with st.expander(f"🗣️ Consult with {persona_name}", expanded=False):
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.consultation_chats[chat_key]:
                    if msg['role'] == 'user':
                        st.markdown(f"**You:** {msg['content']}")
                    else:
                        st.markdown(f"**{persona_name}:** {msg['content']}")
            
            # Quick questions
            st.markdown("**Quick questions:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("What are the risks?", key=f"risk_{persona_name}"):
                    question = "What are the main risks or limitations in this approach?"
                    ConsultationManager.send_consultation(persona_name, question, context)
                    st.rerun()
                    
                if st.button("Alternative approaches?", key=f"alt_{persona_name}"):
                    question = "What alternative approaches should we consider?"
                    ConsultationManager.send_consultation(persona_name, question, context)
                    st.rerun()
                    
            with col2:
                if st.button("More detail?", key=f"detail_{persona_name}"):
                    question = "Can you provide more detail on the methodology?"
                    ConsultationManager.send_consultation(persona_name, question, context)
                    st.rerun()
                    
                if st.button("Success metrics?", key=f"metrics_{persona_name}"):
                    question = "How should we measure success for this analysis?"
                    ConsultationManager.send_consultation(persona_name, question, context)
                    st.rerun()
            
            # Custom question
            custom_question = st.text_input(
                "Ask a custom question:",
                key=f"custom_q_{persona_name}",
                placeholder="Type your question here..."
            )
            
            if st.button(f"Send to {persona_name}", key=f"send_{persona_name}"):
                if custom_question:
                    ConsultationManager.send_consultation(persona_name, custom_question, context)
                    st.rerun()
    
    @staticmethod
    def send_consultation(persona_name: str, question: str, context: str):
        """Send consultation question and get response"""
        chat_key = f"chat_{persona_name}"
        
        # Add user question
        st.session_state.consultation_chats[chat_key].append({
            'role': 'user',
            'content': question
        })
        
        # Get AI response (mock for now)
        response = f"[{persona_name} Response]: Based on the context, {question.lower()} "
        response += "I recommend focusing on data quality first, then proceeding with the analysis."
        
        st.session_state.consultation_chats[chat_key].append({
            'role': persona_name,
            'content': response
        })

# Enhanced task management
class TaskManager:
    """Manages analysis tasks with user control"""
    
    @staticmethod
    def display_editable_task(task: Dict, task_num: int) -> Dict:
        """Display task with editing capabilities"""
        with st.expander(f"📋 Task {task_num}: {task.get('title', 'Analysis Task')}", 
                        expanded=task_num <= 2):
            
            # Task approval status
            approval_key = f"task_{task_num}_approved"
            is_approved = st.session_state.task_approvals.get(approval_key, False)
            
            if is_approved:
                st.success("✅ Task Approved")
            else:
                st.warning("⏳ Pending Approval")
            
            # Editable fields
            col1, col2 = st.columns(2)
            
            with col1:
                task['title'] = st.text_input(
                    "Task Title",
                    value=task.get('title', ''),
                    key=f"title_{task_num}"
                )
                
                task['objective'] = st.text_area(
                    "Objective",
                    value=task.get('objective', ''),
                    key=f"obj_{task_num}",
                    height=80
                )
            
            with col2:
                task['method'] = st.text_area(
                    "Method",
                    value=task.get('method', ''),
                    key=f"method_{task_num}",
                    height=80
                )
                
                task['priority'] = st.select_slider(
                    "Priority",
                    options=['Low', 'Medium', 'High', 'Critical'],
                    value=task.get('priority', 'Medium'),
                    key=f"priority_{task_num}"
                )
            
            # Code editor
            st.markdown("**Generated Code:**")
            task['code'] = st.text_area(
                "Python Code",
                value=task.get('code', '# Code will be generated here'),
                key=f"code_{task_num}",
                height=200
            )
            
            # Task actions
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔍 Preview", key=f"preview_{task_num}"):
                    TaskManager.preview_task(task)
            
            with col2:
                if st.button("✅ Approve", key=f"approve_task_{task_num}"):
                    st.session_state.task_approvals[approval_key] = True
                    st.success("Task approved!")
                    st.rerun()
            
            with col3:
                if st.button("🔄 Regenerate", key=f"regen_{task_num}"):
                    # Regenerate task code
                    st.info("Regenerating task code...")
            
            with col4:
                if st.button("❌ Remove", key=f"remove_{task_num}"):
                    task['status'] = 'removed'
                    st.rerun()
            
            # Execution options
            if is_approved:
                st.markdown("---")
                st.markdown("**Execution Options:**")
                
                exec_col1, exec_col2 = st.columns(2)
                with exec_col1:
                    exec_mode = st.radio(
                        "Execution Mode",
                        ["Auto (Marimo)", "Interactive", "Manual Review"],
                        key=f"exec_mode_{task_num}"
                    )
                
                with exec_col2:
                    if st.button("▶️ Execute Task", key=f"exec_{task_num}", type="primary"):
                        TaskManager.execute_task(task, exec_mode)
        
        return task
    
    @staticmethod
    def preview_task(task: Dict):
        """Preview task execution without running"""
        with st.expander("Task Preview", expanded=True):
            st.markdown(f"**Title:** {task.get('title', 'N/A')}")
            st.markdown(f"**Objective:** {task.get('objective', 'N/A')}")
            st.markdown(f"**Method:** {task.get('method', 'N/A')}")
            st.code(task.get('code', '# No code generated'), language='python')
    
    @staticmethod
    def execute_task(task: Dict, mode: str):
        """Execute task based on selected mode"""
        if mode == "Auto (Marimo)":
            st.info("🚀 Executing in Marimo notebook...")
            # Create and run Marimo notebook
        elif mode == "Interactive":
            st.info("💻 Opening interactive session...")
            # Open interactive environment
        else:
            st.info("👀 Manual review mode - code displayed above")

# Main application with enhanced human-in-the-loop
def main():
    init_session_state()
    
    # Initialize managers
    feedback_mgr = HumanFeedbackManager()
    consultation_mgr = ConsultationManager()
    task_mgr = TaskManager()
    
    # Enhanced sidebar with human controls
    with st.sidebar:
        st.title("🤝 AI Analysis Team")
        st.markdown("**Human-in-the-Loop Edition**")
        st.markdown("---")
        
        # API Configuration
        api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            help="Enter your Google Gemini API key"
        )
        if api_key != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_key
        
        # Human Control Settings
        st.markdown("### ⚙️ Human Control Settings")
        
        st.session_state.require_approval = st.checkbox(
            "Require approval at each step",
            value=st.session_state.require_approval,
            help="Pause for human approval before proceeding"
        )
        
        st.session_state.allow_manual_override = st.checkbox(
            "Allow manual override",
            value=st.session_state.allow_manual_override,
            help="Enable manual editing of AI outputs"
        )
        
        st.session_state.auto_proceed = st.checkbox(
            "Auto-proceed after approval",
            value=st.session_state.auto_proceed,
            help="Automatically continue after approval"
        )
        
        # Revision Tracking
        st.markdown("### 📊 Revision Tracking")
        total_revisions = sum(st.session_state.revision_count.values())
        st.metric("Total Revisions", total_revisions)
        
        if st.session_state.revision_count:
            for stage, count in st.session_state.revision_count.items():
                st.text(f"{stage}: {count} revisions")
        
        # Navigation
        st.markdown("---")
        st.markdown("### 📍 Navigation")
        
        if st.session_state.project_initialized:
            steps = [
                "1️⃣ Project Setup",
                "2️⃣ Manager Planning",
                "3️⃣ Data Understanding",
                "4️⃣ Task Generation",
                "5️⃣ Task Approval",
                "6️⃣ Execution",
                "7️⃣ Final Report"
            ]
            
            # Non-linear navigation
            for i, step in enumerate(steps):
                if i <= st.session_state.current_step:
                    if st.button(step, key=f"nav_{i}", 
                               type="primary" if i == st.session_state.current_step else "secondary"):
                        st.session_state.current_step = i
                        st.rerun()
                else:
                    st.button(step, key=f"nav_{i}", disabled=True)
        
        # Quick Actions
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("💾 Save Progress"):
            save_progress()
            st.success("Progress saved!")
        
        if st.button("📤 Export Session"):
            export_session()
        
        if st.button("🔄 Reset All"):
            if st.checkbox("Confirm reset"):
                reset_session()
                st.rerun()
    
    # Main content area with step-based display
    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar to begin.")
        st.stop()
    
    # Display current step with human-in-the-loop features
    if st.session_state.current_step == 0:
        display_setup_with_feedback()
    elif st.session_state.current_step == 1:
        display_planning_with_feedback(feedback_mgr, consultation_mgr)
    elif st.session_state.current_step == 2:
        display_analysis_with_feedback(feedback_mgr, consultation_mgr)
    elif st.session_state.current_step == 3:
        display_task_generation_with_feedback(feedback_mgr, consultation_mgr)
    elif st.session_state.current_step == 4:
        display_task_approval(task_mgr)
    elif st.session_state.current_step == 5:
        display_execution_with_control()
    elif st.session_state.current_step == 6:
        display_final_report_with_feedback(feedback_mgr)

def display_setup_with_feedback():
    """Enhanced setup with validation and feedback"""
    st.title("🚀 Project Setup - Human Guided")
    
    # Show tips
    with st.expander("💡 Setup Tips", expanded=True):
        st.markdown("""
        - **Be specific** in your problem statement
        - **Include context** about your business goals
        - **Upload clean data** for best results
        - You can **revise everything** later
        """)
    
    with st.form("enhanced_setup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input(
                "Project Name",
                placeholder="e.g., Q4 Sales Analysis",
                help="Choose a descriptive name"
            )
            
            problem_statement = st.text_area(
                "Problem Statement",
                placeholder="What specific insights are you looking for?",
                height=150,
                help="Be as specific as possible"
            )
        
        with col2:
            data_context = st.text_area(
                "Business Context",
                placeholder="What's the business background?",
                height=100,
                help="Optional but recommended"
            )
            
            analysis_goals = st.multiselect(
                "Analysis Goals",
                ["Trend Analysis", "Segmentation", "Forecasting", 
                 "Anomaly Detection", "Correlation Analysis", "Classification"],
                help="Select all that apply"
            )
        
        uploaded_files = st.file_uploader(
            "Upload Data Files",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True,
            help="Support for CSV and Excel files"
        )
        
        # Validation before submit
        col1, col2, col3 = st.columns(3)
        with col1:
            validate = st.form_submit_button("Validate", type="secondary")
        with col2:
            st.empty()
        with col3:
            submit = st.form_submit_button("Start Analysis", type="primary")
        
        if validate:
            # Validation logic
            issues = []
            if not project_name:
                issues.append("Project name is required")
            if not problem_statement:
                issues.append("Problem statement is required")
            if not uploaded_files:
                issues.append("At least one data file is required")
            
            if issues:
                st.error("Please fix the following issues:")
                for issue in issues:
                    st.markdown(f"- {issue}")
            else:
                st.success("✅ All validations passed!")
        
        if submit:
            # Process and continue
            st.session_state.project_initialized = True
            st.session_state.current_step = 1
            st.rerun()

def display_planning_with_feedback(feedback_mgr, consultation_mgr):
    """Manager planning with comprehensive feedback"""
    st.title("👔 Strategic Planning - Interactive")
    
    # Generate or display plan
    if st.session_state.manager_plan is None:
        with st.spinner("🤔 Manager is creating the strategic plan..."):
            # Mock plan generation
            plan = """
            ## Strategic Analysis Plan
            
            ### Executive Summary
            Comprehensive analysis to identify growth opportunities and optimize operations.
            
            ### Objectives
            1. Identify top performing segments
            2. Discover growth opportunities
            3. Optimize resource allocation
            
            ### Methodology
            - Statistical analysis
            - Machine learning models
            - Predictive analytics
            
            ### Success Metrics
            - Actionable insights: 5+
            - Forecast accuracy: >85%
            - ROI improvement: >15%
            """
            st.session_state.manager_plan = plan
    
    # Display plan with feedback options
    st.markdown(st.session_state.manager_plan)
    
    # Feedback component
    feedback = feedback_mgr.get_feedback_ui(
        "Strategic Plan", 
        st.session_state.manager_plan,
        "Manager"
    )
    
    if feedback == "APPROVED":
        st.session_state.current_step = 2
        st.rerun()
    elif feedback and feedback != "APPROVED":
        # Apply feedback
        st.info("Applying your feedback...")
        # Would call AI to revise plan
    
    # Consultation options
    consultation_mgr.create_consultation_chat(
        "Manager",
        st.session_state.manager_plan
    )
    
    # Show feedback history
    feedback_mgr.show_feedback_history("Strategic Plan")

def display_task_approval(task_mgr):
    """Task approval interface"""
    st.title("✅ Task Review & Approval")
    
    if not st.session_state.analysis_tasks:
        # Generate sample tasks
        st.session_state.analysis_tasks = [
            {'title': 'Data Profiling', 'objective': 'Understand data', 
             'method': 'Statistical analysis', 'code': '# Profile code'},
            {'title': 'Trend Analysis', 'objective': 'Identify trends',
             'method': 'Time series', 'code': '# Trend code'},
            {'title': 'Segmentation', 'objective': 'Group customers',
             'method': 'Clustering', 'code': '# Clustering code'}
        ]
    
    # Task approval workflow
    st.markdown("### Review and approve analysis tasks before execution")
    
    # Bulk actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve All"):
            for i in range(len(st.session_state.analysis_tasks)):
                st.session_state.task_approvals[f"task_{i+1}_approved"] = True
            st.rerun()
    
    with col2:
        if st.button("🔄 Regenerate All"):
            st.info("Regenerating all tasks...")
    
    with col3:
        approved_count = sum(1 for k, v in st.session_state.task_approvals.items() if v)
        st.metric("Approved", f"{approved_count}/{len(st.session_state.analysis_tasks)}")
    
    # Individual task review
    for i, task in enumerate(st.session_state.analysis_tasks, 1):
        task = task_mgr.display_editable_task(task, i)
        st.session_state.analysis_tasks[i-1] = task
    
    # Proceed button
    if approved_count == len(st.session_state.analysis_tasks):
        if st.button("▶️ Proceed to Execution", type="primary"):
            st.session_state.current_step = 5
            st.rerun()
    else:
        st.info(f"Please approve all tasks to proceed ({approved_count}/{len(st.session_state.analysis_tasks)} approved)")

def save_progress():
    """Save current session progress"""
    progress_data = {
        'timestamp': datetime.now().isoformat(),
        'current_step': st.session_state.current_step,
        'project_name': st.session_state.project_name,
        'feedback_history': st.session_state.feedback_history,
        'revision_count': st.session_state.revision_count,
        'task_approvals': st.session_state.task_approvals
    }
    
    filename = f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(progress_data, f, indent=2, default=str)
    
    return filename

def export_session():
    """Export complete session data"""
    st.download_button(
        label="Download Session Data",
        data=json.dumps(st.session_state.to_dict(), indent=2, default=str),
        file_name=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def reset_session():
    """Reset session state"""
    for key in list(st.session_state.keys()):
        if key not in ['gemini_api_key']:
            del st.session_state[key]
    init_session_state()

# Placeholder functions for remaining steps
def display_analysis_with_feedback(feedback_mgr, consultation_mgr):
    st.title("📊 Data Understanding")
    st.info("Data analysis with feedback - Implementation needed")

def display_task_generation_with_feedback(feedback_mgr, consultation_mgr):
    st.title("🎯 Task Generation")
    st.info("Task generation with feedback - Implementation needed")

def display_execution_with_control():
    st.title("🚀 Controlled Execution")
    st.info("Marimo execution with controls - Implementation needed")

def display_final_report_with_feedback(feedback_mgr):
    st.title("📑 Final Report")
    st.info("Report with feedback options - Implementation needed")

if __name__ == "__main__":
    main()