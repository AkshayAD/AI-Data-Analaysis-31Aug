"""
Simple verification that the Generate AI Insights button exists in the code
"""

from pathlib import Path

def verify_button_in_code():
    """Check if the button is properly implemented in the code"""
    print("\n" + "="*60)
    print("VERIFYING GENERATE AI INSIGHTS BUTTON IN CODE")
    print("="*60)
    
    app_file = Path("human_loop_platform/app_working.py")
    
    if not app_file.exists():
        print(f"❌ File not found: {app_file}")
        return False
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check for key elements
    checks = [
        ('with tab5:', 'Tab 5 definition'),
        ('AI-Powered Insights', 'AI Insights section header'),
        ('Generate AI Insights', 'Generate button text'),
        ('🤖', 'Robot emoji in button'),
        ('st.button("🤖 Generate AI Insights"', 'Full button definition'),
        ('if st.session_state.data_insights:', 'Insights display logic'),
        ('genai.GenerativeModel', 'Gemini model usage'),
    ]
    
    all_good = True
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ Found: {description}")
        else:
            print(f"❌ Missing: {description}")
            all_good = False
    
    # Find the exact line with the button
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'Generate AI Insights' in line and 'button' in line:
            print(f"\n📍 Button found at line {i}:")
            print(f"   {line.strip()}")
            
            # Show context
            print("\n📄 Context (5 lines before and after):")
            start = max(0, i-6)
            end = min(len(lines), i+5)
            for j in range(start, end):
                prefix = ">>>" if j == i-1 else "   "
                print(f"{prefix} {j+1:4d}: {lines[j]}")
    
    print("\n" + "="*60)
    
    if all_good:
        print("✅ VERIFICATION PASSED: Button is properly implemented in code")
        print("\nThe button SHOULD be visible when:")
        print("1. User is in Stage 2 (Data Understanding)")
        print("2. User clicks on the '💡 AI Insights' tab")
        print("3. API key is configured")
        print("4. Data is uploaded")
    else:
        print("❌ VERIFICATION FAILED: Button implementation has issues")
    
    print("="*60)
    
    return all_good

if __name__ == "__main__":
    result = verify_button_in_code()
    exit(0 if result else 1)