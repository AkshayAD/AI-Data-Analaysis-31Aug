"""
AI Data Analysis Platform - Fully Automated Version
Simplified interface with automatic execution and no unnecessary options
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
    page_title="AI Data Analysis Platform - Automated",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_view = 'overview'
        st.session_state.workflow_manager = WorkflowManager()
        st.session_state.task_executor = TaskExecutor()
        st.session_state.report_generator = ReportGenerator()
        st.session_state.active_plans = {}
        st.session_state.task_results = {}
        st.session_state.uploaded_data = {}
        st.session_state.plan_reports = {}
        st.session_state.execution_logs = []

init_session_state()

# Helper Functions (defined before usage)
def execute_tasks_automatically(plan_id, tasks, data):
    """Execute tasks automatically after plan creation"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    successful_tasks = 0
    failed_tasks = 0
    
    for i, task in enumerate(tasks):
        status_text.text(f"🔄 Executing: {task['name']}...")
        progress_bar.progress((i + 1) / len(tasks))
        
        try:
            # Execute task
            result = st.session_state.task_executor.execute_task(task, data)
            st.session_state.task_results[task['id']] = result
            
            # Log execution
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'task': task['name'],
                'status': result.get('status', 'unknown'),
                'execution_time': result.get('execution_time', 'N/A')
            }
            st.session_state.execution_logs.append(log_entry)
            
            if result.get('status') == 'success':
                successful_tasks += 1
                with results_container:
                    st.success(f"✅ {task['name']} - Completed in {result.get('execution_time', 'N/A')}")
            else:
                failed_tasks += 1
                with results_container:
                    st.warning(f"⚠️ {task['name']} - Failed")
        
        except Exception as e:
            failed_tasks += 1
            with results_container:
                st.error(f"❌ {task['name']} - Error: {str(e)}")
            
        time.sleep(0.2)  # Brief pause for UI update
    
    status_text.text("✅ Execution completed!")
    progress_bar.progress(1.0)
    
    # Summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ Successful", successful_tasks)
    with col2:
        st.metric("❌ Failed", failed_tasks)
    with col3:
        success_rate = (successful_tasks / len(tasks) * 100) if tasks else 0
        st.metric("📊 Success Rate", f"{success_rate:.0f}%")
    
    return successful_tasks, failed_tasks

def generate_plan_report(plan_id):
    """Generate comprehensive report for a plan"""
    plan = st.session_state.active_plans.get(plan_id)
    if not plan:
        st.error("Plan not found")
        return None
    
    # Get task results
    plan_task_ids = [task['id'] for task in plan.get('tasks', [])]
    plan_task_results = [st.session_state.task_results.get(tid) 
                         for tid in plan_task_ids 
                         if tid in st.session_state.task_results]
    
    if not plan_task_results:
        st.warning("No completed tasks found. Execute tasks first.")
        return None
    
    try:
        # Aggregate results
        aggregated = st.session_state.report_generator.aggregate_plan_results(plan, plan_task_results)
        
        # Generate report
        report = st.session_state.report_generator.generate_executive_report(aggregated)
        
        # Store report
        st.session_state.plan_reports[plan_id] = report
        
        return report
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return None

# Custom CSS
st.markdown("""
<style>
    .automated-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    .step-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-box {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<div class="automated-header">🤖 AI Data Analysis Platform - Fully Automated</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Quick Navigation")
    
    view_options = {
        'overview': '🏠 Home',
        'analyze': '🚀 Start Analysis',
        'results': '📊 View Results',
        'reports': '📄 Reports'
    }
    
    selected_view = st.selectbox(
        "Select Page",
        options=list(view_options.keys()),
        format_func=lambda x: view_options[x],
        key='view_selector'
    )
    
    st.session_state.current_view = selected_view
    
    # Quick stats
    st.markdown("---")
    st.markdown("### 📈 Platform Stats")
    st.metric("Active Analyses", len(st.session_state.active_plans))
    st.metric("Completed Tasks", len(st.session_state.task_results))
    st.metric("Reports Generated", len(st.session_state.plan_reports))
    
    # Recent logs
    if st.session_state.execution_logs:
        st.markdown("---")
        st.markdown("### 📝 Recent Activity")
        for log in st.session_state.execution_logs[-3:]:
            if log['status'] == 'success':
                st.success(f"✅ {log['task'][:20]}...")
            else:
                st.warning(f"⚠️ {log['task'][:20]}...")

# Main content based on view
if st.session_state.current_view == 'overview':
    st.markdown("## 🏠 Welcome to Automated Data Analysis")
    
    st.markdown("""
    ### 🎯 How It Works
    This platform provides **fully automated data analysis** with just a few clicks:
    """)
    
    # Process steps
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="step-card">
            <h3>1️⃣ Upload Data</h3>
            <p>Upload your CSV/Excel file or use sample data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-card">
            <h3>2️⃣ Define Goals</h3>
            <p>Tell us what you want to analyze</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="step-card">
            <h3>3️⃣ Get Results</h3>
            <p>AI analyzes and generates reports automatically</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start New Analysis", use_container_width=True, type="primary"):
            st.session_state.current_view = 'analyze'
            st.rerun()
    
    # Platform capabilities
    st.markdown("### 🛠️ Platform Capabilities")
    
    capabilities = {
        "🔍 Data Profiling": "Automatic data quality assessment and statistics",
        "📊 Statistical Analysis": "Comprehensive statistical testing and correlations",
        "🔮 Predictive Modeling": "ML-powered predictions and forecasting",
        "🎯 Anomaly Detection": "Identify outliers and unusual patterns",
        "📈 Smart Visualizations": "Auto-generated charts and graphs",
        "📄 Executive Reports": "Professional reports with insights and recommendations"
    }
    
    col1, col2 = st.columns(2)
    for i, (capability, description) in enumerate(capabilities.items()):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"**{capability}**")
            st.caption(description)

elif st.session_state.current_view == 'analyze':
    st.markdown("## 🚀 Start Automated Analysis")
    
    with st.form("analysis_form", clear_on_submit=False):
        st.markdown("### 📊 Step 1: Data Source")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_option = st.radio(
                "Choose data source:",
                ["📁 Upload File", "🎲 Use Sample Data"],
                horizontal=True
            )
        
        with col2:
            if data_option == "📁 Upload File":
                uploaded_file = st.file_uploader(
                    "Select your data file",
                    type=['csv', 'xlsx'],
                    help="Upload CSV or Excel file"
                )
            else:
                sample_type = st.selectbox(
                    "Sample dataset:",
                    ["Sales Data", "Customer Data", "Financial Data", "Marketing Data"]
                )
                uploaded_file = None
        
        st.markdown("### 🎯 Step 2: Analysis Goals")
        
        analysis_name = st.text_input(
            "Give your analysis a name:",
            placeholder="e.g., Q4 Sales Analysis",
            help="A descriptive name for your analysis"
        )
        
        # Predefined objective templates
        st.markdown("**Quick Templates:** (select any that apply)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_analysis = st.checkbox("📈 Trend Analysis")
            anomaly_detection = st.checkbox("🔍 Anomaly Detection")
        
        with col2:
            predictions = st.checkbox("🔮 Predictions/Forecasting")
            segmentation = st.checkbox("👥 Customer Segmentation")
        
        with col3:
            correlations = st.checkbox("🔗 Find Correlations")
            performance = st.checkbox("📊 Performance Metrics")
        
        # Custom objectives
        custom_objectives = st.text_area(
            "Additional analysis objectives (optional):",
            placeholder="- Identify top performing products\n- Analyze seasonal patterns\n- Find growth opportunities",
            height=100
        )
        
        # Simplified options (removed priority and deadline)
        with st.expander("⚙️ Advanced Settings"):
            auto_visualizations = st.checkbox("Generate visualizations", value=True)
            detailed_report = st.checkbox("Generate detailed report", value=True)
            confidence_threshold = st.slider("Minimum confidence threshold", 0.5, 1.0, 0.7)
        
        submitted = st.form_submit_button("🚀 Start Analysis", use_container_width=True, type="primary")
        
        if submitted:
            if not analysis_name:
                st.error("Please provide a name for your analysis")
            else:
                # Prepare data
                data = None
                data_id = None
                
                if data_option == "📁 Upload File" and uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            data = pd.read_csv(uploaded_file)
                        else:
                            data = pd.read_excel(uploaded_file)
                        
                        data_id = str(uuid.uuid4())
                        st.session_state.uploaded_data[data_id] = data
                        st.success(f"✅ Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
                    except Exception as e:
                        st.error(f"Error loading file: {str(e)}")
                        data = None
                
                elif data_option == "🎲 Use Sample Data":
                    # Generate sample data based on type
                    np.random.seed(42)
                    
                    if sample_type == "Sales Data":
                        data = pd.DataFrame({
                            'Date': pd.date_range('2024-01-01', periods=200, freq='D'),
                            'Sales': np.random.normal(5000, 1500, 200) * (1 + np.random.random(200) * 0.3),
                            'Product': np.random.choice(['Product A', 'Product B', 'Product C', 'Product D'], 200),
                            'Region': np.random.choice(['North', 'South', 'East', 'West'], 200),
                            'Customer_Type': np.random.choice(['New', 'Returning', 'VIP'], 200),
                            'Quantity': np.random.randint(1, 50, 200),
                            'Discount': np.random.uniform(0, 0.3, 200)
                        })
                    elif sample_type == "Customer Data":
                        data = pd.DataFrame({
                            'Customer_ID': range(1, 301),
                            'Age': np.random.randint(18, 70, 300),
                            'Income': np.random.normal(50000, 20000, 300),
                            'Spending_Score': np.random.randint(1, 100, 300),
                            'Membership_Years': np.random.randint(0, 10, 300),
                            'Products_Purchased': np.random.randint(1, 50, 300),
                            'Satisfaction': np.random.uniform(1, 5, 300)
                        })
                    else:
                        # Default financial data
                        data = pd.DataFrame({
                            'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
                            'Revenue': np.random.normal(10000, 2000, 100),
                            'Costs': np.random.normal(6000, 1000, 100),
                            'Units_Sold': np.random.randint(50, 200, 100),
                            'Market_Share': np.random.uniform(0.1, 0.3, 100)
                        })
                    
                    data_id = str(uuid.uuid4())
                    st.session_state.uploaded_data[data_id] = data
                    st.info(f"📊 Using sample {sample_type.lower()} ({data.shape[0]} rows)")
                
                if data is not None:
                    # Build objectives list
                    objectives = []
                    if trend_analysis:
                        objectives.append("Analyze trends and patterns over time")
                    if anomaly_detection:
                        objectives.append("Detect anomalies and outliers in the data")
                    if predictions:
                        objectives.append("Build predictive models and generate forecasts")
                    if segmentation:
                        objectives.append("Perform customer or data segmentation")
                    if correlations:
                        objectives.append("Identify correlations between variables")
                    if performance:
                        objectives.append("Calculate key performance metrics")
                    
                    # Add custom objectives
                    if custom_objectives:
                        custom_objs = [obj.strip() for obj in custom_objectives.split('\n') if obj.strip()]
                        objectives.extend(custom_objs)
                    
                    # Default objective if none selected
                    if not objectives:
                        objectives = ["Perform comprehensive data analysis and generate insights"]
                    
                    # Generate tasks
                    st.markdown("---")
                    st.markdown("### 🤖 AI Analysis Pipeline")
                    
                    with st.spinner("🧠 AI is planning analysis tasks..."):
                        tasks = st.session_state.workflow_manager.generate_analysis_tasks(
                            objectives=objectives,
                            data_info={
                                'shape': data.shape,
                                'columns': list(data.columns),
                                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()}
                            }
                        )
                        time.sleep(1)  # Brief pause for effect
                    
                    st.success(f"✅ Generated {len(tasks)} analysis tasks")
                    
                    # Create plan
                    plan_id = str(uuid.uuid4())
                    plan = {
                        'id': plan_id,
                        'name': analysis_name,
                        'objectives': objectives,
                        'data_source': data_option,
                        'data_id': data_id,
                        'tasks': tasks,
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    }
                    
                    st.session_state.active_plans[plan_id] = plan
                    
                    # Show tasks that will be executed
                    st.markdown("#### 📋 Tasks to be executed:")
                    task_cols = st.columns(3)
                    for i, task in enumerate(tasks):
                        with task_cols[i % 3]:
                            icon = {
                                'data_profiling': '🔍',
                                'statistical_analysis': '📊',
                                'correlation_analysis': '🔗',
                                'predictive_modeling': '🔮',
                                'anomaly_detection': '🎯',
                                'segmentation': '👥',
                                'time_series': '📈',
                                'visualization': '📊',
                                'reporting': '📄'
                            }.get(task.get('type', ''), '📌')
                            st.markdown(f"{icon} {task['name']}")
                    
                    # Execute tasks automatically
                    st.markdown("---")
                    st.markdown("### ⚡ Executing Analysis")
                    
                    successful, failed = execute_tasks_automatically(plan_id, tasks, data)
                    
                    # Generate report if successful
                    if successful > 0 and detailed_report:
                        st.markdown("---")
                        st.markdown("### 📄 Generating Report")
                        
                        with st.spinner("Creating executive report..."):
                            report = generate_plan_report(plan_id)
                            time.sleep(1)
                        
                        if report:
                            st.success("✅ Report generated successfully!")
                            
                            # Show report preview
                            st.markdown("#### 📊 Report Preview")
                            
                            # Show key sections
                            if 'sections' in report:
                                overview = report['sections'].get('overview', {})
                                if overview:
                                    st.markdown("**Overview:**")
                                    st.markdown(overview.get('content', '')[:500] + "...")
                            
                            # Download buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                html_report = st.session_state.report_generator.export_report_to_html(report)
                                st.download_button(
                                    label="📥 Download Full Report (HTML)",
                                    data=html_report,
                                    file_name=f"{analysis_name.replace(' ', '_')}_report.html",
                                    mime="text/html"
                                )
                            with col2:
                                st.download_button(
                                    label="📥 Download Data (JSON)",
                                    data=json.dumps(report, indent=2),
                                    file_name=f"{analysis_name.replace(' ', '_')}_data.json",
                                    mime="application/json"
                                )
                            
                            st.info("💡 View the full report in the Reports section")
                else:
                    st.warning("Please select a data source to begin analysis")

elif st.session_state.current_view == 'results':
    st.markdown("## 📊 Analysis Results")
    
    if not st.session_state.task_results:
        st.info("No results yet. Start a new analysis to see results here!")
        if st.button("🚀 Start Analysis"):
            st.session_state.current_view = 'analyze'
            st.rerun()
    else:
        # Group results by plan
        for plan_id, plan in st.session_state.active_plans.items():
            plan_results = []
            for task in plan['tasks']:
                if task['id'] in st.session_state.task_results:
                    plan_results.append(st.session_state.task_results[task['id']])
            
            if plan_results:
                st.markdown(f"### 📊 {plan['name']}")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Tasks", len(plan_results))
                with col2:
                    successful = len([r for r in plan_results if r.get('status') == 'success'])
                    st.metric("Successful", successful)
                with col3:
                    avg_confidence = np.mean([r.get('confidence', 0) for r in plan_results])
                    st.metric("Confidence", f"{avg_confidence*100:.0f}%")
                with col4:
                    avg_quality = np.mean([r.get('quality_score', 0) for r in plan_results])
                    st.metric("Quality", f"{avg_quality*100:.0f}%")
                
                # Detailed results
                with st.expander("View Detailed Results"):
                    for result in plan_results:
                        if result.get('status') == 'success' and 'results' in result:
                            st.markdown(f"**{result.get('task_name', 'Task')}**")
                            
                            task_data = result['results']
                            
                            # Insights
                            if 'insights' in task_data and task_data['insights']:
                                st.markdown("💡 **Insights:**")
                                for insight in task_data['insights'][:3]:
                                    st.markdown(f"- {insight}")
                            
                            # Key metrics
                            if 'metrics' in task_data:
                                st.markdown("📊 **Metrics:**")
                                metrics_df = pd.DataFrame([task_data['metrics']])
                                st.dataframe(metrics_df)
                            
                            st.markdown("---")

elif st.session_state.current_view == 'reports':
    st.markdown("## 📄 Generated Reports")
    
    if not st.session_state.plan_reports:
        st.info("No reports generated yet. Complete an analysis to generate reports!")
        if st.button("🚀 Start Analysis"):
            st.session_state.current_view = 'analyze'
            st.rerun()
    else:
        for plan_id, report in st.session_state.plan_reports.items():
            plan = st.session_state.active_plans.get(plan_id)
            if plan:
                with st.expander(f"📄 {plan['name']} - Report", expanded=True):
                    # Report content
                    if 'sections' in report:
                        for section_key, section in report['sections'].items():
                            st.markdown(f"### {section['title']}")
                            st.markdown(section['content'])
                    
                    # Download options
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        html_report = st.session_state.report_generator.export_report_to_html(report)
                        st.download_button(
                            label="📥 Download HTML Report",
                            data=html_report,
                            file_name=f"{plan['name'].replace(' ', '_')}_report.html",
                            mime="text/html",
                            key=f"html_{plan_id}"
                        )
                    with col2:
                        st.download_button(
                            label="📥 Download JSON Data",
                            data=json.dumps(report, indent=2),
                            file_name=f"{plan['name'].replace(' ', '_')}_data.json",
                            mime="application/json",
                            key=f"json_{plan_id}"
                        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🤖 Fully Automated AI Data Analysis Platform | No manual steps required
    </div>
    """,
    unsafe_allow_html=True
)