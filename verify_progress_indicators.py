"""
Verify Progress Indicators Implementation
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
    
    # Find all AI operations and check for spinners
    ai_operations = []
    
    # Pattern to find model.generate_content calls
    pattern = r'(.*?)model\.generate_content\((.*?)\)'
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'model.generate_content' in line:
            # Check if there's a spinner in the previous ~5 lines
            start = max(0, i-5)
            context_lines = lines[start:i+1]
            context = '\n'.join(context_lines)
            
            has_spinner = 'with st.spinner' in context
            
            # Find the context/purpose
            purpose = "Unknown"
            if 'Test Connection' in context:
                purpose = "API Connection Test"
            elif 'Generate AI Plan' in context or 'plan' in context.lower():
                purpose = "Plan Generation"
            elif 'chat' in context.lower() or 'question' in context.lower():
                purpose = "Chat/Q&A"
            elif 'Generate AI Insights' in context or 'insights' in context.lower():
                purpose = "AI Insights Generation"
            
            ai_operations.append({
                'line': i + 1,
                'purpose': purpose,
                'has_spinner': has_spinner,
                'code': line.strip()
            })
    
    # Check all spinners and their messages
    spinner_messages = []
    for i, line in enumerate(lines):
        if 'with st.spinner' in line:
            # Extract the message
            match = re.search(r'st\.spinner\("([^"]+)"\)', line)
            if match:
                message = match.group(1)
                spinner_messages.append({
                    'line': i + 1,
                    'message': message
                })
    
    # Print results
    print("\n📋 AI OPERATIONS CHECK:")
    all_have_spinners = True
    for op in ai_operations:
        icon = "✅" if op['has_spinner'] else "❌"
        print(f"{icon} Line {op['line']}: {op['purpose']} - {'Has spinner' if op['has_spinner'] else 'MISSING SPINNER'}")
        if not op['has_spinner']:
            all_have_spinners = False
    
    print("\n💬 SPINNER MESSAGES:")
    for spinner in spinner_messages:
        print(f"  Line {spinner['line']}: \"{spinner['message']}\"")
    
    # Validation
    print("\n✅ VALIDATION:")
    
    checks = {
        "All AI operations have spinners": all_have_spinners,
        "Spinner messages are descriptive": all(
            any(word in msg['message'].lower() for word in ['testing', 'generating', 'analyzing', 'processing'])
            for msg in spinner_messages
        ),
        "Consistent messaging style": all('...' in msg['message'] for msg in spinner_messages),
        "Total spinners found": len(spinner_messages),
        "Total AI operations": len(ai_operations)
    }
    
    all_passed = True
    for check, value in checks.items():
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            print(f"{icon} {check}")
            if not value:
                all_passed = False
        else:
            print(f"ℹ️  {check}: {value}")
    
    # Success criteria
    print("\n📊 SUCCESS CRITERIA:")
    criteria = {
        "Spinners show during all AI operations": all_have_spinners,
        "User sees descriptive messages": len(spinner_messages) >= 4,
        "Operations don't appear frozen": all_have_spinners,
        "UX feels responsive": all_have_spinners and len(spinner_messages) >= 4
    }
    
    all_criteria_met = True
    for criterion, met in criteria.items():
        icon = "✅" if met else "❌"
        print(f"{icon} {criterion}")
        if not met:
            all_criteria_met = False
    
    print("\n" + "="*70)
    if all_criteria_met:
        print("🎉 ALL CRITERIA MET - Implementation complete!")
    else:
        print("❌ Some criteria not met - Review needed")
    print("="*70)
    
    return all_criteria_met

if __name__ == "__main__":
    success = verify_implementation()
    exit(0 if success else 1)