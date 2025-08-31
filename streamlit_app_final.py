"""
AI Data Analysis Platform - Final Automated Version
Streamlined interface for complete automation
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import sys
import time
import uuid

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'python'))

from workflow.workflow_manager import WorkflowManager
from agents import DataAnalysisAgent, VisualizationAgent, MLAgent
from execution.task_executor import TaskExecutor
from reporting.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Platform",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.workflow_manager = WorkflowManager()
    st.session_state.task_executor = TaskExecutor()
    st.session_state.report_generator = ReportGenerator()
    st.session_state.results = {}
    st.session_state.current_analysis = None

# Title
st.markdown("# 🤖 AI Data Analysis Platform")
st.markdown("### Fully Automated Analysis in One Click")
st.markdown("---")

# Main container
with st.container():
    # Analysis form
    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Data Source")
            use_sample = st.checkbox("Use Sample Data", value=True)
            
            if not use_sample:
                uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
            else:
                sample_type = st.selectbox(
                    "Sample Dataset",
                    ["Sales Data", "Customer Data", "Financial Data"]
                )
            
            analysis_name = st.text_input(
                "Analysis Name",
                value=f"Analysis {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        
        with col2:
            st.markdown("#### 🎯 Analysis Options")
            
            # Analysis objectives
            objectives = st.text_area(
                "Analysis Objectives",
                placeholder="Enter the objectives of your analysis (e.g., identify sales trends, detect anomalies, predict customer churn...)",
                height=100,
                help="Describe what you want to achieve with this analysis"
            )
            
            # Analysis types as checkboxes
            do_profiling = st.checkbox("Data Profiling", value=True)
            do_statistics = st.checkbox("Statistical Analysis", value=True)
            do_correlations = st.checkbox("Correlation Analysis", value=True)
            do_predictions = st.checkbox("Predictive Modeling", value=True)
            do_anomalies = st.checkbox("Anomaly Detection", value=True)
            do_visualization = st.checkbox("Generate Visualizations", value=True)
        
        # Submit button
        submitted = st.form_submit_button(
            "🚀 Run Complete Analysis",
            use_container_width=True,
            type="primary"
        )

# Process analysis when form is submitted
if submitted:
    st.session_state.current_analysis = analysis_name
    st.session_state.analysis_objectives = objectives
    
    # Prepare data
    data = None
    
    if use_sample:
        # Generate sample data
        np.random.seed(42)
        
        if sample_type == "Sales Data":
            data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
                'Sales': np.random.normal(5000, 1500, 100),
                'Product': np.random.choice(['A', 'B', 'C'], 100),
                'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                'Quantity': np.random.randint(1, 100, 100)
            })
        elif sample_type == "Customer Data":
            data = pd.DataFrame({
                'CustomerID': range(1, 101),
                'Age': np.random.randint(18, 65, 100),
                'Income': np.random.normal(50000, 15000, 100),
                'Spending': np.random.normal(1000, 300, 100),
                'Satisfaction': np.random.uniform(1, 5, 100)
            })
        else:
            data = pd.DataFrame({
                'Date': pd.date_range('2024-01-01', periods=100, freq='D'),
                'Revenue': np.random.normal(10000, 2000, 100),
                'Costs': np.random.normal(6000, 1000, 100),
                'Profit': np.random.normal(4000, 1000, 100)
            })
        
        st.success(f"✅ Loaded {sample_type}: {data.shape[0]} rows, {data.shape[1]} columns")
    
    elif uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        st.success(f"✅ Loaded {uploaded_file.name}")
    
    if data is not None:
        # Show data preview
        with st.expander("📋 Data Preview"):
            st.dataframe(data.head(10))
        
        # Progress container
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### ⚡ Executing Analysis")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Build task list
            tasks = []
            if do_profiling:
                tasks.append({'id': '1', 'name': 'Data Profiling', 'type': 'data_profiling'})
            if do_statistics:
                tasks.append({'id': '2', 'name': 'Statistical Analysis', 'type': 'statistical_analysis'})
            if do_correlations:
                tasks.append({'id': '3', 'name': 'Correlation Analysis', 'type': 'correlation_analysis'})
            if do_predictions:
                tasks.append({'id': '4', 'name': 'Predictive Modeling', 'type': 'predictive_modeling'})
            if do_anomalies:
                tasks.append({'id': '5', 'name': 'Anomaly Detection', 'type': 'anomaly_detection'})
            
            # Execute tasks
            results = {}
            for i, task in enumerate(tasks):
                status_text.text(f"Running: {task['name']}...")
                progress_bar.progress((i + 1) / len(tasks))
                
                try:
                    result = st.session_state.task_executor.execute_task(task, data)
                    results[task['name']] = result
                    
                    if result.get('status') == 'success':
                        st.success(f"✅ {task['name']} completed")
                    else:
                        st.warning(f"⚠️ {task['name']} had issues")
                except Exception as e:
                    st.error(f"❌ {task['name']} failed: {str(e)}")
                
                time.sleep(0.5)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis Complete!")
        
        # Store results
        st.session_state.results = results
        
        # Display results
        st.markdown("---")
        st.markdown("### 📊 Analysis Results")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        successful = len([r for r in results.values() if r.get('status') == 'success'])
        total = len(results)
        
        with col1:
            st.metric("Tasks Completed", f"{successful}/{total}")
        
        with col2:
            avg_confidence = np.mean([r.get('confidence', 0) for r in results.values()])
            st.metric("Avg Confidence", f"{avg_confidence*100:.0f}%")
        
        with col3:
            avg_quality = np.mean([r.get('quality_score', 0) for r in results.values()])
            st.metric("Avg Quality", f"{avg_quality*100:.0f}%")
        
        with col4:
            total_insights = sum([len(r.get('results', {}).get('insights', [])) for r in results.values()])
            st.metric("Total Insights", total_insights)
        
        # Detailed results in tabs
        if results:
            tabs = st.tabs(list(results.keys()))
            
            for tab, (task_name, result) in zip(tabs, results.items()):
                with tab:
                    if result.get('status') == 'success' and 'results' in result:
                        task_data = result['results']
                        
                        # Insights
                        if 'insights' in task_data and task_data['insights']:
                            st.markdown("**💡 Key Insights:**")
                            for insight in task_data['insights']:
                                st.markdown(f"- {insight}")
                        
                        # Metrics
                        if 'metrics' in task_data:
                            st.markdown("**📈 Metrics:**")
                            st.json(task_data['metrics'])
                        
                        # Statistics
                        if 'statistics' in task_data:
                            st.markdown("**📊 Statistics:**")
                            st.json(task_data['statistics'])
                    else:
                        st.error("No results available for this task")
        
        # Generate Report
        st.markdown("---")
        st.markdown("### 📄 Executive Report")
        
        if st.button("📄 Generate Report", use_container_width=True):
            with st.spinner("Generating report..."):
                # Create plan for report generation
                plan = {
                    'id': str(uuid.uuid4()),
                    'name': analysis_name,
                    'objectives': [st.session_state.get('analysis_objectives', '')] if st.session_state.get('analysis_objectives') else ["Automated analysis"],
                    'tasks': tasks
                }
                
                # Convert results to expected format
                task_results = list(results.values())
                
                try:
                    # Generate report
                    aggregated = st.session_state.report_generator.aggregate_plan_results(plan, task_results)
                    report = st.session_state.report_generator.generate_executive_report(aggregated)
                    
                    # Display report
                    st.success("✅ Report Generated!")
                    
                    # Show report sections
                    for section_key, section in report.get('sections', {}).items():
                        st.markdown(f"#### {section['title']}")
                        st.markdown(section['content'])
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        html_report = st.session_state.report_generator.export_report_to_html(report)
                        st.download_button(
                            "📥 Download HTML Report",
                            data=html_report,
                            file_name=f"{analysis_name.replace(' ', '_')}.html",
                            mime="text/html"
                        )
                    
                    with col2:
                        st.download_button(
                            "📥 Download JSON Data",
                            data=json.dumps(report, indent=2),
                            file_name=f"{analysis_name.replace(' ', '_')}.json",
                            mime="application/json"
                        )
                    
                except Exception as e:
                    st.error(f"Report generation failed: {str(e)}")
        
        # Visualizations
        if do_visualization and data is not None:
            st.markdown("---")
            st.markdown("### 📈 Visualizations")
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Correlation heatmap
                    fig = px.imshow(
                        data[numeric_cols].corr(),
                        title="Correlation Heatmap",
                        color_continuous_scale="RdBu",
                        aspect="auto"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Distribution plot
                    if len(numeric_cols) > 0:
                        fig = px.histogram(
                            data,
                            x=numeric_cols[0],
                            title=f"Distribution of {numeric_cols[0]}",
                            nbins=30
                        )
                        st.plotly_chart(fig, use_container_width=True)

# Sidebar info
with st.sidebar:
    st.markdown("### 📊 Platform Info")
    st.info(
        "This platform provides automated data analysis with:\n"
        "- Data profiling\n"
        "- Statistical analysis\n"
        "- Predictive modeling\n"
        "- Anomaly detection\n"
        "- Automated reporting"
    )
    
    if st.session_state.current_analysis:
        st.markdown("### 📈 Current Analysis")
        st.markdown(f"**Name:** {st.session_state.current_analysis}")
        
        if st.session_state.results:
            st.markdown(f"**Tasks:** {len(st.session_state.results)}")
            successful = len([r for r in st.session_state.results.values() 
                            if r.get('status') == 'success'])
            st.markdown(f"**Successful:** {successful}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🤖 Automated AI Data Analysis Platform | One-Click Analysis
    </div>
    """,
    unsafe_allow_html=True
)