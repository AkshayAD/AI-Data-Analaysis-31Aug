#!/usr/bin/env python3
"""
Human-in-Loop AI Data Analysis Platform - Fixed Navigation
Main Application Entry Point
"""

import streamlit as st
from pathlib import Path
import sys
import json

# Configure Streamlit - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Analysis Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

def main():
    """Main application with fixed navigation"""
    
    # Initialize session state with persistent navigation
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    
    if 'stage_0_complete' not in st.session_state:
        st.session_state.stage_0_complete = False
        
    if 'stage_1_complete' not in st.session_state:
        st.session_state.stage_1_complete = False
    
    # Debug info in sidebar
    with st.sidebar:
        st.write("🔍 Debug Info")
        st.write(f"Current Stage: {st.session_state.current_stage}")
        st.write(f"Stage 0 Complete: {st.session_state.stage_0_complete}")
        st.write(f"Stage 1 Complete: {st.session_state.stage_1_complete}")
        
        st.divider()
        
        # Manual navigation for testing
        st.write("Manual Navigation:")
        if st.button("Go to Stage 0"):
            st.session_state.current_stage = 0
            st.rerun()
        if st.button("Go to Stage 1"):
            st.session_state.current_stage = 1
            st.rerun()
        if st.button("Go to Stage 2"):
            st.session_state.current_stage = 2
            st.rerun()
    
    # Main content area based on current stage
    if st.session_state.current_stage == 0:
        render_stage_0()
    elif st.session_state.current_stage == 1:
        render_stage_1()
    elif st.session_state.current_stage == 2:
        render_stage_2()
    else:
        st.error(f"Unknown stage: {st.session_state.current_stage}")

def render_stage_0():
    """Render Stage 0: Input & Objectives"""
    import importlib.util
    
    # Import the actual Stage 0 module
    spec = importlib.util.spec_from_file_location(
        "input_objective", 
        str(Path(__file__).parent / "frontend" / "pages" / "00_Input_Objective_v2.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Call the main function
    module.main()

def render_stage_1():
    """Render Stage 1: Plan Generation"""
    import importlib.util
    
    # Import the actual Stage 1 module
    spec = importlib.util.spec_from_file_location(
        "plan_generation",
        str(Path(__file__).parent / "frontend" / "pages" / "01_Plan_Generation_v2.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Call the main function
    module.main()

def render_stage_2():
    """Render Stage 2: Data Understanding"""
    import importlib.util
    
    # Import the actual Stage 2 module
    spec = importlib.util.spec_from_file_location(
        "data_understanding",
        str(Path(__file__).parent / "frontend" / "pages" / "02_Data_Understanding_v2.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Call the main function if it exists
    if hasattr(module, 'main'):
        module.main()

if __name__ == "__main__":
    main()