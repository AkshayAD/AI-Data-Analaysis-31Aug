"""
Stage 2: Data Understanding with Real Data Processing
Actually processes uploaded files and provides real insights
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
from datetime import datetime

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.ai_teammates.manager import AIManager

class DataUnderstandingPage:
    """Data Understanding page with real data processing"""
    
    def __init__(self):
        """Initialize with real data from previous stages"""
        # Initialize AI Manager
        self.ai_manager = AIManager()
        
        # Initialize session state
        if 'data_profiles' not in st.session_state:
            st.session_state.data_profiles = {}
        
        if 'quality_issues' not in st.session_state:
            st.session_state.quality_issues = []
        
        if 'ai_insights' not in st.session_state:
            st.session_state.ai_insights = []
        
        # Load actual data from session state
        self.uploaded_data = st.session_state.get('uploaded_data', {})
    
    def render(self):
        """Render the main page"""
        # Check prerequisites
        if not st.session_state.get('api_configured', False):
            st.error("⚠️ API not configured. Please return to Stage 0.")
            if st.button("← Back to Stage 0"):
                st.session_state.current_stage = 0
                st.rerun()
            return
        
        if not self.uploaded_data:
            st.warning("⚠️ No data found. Please upload data in Stage 0.")
            if st.button("← Back to Stage 0"):
                st.session_state.current_stage = 0
                st.rerun()
            return
        
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>📊 Data Understanding & Profiling</h1>
            <p style='font-size: 1.1rem; color: #666;'>Explore, profile, and understand your actual data</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        self._render_progress_indicator()
        
        # Main content
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Data profiling tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "🔍 Profiling", "⚠️ Quality", "📈 Visualizations", "🤖 AI Insights"])
            
            with tab1:
                self._render_overview_tab()
            
            with tab2:
                self._render_profiling_tab()
            
            with tab3:
                self._render_quality_tab()
            
            with tab4:
                self._render_visualizations_tab()
                
            with tab5:
                self._render_ai_insights_tab()
        
        with col2:
            # Insights panel
            self._render_insights_panel()
        
        # Action buttons
        self._render_action_buttons()
    
    def _render_overview_tab(self):
        """Render data overview with real data"""
        st.header("Data Overview")
        
        # Calculate real metrics
        total_files = len(self.uploaded_data)
        total_rows = sum(
            data.get('rows', 0) for data in self.uploaded_data.values()
            if data.get('type') == 'dataframe'
        )
        total_columns = sum(
            data.get('columns', 0) for data in self.uploaded_data.values()
            if data.get('type') == 'dataframe'
        )
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Files Loaded", total_files, "✅ Ready")
        
        with col2:
            st.metric("Total Records", f"{total_rows:,}")
        
        with col3:
            st.metric("Total Features", total_columns)
        
        with col4:
            quality_score = self._calculate_quality_score()
            st.metric("Data Quality", f"{quality_score}%")
        
        # File information
        st.subheader("📁 Loaded Files")
        
        files_info = []
        for filename, data in self.uploaded_data.items():
            file_info = {
                "File Name": filename,
                "Type": data.get('type', 'Unknown').title(),
                "Size": f"{data.get('size', 0):,} bytes",
                "Records": f"{data.get('rows', 'N/A'):,}" if data.get('type') == 'dataframe' else "N/A",
                "Columns": data.get('columns', 'N/A') if data.get('type') == 'dataframe' else "N/A",
                "Status": "✅ Processed"
            }
            files_info.append(file_info)
        
        if files_info:
            df_files = pd.DataFrame(files_info)
            st.dataframe(df_files, use_container_width=True, hide_index=True)
        
        # Show actual data samples
        st.subheader("📋 Data Samples")
        
        # File selector
        dataframe_files = [
            name for name, data in self.uploaded_data.items()
            if data.get('type') == 'dataframe'
        ]
        
        if dataframe_files:
            selected_file = st.selectbox("Select file to preview:", dataframe_files)
            
            if selected_file and 'data' in self.uploaded_data[selected_file]:
                df = self.uploaded_data[selected_file]['data']
                
                # Show info
                st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                st.write(f"**Columns:** {', '.join(df.columns.tolist())}")
                
                # Show sample
                st.dataframe(df.head(20), use_container_width=True)
        else:
            st.info("No dataframe files to preview")
    
    def _render_profiling_tab(self):
        """Render detailed profiling with real data"""
        st.header("Data Profiling")
        
        # Get dataframe files
        dataframe_files = [
            name for name, data in self.uploaded_data.items()
            if data.get('type') == 'dataframe' and 'data' in data
        ]
        
        if not dataframe_files:
            st.info("No dataframe files available for profiling")
            return
        
        # File and column selector
        col1, col2 = st.columns(2)
        
        with col1:
            selected_file = st.selectbox(
                "Select File",
                dataframe_files,
                key="profile_file"
            )
        
        if selected_file:
            df = self.uploaded_data[selected_file]['data']
            
            with col2:
                selected_column = st.selectbox(
                    "Select Column",
                    df.columns.tolist(),
                    key="profile_column"
                )
            
            if selected_column:
                # Profile the selected column
                col_data = df[selected_column]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"📊 Statistics: {selected_column}")
                    
                    # Basic stats
                    stats = {
                        "Count": len(col_data),
                        "Non-null": col_data.notna().sum(),
                        "Null": col_data.isna().sum(),
                        "Null %": f"{col_data.isna().sum() / len(col_data) * 100:.2f}%",
                        "Unique": col_data.nunique(),
                        "Type": str(col_data.dtype)
                    }
                    
                    # Additional stats for numeric columns
                    if pd.api.types.is_numeric_dtype(col_data):
                        stats.update({
                            "Mean": f"{col_data.mean():.2f}",
                            "Std": f"{col_data.std():.2f}",
                            "Min": col_data.min(),
                            "25%": col_data.quantile(0.25),
                            "50%": col_data.quantile(0.50),
                            "75%": col_data.quantile(0.75),
                            "Max": col_data.max()
                        })
                    
                    for key, value in stats.items():
                        st.write(f"**{key}:** {value}")
                
                with col2:
                    st.subheader("📈 Distribution")
                    
                    # Create appropriate visualization
                    if pd.api.types.is_numeric_dtype(col_data):
                        # Histogram for numeric data
                        fig = px.histogram(
                            col_data.dropna(),
                            nbins=30,
                            title=f"Distribution of {selected_column}"
                        )
                    else:
                        # Bar chart for categorical data
                        value_counts = col_data.value_counts().head(20)
                        fig = px.bar(
                            x=value_counts.index,
                            y=value_counts.values,
                            title=f"Top values in {selected_column}"
                        )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_tab(self):
        """Render data quality assessment with real analysis"""
        st.header("Data Quality Assessment")
        
        # Calculate real quality metrics
        quality_issues = []
        
        for filename, data in self.uploaded_data.items():
            if data.get('type') == 'dataframe' and 'data' in data:
                df = data['data']
                
                # Check for missing values
                missing = df.isnull().sum()
                for col, count in missing[missing > 0].items():
                    percentage = count / len(df) * 100
                    if percentage > 50:
                        severity = "🔴 High"
                        impact = "high"
                    elif percentage > 20:
                        severity = "🟡 Medium"
                        impact = "medium"
                    else:
                        severity = "🟢 Low"
                        impact = "low"
                    
                    quality_issues.append({
                        "File": filename,
                        "Severity": severity,
                        "Feature": col,
                        "Issue": f"{count} missing values ({percentage:.1f}%)",
                        "Impact": f"May affect analysis of {col}",
                        "Action": "Consider imputation or removal"
                    })
                
                # Check for duplicates
                duplicates = df.duplicated().sum()
                if duplicates > 0:
                    quality_issues.append({
                        "File": filename,
                        "Severity": "🟡 Medium",
                        "Feature": "All rows",
                        "Issue": f"{duplicates} duplicate rows found",
                        "Impact": "May skew analysis results",
                        "Action": "Review and remove duplicates if needed"
                    })
        
        # Calculate quality score
        quality_score = self._calculate_quality_score()
        
        # Display quality score
        st.progress(quality_score / 100)
        st.write(f"Overall Data Quality Score: **{quality_score}%**")
        
        # Display issues
        if quality_issues:
            st.subheader("⚠️ Quality Issues Detected")
            
            for issue in quality_issues:
                with st.expander(f"{issue['Severity']} - {issue['File']}: {issue['Feature']}"):
                    st.write(f"**Issue:** {issue['Issue']}")
                    st.write(f"**Impact:** {issue['Impact']}")
                    st.write(f"**Recommended Action:** {issue['Action']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"🤖 Get AI Suggestion", key=f"ai_{issue['File']}_{issue['Feature']}"):
                            with st.spinner("Getting AI suggestion..."):
                                suggestion = self._get_ai_quality_suggestion(issue)
                                st.info(suggestion)
                    with col2:
                        if st.button(f"✓ Mark as Resolved", key=f"resolve_{issue['File']}_{issue['Feature']}"):
                            st.success("Marked as resolved")
        else:
            st.success("✅ No quality issues detected!")
    
    def _render_visualizations_tab(self):
        """Render real data visualizations"""
        st.header("Data Visualizations")
        
        # Get dataframe files
        dataframe_files = [
            name for name, data in self.uploaded_data.items()
            if data.get('type') == 'dataframe' and 'data' in data
        ]
        
        if not dataframe_files:
            st.info("No dataframe files available for visualization")
            return
        
        # File selector
        selected_file = st.selectbox(
            "Select File for Visualization",
            dataframe_files,
            key="viz_file"
        )
        
        if selected_file:
            df = self.uploaded_data[selected_file]['data']
            
            # Visualization type selector
            viz_type = st.selectbox(
                "Select Visualization Type",
                ["Correlation Matrix", "Feature Distributions", "Scatter Plot", "Time Series", "Pair Plot"]
            )
            
            if viz_type == "Correlation Matrix":
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 1:
                    corr = df[numeric_cols].corr()
                    
                    fig = px.imshow(
                        corr,
                        labels=dict(x="Features", y="Features", color="Correlation"),
                        x=numeric_cols,
                        y=numeric_cols,
                        color_continuous_scale='RdBu',
                        title="Feature Correlation Matrix"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Find strong correlations
                    strong_corr = []
                    for i in range(len(corr)):
                        for j in range(i+1, len(corr)):
                            if abs(corr.iloc[i, j]) > 0.7:
                                strong_corr.append(f"{corr.index[i]} & {corr.columns[j]}: {corr.iloc[i, j]:.3f}")
                    
                    if strong_corr:
                        st.info(f"💡 Strong correlations detected: {', '.join(strong_corr)}")
                else:
                    st.warning("Not enough numeric columns for correlation matrix")
            
            elif viz_type == "Feature Distributions":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    selected_features = st.multiselect(
                        "Select features to compare",
                        numeric_cols,
                        default=numeric_cols[:min(3, len(numeric_cols))]
                    )
                    
                    if selected_features:
                        fig = go.Figure()
                        for feature in selected_features:
                            fig.add_trace(go.Box(y=df[feature], name=feature))
                        
                        fig.update_layout(title="Feature Distributions Comparison")
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No numeric columns for distribution plot")
            
            elif viz_type == "Scatter Plot":
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                if len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                    with col2:
                        y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
                    
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 numeric columns for scatter plot")
    
    def _render_ai_insights_tab(self):
        """Render AI-generated insights"""
        st.header("🤖 AI-Generated Insights")
        
        # Get dataframe files
        dataframe_files = [
            name for name, data in self.uploaded_data.items()
            if data.get('type') == 'dataframe' and 'data' in data
        ]
        
        if not dataframe_files:
            st.info("No dataframe files available for AI analysis")
            return
        
        # File selector
        selected_file = st.selectbox(
            "Select File for AI Analysis",
            dataframe_files,
            key="ai_file"
        )
        
        if selected_file:
            df = self.uploaded_data[selected_file]['data']
            
            # Analysis type selector
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Quick Summary", "Pattern Detection", "Anomaly Detection", "Correlation Analysis", "Predictive Insights"]
            )
            
            # Generate insights button
            if st.button("🎯 Generate AI Insights", type="primary"):
                with st.spinner("AI is analyzing your data..."):
                    insights = self.ai_manager.analyze_data(df, analysis_type.lower())
                    
                    if insights:
                        st.session_state.ai_insights.append({
                            'file': selected_file,
                            'type': analysis_type,
                            'insights': insights,
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        # Display insights
                        st.success("✅ AI Analysis Complete!")
                        
                        if 'summary' in insights:
                            st.markdown("### 📊 Analysis Summary")
                            st.write(insights['summary'])
                        
                        if 'data_shape' in insights:
                            st.write(f"**Data Shape:** {insights['data_shape']}")
                        
                        # Show any additional insights
                        for key, value in insights.items():
                            if key not in ['summary', 'data_shape', 'timestamp']:
                                with st.expander(f"📈 {key.replace('_', ' ').title()}"):
                                    if isinstance(value, dict):
                                        st.json(value)
                                    else:
                                        st.write(value)
        
        # Show previous insights
        if st.session_state.ai_insights:
            st.subheader("📚 Previous Insights")
            for insight_data in st.session_state.ai_insights[-5:]:  # Show last 5
                with st.expander(f"{insight_data['file']} - {insight_data['type']} ({insight_data['timestamp'][:10]})"):
                    if 'summary' in insight_data['insights']:
                        st.write(insight_data['insights']['summary'])
    
    def _render_insights_panel(self):
        """Render insights panel"""
        st.header("💡 Key Insights")
        
        # Calculate and display key metrics
        with st.expander("📊 Data Summary", expanded=True):
            total_files = len(self.uploaded_data)
            total_rows = sum(
                data.get('rows', 0) for data in self.uploaded_data.values()
                if data.get('type') == 'dataframe'
            )
            
            st.write(f"• **Files:** {total_files}")
            st.write(f"• **Total Records:** {total_rows:,}")
            st.write(f"• **Quality Score:** {self._calculate_quality_score()}%")
            
            if st.session_state.ai_insights:
                st.write(f"• **AI Insights Generated:** {len(st.session_state.ai_insights)}")
        
        # Quick actions
        with st.expander("⚡ Quick Actions"):
            if st.button("📊 Generate Report", use_container_width=True):
                st.info("Report generation in progress...")
            
            if st.button("🤖 Get AI Recommendations", use_container_width=True):
                st.info("Getting AI recommendations...")
            
            if st.button("📥 Export Profiles", use_container_width=True):
                st.info("Exporting data profiles...")
    
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
                elif completed:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: #d4edda; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem; 
                                background: #e0e0e0; border-radius: 10px;'>
                        <small>Step {i+1}</small><br>{stage_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_action_buttons(self):
        """Render action buttons"""
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("← Previous", help="Go back to Plan Generation"):
                st.session_state.current_stage = 1
                st.rerun()
        
        with col2:
            if st.button("🔄 Refresh Analysis", help="Re-analyze data"):
                st.success("✅ Analysis refreshed")
                st.rerun()
        
        with col3:
            if st.button("📥 Export Report", help="Export analysis report"):
                self._export_report()
        
        with col4:
            if st.button("Continue →", type="primary", help="Proceed to Task Configuration"):
                st.session_state.current_stage = 3
                st.session_state.stage_2_complete = True
                st.success("✅ Moving to Task Configuration...")
                st.balloons()
                st.rerun()
    
    def _calculate_quality_score(self) -> int:
        """Calculate real data quality score"""
        total_issues = 0
        total_checks = 0
        
        for filename, data in self.uploaded_data.items():
            if data.get('type') == 'dataframe' and 'data' in data:
                df = data['data']
                
                # Check for missing values
                total_checks += len(df.columns)
                missing_cols = (df.isnull().sum() > 0).sum()
                total_issues += missing_cols
                
                # Check for duplicates
                total_checks += 1
                if df.duplicated().sum() > 0:
                    total_issues += 1
        
        if total_checks == 0:
            return 100
        
        return int((1 - total_issues / total_checks) * 100)
    
    def _get_ai_quality_suggestion(self, issue: Dict) -> str:
        """Get AI suggestion for quality issue"""
        if not self.ai_manager.model:
            return "AI suggestions require API configuration"
        
        prompt = f"""
        Data quality issue detected:
        - File: {issue['File']}
        - Feature: {issue['Feature']}
        - Issue: {issue['Issue']}
        - Impact: {issue['Impact']}
        
        Please provide a specific, actionable suggestion to address this issue.
        """
        
        try:
            response = self.ai_manager.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not get AI suggestion: {str(e)}"
    
    def _export_report(self):
        """Export analysis report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files": list(self.uploaded_data.keys()),
            "quality_score": self._calculate_quality_score(),
            "ai_insights": st.session_state.ai_insights
        }
        
        # Create report file
        report_file = Path(__file__).parent.parent.parent / "data" / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        st.success(f"✅ Report exported to {report_file.name}")

# Main execution
def main():
    page = DataUnderstandingPage()
    page.render()

if __name__ == "__main__":
    main()