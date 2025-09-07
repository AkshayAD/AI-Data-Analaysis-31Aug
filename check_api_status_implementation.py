"""
Check current API status implementation
"""

from pathlib import Path

def check_implementation():
    print("\n" + "="*60)
    print("CHECKING CURRENT API STATUS IMPLEMENTATION")
    print("="*60)
    
    app_file = Path("human_loop_platform/app_working.py")
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for current implementation
    checks = {
        "API key input": "text_input" in content and "password" in content,
        "Test Connection button": '"Test Connection"' in content,
        "Success message": '"✅ API Connected Successfully!"' in content,
        "Error message": '"❌ Connection failed:"' in content,
        "Empty key handling": '"Please enter an API key"' in content,
        "Session state for API key": "st.session_state.api_key" in content,
        "Session state for status": "api_status" in content or "connection_status" in content,
        "Persistent status": "api_connected" in content or "api_tested" in content,
    }
    
    print("\n📋 Current Implementation:")
    for feature, present in checks.items():
        icon = "✅" if present else "❌"
        print(f"{icon} {feature}")
    
    # Find relevant code sections
    lines = content.split('\n')
    
    print("\n📄 API Test Code (lines 97-107):")
    for i in range(96, 107):
        if i < len(lines):
            print(f"  {i+1:3d}: {lines[i]}")
    
    print("\n❌ MISSING FEATURES:")
    missing = []
    
    if not checks["Session state for status"]:
        missing.append("- No session state for API connection status")
    
    if not checks["Persistent status"]:
        missing.append("- Status not persistent across refreshes")
    
    if missing:
        for m in missing:
            print(m)
    else:
        print("None - all features present")
    
    print("\n🔧 REQUIRED CHANGES:")
    print("1. Add 'api_status' and 'api_status_message' to session state")
    print("2. Store test results in session state")
    print("3. Display persistent status indicator")
    print("4. Show error details on failure")
    print("="*60)
    
    return not all([checks["Session state for status"], checks["Persistent status"]])

if __name__ == "__main__":
    needs_implementation = check_implementation()
    exit(0 if not needs_implementation else 1)