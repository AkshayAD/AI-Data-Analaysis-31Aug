#!/usr/bin/env python3
"""
Human-in-Loop AI Data Analysis Platform
Main Application Entry Point - FIXED VERSION
"""

import streamlit as st
from pathlib import Path
import sys

# Configure Streamlit - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Analysis Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "frontend"))
sys.path.append(str(Path(__file__).parent / "frontend" / "pages"))

def main():
    """Main application entry point with fixed navigation"""
    
    # Initialize all session state variables upfront
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    
    if 'analysis_context' not in st.session_state:
        st.session_state.analysis_context = {}
    
    if 'generated_plan' not in st.session_state:
        st.session_state.generated_plan = None
        
    if 'stage_0_complete' not in st.session_state:
        st.session_state.stage_0_complete = False
    
    if 'plan_approved' not in st.session_state:
        st.session_state.plan_approved = False
    
    # Debug info in sidebar
    with st.sidebar:
        st.caption("🔍 Debug Navigation")
        st.caption(f"Stage: {st.session_state.current_stage}")
        st.caption(f"Stage 0: {'✅' if st.session_state.stage_0_complete else '⏳'}")
        st.divider()
        
        # Force navigation buttons for testing
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("S0", help="Force Stage 0"):
                st.session_state.current_stage = 0
                st.rerun()
        with col2:
            if st.button("S1", help="Force Stage 1"):
                st.session_state.current_stage = 1
                st.rerun()
        with col3:
            if st.button("S2", help="Force Stage 2"):
                st.session_state.current_stage = 2
                st.rerun()
    
    # Stage routing - import modules only when needed
    if st.session_state.current_stage == 0:
        # Stage 0: Input & Objectives
        try:
            from frontend.pages.stage_0 import InputObjectivePage
            page = InputObjectivePage()
            page.render()
        except ImportError:
            # Fallback - import the actual file
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "input_objective", 
                str(Path(__file__).parent / "frontend" / "pages" / "00_Input_Objective.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Create page instance and render
            page = module.InputObjectivePage()
            page.render()
    
    elif st.session_state.current_stage == 1:
        # Stage 1: Plan Generation
        try:
            from frontend.pages.stage_1 import PlanGenerationPage
            page = PlanGenerationPage()
            page.render()
        except ImportError:
            # Fallback - import the actual file
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "plan_generation",
                str(Path(__file__).parent / "frontend" / "pages" / "01_Plan_Generation.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Create page instance and render
            page = module.PlanGenerationPage()
            page.render()
    
    elif st.session_state.current_stage == 2:
        # Stage 2: Data Understanding (placeholder)
        st.header("📊 Stage 2: Data Understanding")
        st.info("This stage is coming soon...")
        if st.button("← Back to Plan Generation"):
            st.session_state.current_stage = 1
            st.rerun()
    
    else:
        st.error(f"Unknown stage: {st.session_state.current_stage}")

if __name__ == "__main__":
    main()