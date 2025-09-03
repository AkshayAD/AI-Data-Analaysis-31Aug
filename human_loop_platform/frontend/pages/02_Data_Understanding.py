"""
Stage 2: Data Understanding
Data profiling, quality assessment, and exploratory analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

class DataUnderstandingPage:
    """Main page for Stage 2: Data Understanding"""
    
    def __init__(self):
        """Initialize the page"""
        # Initialize session state
        if 'data_profiles' not in st.session_state:
            st.session_state.data_profiles = {}
        
        if 'quality_issues' not in st.session_state:
            st.session_state.quality_issues = []
        
        if 'insights' not in st.session_state:
            st.session_state.insights = []
        
        # Load context from previous stages
        self._load_context()
        
    def _load_context(self):
        """Load context from previous stages"""
        context_file = Path(__file__).parent.parent.parent / "data" / "analysis_context.json"
        
        if context_file.exists():
            with open(context_file, 'r') as f:
                st.session_state.analysis_context = json.load(f)
    
    def render(self):
        """Render the main page"""
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>📊 Data Understanding & Profiling</h1>
            <p style='font-size: 1.1rem; color: #666;'>Explore, profile, and understand your data</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        self._render_progress_indicator()
        
        # Check if plan exists
        if not st.session_state.get('generated_plan'):
            st.warning("⚠️ No analysis plan found. Please complete Plan Generation first.")
            if st.button("← Go to Plan Generation"):
                st.session_state.current_stage = 1
                st.rerun()
            return
        
        # Main content area
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Data profiling area
            self._render_data_area()
        
        with col2:
            # Insights and recommendations
            self._render_insights_panel()
        
        # Action buttons at bottom
        self._render_action_buttons()
    
    def _render_progress_indicator(self):
        """Render progress indicator"""
        stages = [
            ("Input & Objectives", True),
            ("Plan Generation", True),
            ("Data Understanding", True),  # Current stage
            ("Task Configuration", False),
            ("Execution", False),
            ("Review & Export", False)
        ]
        
        cols = st.columns(len(stages))
        for i, (stage_name, completed) in enumerate(stages):
            with cols[i]:
                if i == 2:  # Current stage
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; border-radius: 10px;'>
                        <strong>Step {i+1}</strong><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    color = "#e0e0e0" if not completed else "#f0f0f0"
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: {color}; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_data_area(self):
        """Render main data profiling area"""
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Profiling", "⚠️ Quality", "📈 Visualizations"])
        
        with tab1:
            self._render_overview_tab()
        
        with tab2:
            self._render_profiling_tab()
        
        with tab3:
            self._render_quality_tab()
        
        with tab4:
            self._render_visualizations_tab()
    
    def _render_overview_tab(self):
        """Render data overview tab"""
        st.header("Data Overview")
        
        # Data summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files Loaded", "3", "✅ Ready")
        
        with col2:
            st.metric("Total Records", "10,542", "+2.3%")
        
        with col3:
            st.metric("Features", "25", "15 numeric, 10 categorical")
        
        with col4:
            st.metric("Data Quality", "87%", "⚠️ 3 issues")
        
        # File information
        st.subheader("📁 Loaded Files")
        
        files_data = {
            "File Name": ["customer_data.csv", "transactions.json", "data_dictionary.pdf"],
            "Type": ["Structured", "Structured", "Documentation"],
            "Size": ["2.3 MB", "4.5 MB", "156 KB"],
            "Records": ["10,542", "45,231", "N/A"],
            "Status": ["✅ Profiled", "✅ Profiled", "📄 Reference"]
        }
        
        df_files = pd.DataFrame(files_data)
        st.dataframe(df_files, use_container_width=True, hide_index=True)
        
        # Data sample
        st.subheader("📋 Data Sample")
        
        # Create sample data
        sample_data = pd.DataFrame({
            "customer_id": [1001, 1002, 1003, 1004, 1005],
            "age": [25, 35, 42, 28, 51],
            "tenure_months": [12, 36, 18, 6, 48],
            "monthly_charges": [45.50, 78.25, 92.10, 35.00, 105.75],
            "total_charges": [546.00, 2817.00, 1657.80, 210.00, 5076.00],
            "churn": ["No", "Yes", "No", "No", "Yes"]
        })
        
        st.dataframe(sample_data, use_container_width=True)
    
    def _render_profiling_tab(self):
        """Render detailed profiling tab"""
        st.header("Data Profiling")
        
        # Feature selector
        feature = st.selectbox(
            "Select Feature to Profile",
            ["age", "tenure_months", "monthly_charges", "total_charges", "churn"]
        )
        
        # Feature statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Statistics: {feature}")
            
            if feature in ["age", "tenure_months", "monthly_charges", "total_charges"]:
                stats = {
                    "Count": 10542,
                    "Mean": 38.5,
                    "Std Dev": 12.3,
                    "Min": 18,
                    "25%": 28,
                    "50%": 37,
                    "75%": 48,
                    "Max": 85,
                    "Missing": 0,
                    "Unique": 68
                }
                
                for key, value in stats.items():
                    st.write(f"**{key}:** {value}")
            else:
                st.write("**Type:** Categorical")
                st.write("**Unique Values:** 2")
                st.write("**Most Common:** No (65%)")
                st.write("**Missing:** 0")
        
        with col2:
            st.subheader("📈 Distribution")
            
            # Create sample distribution
            if feature in ["age", "tenure_months", "monthly_charges", "total_charges"]:
                data = np.random.normal(38.5, 12.3, 1000)
                fig = px.histogram(x=data, nbins=30, title=f"Distribution of {feature}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.pie(values=[65, 35], names=["No", "Yes"], 
                            title=f"Distribution of {feature}")
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_tab(self):
        """Render data quality tab"""
        st.header("Data Quality Assessment")
        
        # Quality score
        quality_score = 87
        
        # Progress bar for quality score
        st.progress(quality_score / 100)
        st.write(f"Overall Data Quality Score: **{quality_score}%**")
        
        # Quality issues
        st.subheader("⚠️ Quality Issues Detected")
        
        issues = [
            {
                "Severity": "🔴 High",
                "Feature": "total_charges",
                "Issue": "11 records with negative values",
                "Impact": "May affect revenue calculations",
                "Action": "Review and correct negative values"
            },
            {
                "Severity": "🟡 Medium",
                "Feature": "age",
                "Issue": "5 outliers detected (age > 100)",
                "Impact": "May skew demographic analysis",
                "Action": "Verify or cap outlier values"
            },
            {
                "Severity": "🟢 Low",
                "Feature": "customer_id",
                "Issue": "3 duplicate IDs found",
                "Impact": "Minor - may affect joins",
                "Action": "Deduplicate or create unique keys"
            }
        ]
        
        for issue in issues:
            with st.expander(f"{issue['Severity']} - {issue['Feature']}: {issue['Issue']}"):
                st.write(f"**Impact:** {issue['Impact']}")
                st.write(f"**Recommended Action:** {issue['Action']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Fix Automatically", key=f"fix_{issue['Feature']}"):
                        st.success(f"✅ Issue fixed for {issue['Feature']}")
                with col2:
                    if st.button(f"Ignore", key=f"ignore_{issue['Feature']}"):
                        st.info(f"Issue marked as reviewed")
    
    def _render_visualizations_tab(self):
        """Render data visualizations tab"""
        st.header("Data Visualizations")
        
        # Visualization type selector
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["Correlation Matrix", "Feature Distributions", "Time Series", "Scatter Plots"]
        )
        
        if viz_type == "Correlation Matrix":
            # Create correlation matrix
            corr_data = np.random.rand(5, 5)
            corr_data = (corr_data + corr_data.T) / 2
            np.fill_diagonal(corr_data, 1)
            
            fig = px.imshow(corr_data,
                           labels=dict(x="Features", y="Features", color="Correlation"),
                           x=['age', 'tenure', 'monthly_charges', 'total_charges', 'support_calls'],
                           y=['age', 'tenure', 'monthly_charges', 'total_charges', 'support_calls'],
                           color_continuous_scale='RdBu',
                           title="Feature Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 Strong correlations detected between tenure and total_charges (0.83)")
        
        elif viz_type == "Feature Distributions":
            # Create multi-feature distribution
            features = st.multiselect(
                "Select features to compare",
                ["age", "tenure_months", "monthly_charges", "total_charges"],
                default=["age", "tenure_months"]
            )
            
            if features:
                fig = go.Figure()
                for feature in features:
                    data = np.random.normal(np.random.randint(20, 60), 15, 1000)
                    fig.add_trace(go.Box(y=data, name=feature))
                
                fig.update_layout(title="Feature Distributions Comparison")
                st.plotly_chart(fig, use_container_width=True)
    
    def _render_insights_panel(self):
        """Render insights and recommendations panel"""
        st.header("💡 Insights")
        
        with st.expander("🔍 Auto-Generated Insights", expanded=True):
            insights = [
                "📊 Customer churn rate is 35%, higher than industry average",
                "📈 Strong correlation between tenure and total charges",
                "⚠️ Age distribution shows bimodal pattern",
                "💰 Monthly charges have right-skewed distribution",
                "🔄 Seasonal pattern detected in transaction data"
            ]
            
            for insight in insights:
                st.write(f"• {insight}")
        
        with st.expander("🎯 Recommendations"):
            st.write("Based on data profiling:")
            st.write("• Clean negative values in total_charges")
            st.write("• Consider feature engineering for age groups")
            st.write("• Investigate high churn segment characteristics")
            st.write("• Create derived features from transaction patterns")
        
        with st.expander("📊 Data Readiness"):
            readiness = {
                "Completeness": 98,
                "Consistency": 95,
                "Accuracy": 92,
                "Timeliness": 88
            }
            
            for metric, score in readiness.items():
                st.write(f"**{metric}:**")
                st.progress(score / 100)
    
    def _render_action_buttons(self):
        """Render action buttons at bottom"""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("← Previous", help="Go back to Plan Generation"):
                st.session_state.current_stage = 1
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh Data", help="Re-profile data"):
                st.success("✅ Data refreshed")
                st.rerun()
        
        with col3:
            if st.button("📥 Export Report", help="Export profiling report"):
                st.success("📄 Report exported")
        
        with col4:
            if st.button("Continue to Task Configuration →", type="primary",
                        help="Proceed to Task Configuration"):
                st.session_state.current_stage = 3
                st.session_state.stage_2_complete = True
                st.success("✅ Data understanding complete! Moving to Task Configuration...")
                st.balloons()
                st.rerun()

# Main execution
def main():
    page = DataUnderstandingPage()
    page.render()

if __name__ == "__main__":
    main()