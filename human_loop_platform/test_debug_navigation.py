#!/usr/bin/env python3
"""
Debug script to test navigation
"""
import streamlit as st
from pathlib import Path
import sys

# Configure Streamlit
st.set_page_config(
    page_title="Navigation Debug Test",
    page_icon="🔍",
    layout="wide"
)

# Add paths
sys.path.append(str(Path(__file__)))

def main():
    st.title("🔍 Navigation Debug Test")
    
    # Initialize session state
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 0
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
        
    st.write(f"Current Stage: {st.session_state.current_stage}")
    st.write(f"Counter: {st.session_state.counter}")
    st.write(f"Session State Keys: {list(st.session_state.keys())}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Stage 0"):
            st.session_state.current_stage = 0
            st.session_state.counter += 1
            st.rerun()
            
    with col2:
        if st.button("Stage 1"):
            st.session_state.current_stage = 1
            st.session_state.counter += 1
            st.rerun()
            
    with col3:
        if st.button("Stage 2"):
            st.session_state.current_stage = 2
            st.session_state.counter += 1
            st.rerun()
    
    st.divider()
    
    # Show different content based on stage
    if st.session_state.current_stage == 0:
        st.header("📝 Stage 0: Input & Objectives")
        st.write("This is Stage 0 content")
        
        if st.button("🚀 Go to Stage 1", type="primary"):
            st.session_state.current_stage = 1
            st.session_state.counter += 1
            st.success("Navigating to Stage 1...")
            st.rerun()
            
    elif st.session_state.current_stage == 1:
        st.header("🎯 Stage 1: Plan Generation")
        st.write("This is Stage 1 content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Stage 0"):
                st.session_state.current_stage = 0
                st.session_state.counter += 1
                st.rerun()
        with col2:
            if st.button("Go to Stage 2 →"):
                st.session_state.current_stage = 2
                st.session_state.counter += 1
                st.rerun()
                
    elif st.session_state.current_stage == 2:
        st.header("📊 Stage 2: Data Understanding")
        st.write("This is Stage 2 content")
        
        if st.button("← Back to Stage 1"):
            st.session_state.current_stage = 1
            st.session_state.counter += 1
            st.rerun()

if __name__ == "__main__":
    main()