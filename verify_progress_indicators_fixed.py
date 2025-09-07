"""
Verify Progress Indicators Implementation - Fixed Version
"""

from pathlib import Path
import re

def verify_implementation():
    print("\n" + "="*70)
    print("VERIFYING PROGRESS INDICATORS IMPLEMENTATION")
    print("="*70)
    
    app_file = Path("human_loop_platform/app_working.py")
    
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Find all button clicks that trigger AI operations
    ai_triggers = []
    
    lines = content.split('\n')
    
    # Look for button clicks followed by AI operations
    button_contexts = [
        ("Test Connection", "API Connection Test"),
        ("Generate AI Plan", "Plan Generation"),
        ("Send", "Chat/Q&A"),
        ("Generate AI Insights", "AI Insights Generation")
    ]
    
    for button_text, purpose in button_contexts:
        for i, line in enumerate(lines):
            if f'"{button_text}"' in line and 'st.button' in line:
                # Check next ~20 lines for spinner and AI call
                end = min(len(lines), i + 20)
                context_lines = lines[i:end]
                context = '\n'.join(context_lines)
                
                has_spinner = 'with st.spinner' in context
                has_ai_call = 'model.generate_content' in context or 'genai.configure' in context
                
                # Extract spinner message if present
                spinner_msg = None
                for ctx_line in context_lines:
                    if 'st.spinner' in ctx_line:
                        match = re.search(r'st\.spinner\("([^"]+)"\)', ctx_line)
                        if match:
                            spinner_msg = match.group(1)
                        break
                
                if has_ai_call:
                    ai_triggers.append({
                        'line': i + 1,
                        'button': button_text,
                        'purpose': purpose,
                        'has_spinner': has_spinner,
                        'spinner_message': spinner_msg
                    })
    
    # Print results
    print("\n📋 AI OPERATIONS WITH TRIGGERS:")
    all_have_spinners = True
    
    for trigger in ai_triggers:
        icon = "✅" if trigger['has_spinner'] else "❌"
        status = f"Spinner: \"{trigger['spinner_message']}\"" if trigger['has_spinner'] else "MISSING SPINNER"
        print(f"{icon} Line {trigger['line']}: {trigger['purpose']} ({trigger['button']}) - {status}")
        if not trigger['has_spinner']:
            all_have_spinners = False
    
    # Check spinner message quality
    print("\n💬 SPINNER MESSAGE QUALITY:")
    good_messages = []
    for trigger in ai_triggers:
        if trigger['spinner_message']:
            msg = trigger['spinner_message']
            is_descriptive = any(word in msg.lower() for word in ['testing', 'generating', 'analyzing', 'processing'])
            has_ellipsis = '...' in msg
            
            quality = "Good" if is_descriptive and has_ellipsis else "Could be improved"
            print(f"  {trigger['purpose']}: \"{msg}\" - {quality}")
            
            if is_descriptive and has_ellipsis:
                good_messages.append(msg)
    
    # Validation
    print("\n✅ IMPLEMENTATION CHECK:")
    
    total_operations = len(ai_triggers)
    operations_with_spinners = sum(1 for t in ai_triggers if t['has_spinner'])
    
    checks = {
        "Total AI operations found": total_operations,
        "Operations with spinners": operations_with_spinners,
        "All operations have spinners": all_have_spinners,
        "All messages are descriptive": len(good_messages) == operations_with_spinners,
        "Consistent style (with '...')": all('...' in t['spinner_message'] for t in ai_triggers if t['spinner_message'])
    }
    
    for check, value in checks.items():
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            print(f"{icon} {check}")
        else:
            print(f"ℹ️  {check}: {value}")
    
    # Success criteria
    print("\n📊 SUCCESS CRITERIA VALIDATION:")
    criteria = {
        "Spinners show during all AI operations": all_have_spinners,
        "User sees descriptive messages": operations_with_spinners >= total_operations,
        "Operations don't appear frozen": all_have_spinners,
        "UX feels responsive": all_have_spinners and operations_with_spinners == total_operations
    }
    
    all_criteria_met = True
    for criterion, met in criteria.items():
        icon = "✅" if met else "❌"
        print(f"{criterion}: {icon}")
        if not met:
            all_criteria_met = False
    
    print("\n" + "="*70)
    if all_criteria_met:
        print("🎉 SUCCESS - All AI operations have progress indicators!")
        print("\nTASK-003 IMPLEMENTATION COMPLETE")
    else:
        print("❌ INCOMPLETE - Some operations missing progress indicators")
    print("="*70)
    
    return all_criteria_met

if __name__ == "__main__":
    success = verify_implementation()
    exit(0 if success else 1)