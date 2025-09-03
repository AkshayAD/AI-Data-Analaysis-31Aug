"""
Stage 0: Input & Objective Setting
Main entry point for the analysis platform
"""

import streamlit as st
import sys
from pathlib import Path
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from components.ObjectiveInput import ObjectiveInput
from components.FileUploader import MultiFormatFileUploader

class InputObjectivePage:
    """Main page for Stage 0: Input & Objective Setting"""
    
    def __init__(self):
        """Initialize the page"""
        self.objective_component = ObjectiveInput()
        self.file_uploader = MultiFormatFileUploader()
        
        # Initialize session state
        if 'stage_0_complete' not in st.session_state:
            st.session_state.stage_0_complete = False
        if 'analysis_context' not in st.session_state:
            st.session_state.analysis_context = {}
    
    def render(self):
        """Render the main page"""
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🚀 AI-Powered Data Analysis Platform</h1>
            <p style='font-size: 1.2rem; color: #666;'>Human-in-the-Loop Intelligence for Better Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress indicator
        self._render_progress_indicator()
        
        # Main content area with tabs
        tab1, tab2, tab3 = st.tabs(["📝 Objectives", "📁 Data Upload", "✅ Review & Proceed"])
        
        with tab1:
            self._render_objectives_tab()
        
        with tab2:
            self._render_upload_tab()
        
        with tab3:
            self._render_review_tab()
        
        # Sidebar with help and tips
        self._render_sidebar()
    
    def _render_progress_indicator(self):
        """Render stage progress indicator"""
        stages = [
            ("Input & Objectives", True),
            ("Plan Generation", False),
            ("Data Understanding", False),
            ("Task Configuration", False),
            ("Execution", False),
            ("Review & Export", False)
        ]
        
        cols = st.columns(len(stages))
        for idx, (stage_name, is_active) in enumerate(stages):
            with cols[idx]:
                if is_active:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white; border-radius: 10px;'>
                        <strong>{idx + 1}. {stage_name}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 0.5rem;
                                background: #f0f0f0; color: #999; border-radius: 10px;'>
                        {idx + 1}. {stage_name}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_objectives_tab(self):
        """Render objectives input tab"""
        objective_data = self.objective_component.render()
        
        if objective_data:
            st.session_state.analysis_context['objective'] = objective_data
    
    def _render_upload_tab(self):
        """Render file upload tab"""
        st.header("📁 Upload Your Data Files")
        
        st.info("""
        💡 **Supported File Types:**
        - **Structured Data:** CSV, Excel, Parquet, JSON
        - **Documents:** PDF, Word, Text files
        - **Images:** PNG, JPG, GIF (charts, screenshots)
        - **SQL:** Database queries and schemas
        - **Notebooks:** Jupyter notebooks, Python scripts
        """)
        
        uploaded_files = self.file_uploader.render()
        
        if uploaded_files:
            st.session_state.analysis_context['files'] = uploaded_files
    
    def _render_review_tab(self):
        """Render review and proceed tab"""
        st.header("✅ Review Your Input")
        
        # Check if all required data is present
        has_objective = 'objective' in st.session_state.analysis_context
        has_files = 'files' in st.session_state.analysis_context and any(
            st.session_state.analysis_context['files'].values()
        )
        
        if not has_objective:
            st.warning("⚠️ Please define your analysis objective in the Objectives tab")
        
        if not has_files:
            st.warning("⚠️ Please upload at least one data file in the Data Upload tab")
        
        if has_objective and has_files:
            # Show summary
            st.success("✅ All required information provided!")
            
            # Objective summary
            with st.expander("📋 Objective Summary", expanded=True):
                obj_data = st.session_state.analysis_context['objective']
                st.markdown(f"**Objective:** {obj_data['objective']}")
                st.markdown(f"**Analysis Type:** {obj_data['analysis_type']}")
                if obj_data.get('success_criteria'):
                    st.markdown(f"**Success Criteria:** {obj_data['success_criteria']}")
            
            # Files summary
            with st.expander("📁 Uploaded Files Summary", expanded=True):
                files_data = st.session_state.analysis_context['files']
                for category, files in files_data.items():
                    if files:
                        st.markdown(f"**{category.title()}:**")
                        for file in files:
                            st.write(f"• {file['name']}")
                            if 'metadata' in file:
                                meta = file['metadata']
                                if 'rows' in meta:
                                    st.write(f"  └─ {meta['rows']} rows × {meta['columns']} columns")
                                elif 'pages' in meta:
                                    st.write(f"  └─ {meta['pages']} pages")
            
            # Proceed button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 Generate Analysis Plan",
                    type="primary",
                    use_container_width=True,
                    help="Proceed to AI-powered plan generation"
                ):
                    st.session_state.stage_0_complete = True
                    # Save context for next stage
                    self._save_context()
                    st.success("✅ Context saved! Proceeding to Plan Generation...")
                    # In real app, would navigate to next page
                    st.balloons()
                    
                    # Show next steps
                    st.info("""
                    **Next Steps:**
                    1. AI Manager will analyze your objective and data
                    2. Generate a comprehensive analysis plan
                    3. You can review, edit, and approve the plan
                    4. Chat with AI teammates for clarification
                    """)
    
    def _render_sidebar(self):
        """Render sidebar with help and tips"""
        with st.sidebar:
            st.header("💡 Help & Tips")
            
            with st.expander("📝 Writing Good Objectives"):
                st.markdown("""
                **Tips for Clear Objectives:**
                - Be specific about what you want to achieve
                - Include measurable success criteria
                - Mention key stakeholders
                - Specify time constraints
                
                **Example:**
                "Analyze customer purchase patterns from 2023 to identify 
                top factors influencing repeat purchases, with the goal of 
                increasing customer retention by 20% in Q1 2024."
                """)
            
            with st.expander("📁 Data Preparation Tips"):
                st.markdown("""
                **Before Uploading:**
                - Ensure CSV files have headers
                - Check for obvious data quality issues
                - Include data dictionaries if available
                - Upload related files together
                
                **Multiple Files:**
                You can upload multiple related files:
                - Main dataset (CSV/Excel)
                - Data dictionary (PDF/Text)
                - Previous reports (PDF)
                - SQL queries for context
                """)
            
            with st.expander("🤖 AI Teammates"):
                st.markdown("""
                **Your AI Team:**
                
                👔 **Manager:** Generates and refines analysis plans
                
                📊 **Associate:** Handles data understanding and prep
                
                🧮 **Analyst:** Executes analysis tasks
                
                ✅ **Reviewer:** Validates results and insights
                """)
            
            st.divider()
            
            # Session info
            st.caption("Session Information")
            if 'analysis_context' in st.session_state:
                context_size = len(json.dumps(st.session_state.analysis_context))
                st.text(f"Context Size: {context_size:,} bytes")
                st.text(f"Files: {sum(len(v) for v in st.session_state.analysis_context.get('files', {}).values())}")
    
    def _save_context(self):
        """Save analysis context to file for next stage"""
        context_file = Path("/root/repo/human_loop_platform/data/analysis_context.json")
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(context_file, 'w') as f:
            # Convert context to serializable format
            context = st.session_state.analysis_context.copy()
            # Don't save actual file data, just metadata
            if 'files' in context:
                for category in context['files']:
                    for file in context['files'][category]:
                        if 'data' in file:
                            del file['data']
            
            json.dump(context, f, indent=2, default=str)

# Main execution
def main():
    page = InputObjectivePage()
    page.render()

if __name__ == "__main__":
    main()