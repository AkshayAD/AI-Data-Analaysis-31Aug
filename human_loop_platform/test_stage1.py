
import streamlit as st
from pathlib import Path
import sys

# Add parent directories to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "frontend" / "pages"))

# Force Stage 1
st.session_state.current_stage = 1

# Import and run Stage 1
import importlib.util
spec = importlib.util.spec_from_file_location(
    "plan_generation",
    str(Path(__file__).parent / "frontend" / "pages" / "01_Plan_Generation.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Run the main function
module.main()
