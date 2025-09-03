"""
Test to capture Stage 1 screenshots by directly setting session state
"""

import streamlit as st
import sys
from pathlib import Path
import json

# Add paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "frontend"))

# Create test context
context_data = {
    "objective": {
        "objective": "Analyze customer churn patterns to identify key factors",
        "analysis_type": "predictive",
        "success_criteria": "Identify top 5 churn factors with 85% accuracy"
    },
    "files": {
        "structured": [
            {"name": "customer_data.csv", "size": 1024000, "rows": 10000, "columns": 25}
        ],
        "unstructured": [],
        "documentation": [
            {"name": "data_dictionary.pdf", "size": 512000}
        ]
    },
    "timestamp": "2024-01-01 10:00:00"
}

# Save context
context_file = Path(__file__).parent.parent / "data" / "analysis_context.json"
context_file.parent.mkdir(exist_ok=True)
with open(context_file, 'w') as f:
    json.dump(context_data, f, indent=2)

print("✅ Context file created successfully")

# Now we'll create a script to run Stage 1 directly
stage1_test = '''
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
'''

# Save the test script
test_script = Path(__file__).parent.parent / "test_stage1.py"
with open(test_script, 'w') as f:
    f.write(stage1_test)

print("✅ Stage 1 test script created")
print("\nTo run Stage 1 directly, execute:")
print("streamlit run test_stage1.py")