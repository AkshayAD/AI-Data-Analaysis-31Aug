#!/usr/bin/env python3
"""
Simple navigation test to verify Streamlit navigation works
"""

import streamlit as st

st.set_page_config(
    page_title="Navigation Test",
    page_icon="🧪",
    layout="wide"
)

# Initialize session state
if 'stage' not in st.session_state:
    st.session_state.stage = 0

st.title("Navigation Test App")
st.write(f"Current Stage: {st.session_state.stage}")

# Navigation buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Go to Stage 0", type="secondary"):
        st.session_state.stage = 0
        st.rerun()

with col2:
    if st.button("Go to Stage 1", type="secondary"):
        st.session_state.stage = 1
        st.rerun()
        
with col3:
    if st.button("Go to Stage 2", type="secondary"):
        st.session_state.stage = 2
        st.rerun()

st.divider()

# Display different content based on stage
if st.session_state.stage == 0:
    st.header("Stage 0: Input & Objectives")
    
    with st.form("stage0_form"):
        objective = st.text_area("Enter your objective:")
        submitted = st.form_submit_button("Submit and Go to Stage 1")
        
        if submitted and objective:
            st.session_state.objective = objective
            st.session_state.stage = 1
            st.rerun()

elif st.session_state.stage == 1:
    st.header("Stage 1: Plan Generation")
    
    if 'objective' in st.session_state:
        st.info(f"Your objective: {st.session_state.objective}")
    
    if st.button("Generate Plan", type="primary"):
        st.success("Plan generated!")
        st.session_state.plan = "Sample plan"
    
    if st.button("Proceed to Stage 2"):
        st.session_state.stage = 2
        st.rerun()

elif st.session_state.stage == 2:
    st.header("Stage 2: Data Understanding")
    
    if 'plan' in st.session_state:
        st.info(f"Working with plan: {st.session_state.plan}")
    
    st.write("Data understanding features coming soon...")

# Debug info
with st.sidebar:
    st.write("Session State:")
    st.json(dict(st.session_state))