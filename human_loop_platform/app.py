#!/usr/bin/env python3
"""
Human-in-Loop AI Data Analysis Platform
Main Application Entry Point
"""

import streamlit as st
from pathlib import Path
import sys

# Configure Streamlit - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Analysis Platform - Input & Objectives",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import pages - using direct import since we'll run from pages directory
import importlib.util
spec = importlib.util.spec_from_file_location(
    "input_objective", 
    str(Path(__file__).parent / "frontend" / "pages" / "00_Input_Objective.py")
)
input_objective_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(input_objective_module)

def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    
    # Stage routing
    if st.session_state.current_stage == 0:
        # Stage 0: Input & Objectives
        input_objective_module.main()
    
    # Additional stages will be added here
    # elif st.session_state.current_stage == 1:
    #     plan_generation_page()
    # elif st.session_state.current_stage == 2:
    #     data_understanding_page()
    # etc.

if __name__ == "__main__":
    main()