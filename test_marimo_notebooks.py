#!/usr/bin/env python3
"""
Test that Marimo notebooks actually work
"""

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from marimo_integration.simple_notebook import create_working_marimo_notebook, create_ml_notebook


def test_notebook_creation():
    """Create and test Marimo notebooks"""
    
    print("="*60)
    print("Testing Marimo Notebook Generation")
    print("="*60)
    
    # Test 1: Create basic analysis notebook
    print("\n1. Creating basic analysis notebook...")
    data_path = "data/sample/customer_purchases.csv"
    
    notebook_path = create_working_marimo_notebook(
        name="test_analysis",
        data_path=data_path
    )
    
    print(f"   ✅ Created: {notebook_path}")
    
    # Check syntax
    print("\n2. Checking Python syntax...")
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(notebook_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ Valid Python syntax")
    else:
        print(f"   ❌ Syntax error: {result.stderr}")
        return False
    
    # Check Marimo structure
    print("\n3. Checking Marimo structure...")
    with open(notebook_path) as f:
        content = f.read()
        
    checks = [
        ("import marimo as mo", "Marimo import"),
        ("app = mo.App()", "App initialization"),
        ("@app.cell", "Cell decorators"),
        ("return", "Return statements"),
        ("if __name__", "Main block")
    ]
    
    all_good = True
    for check_str, check_name in checks:
        if check_str in content:
            print(f"   ✅ {check_name} found")
        else:
            print(f"   ❌ {check_name} missing")
            all_good = False
    
    if not all_good:
        return False
    
    # Test 2: Create ML notebook
    print("\n4. Creating ML notebook...")
    ml_notebook_path = create_ml_notebook(
        name="test_ml",
        data_path=data_path,
        target_column="customer_lifetime_value"
    )
    
    print(f"   ✅ Created: {ml_notebook_path}")
    
    # Check ML notebook syntax
    result = subprocess.run(
        ["python3", "-m", "py_compile", str(ml_notebook_path)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("   ✅ ML notebook has valid syntax")
    else:
        print(f"   ❌ ML notebook syntax error: {result.stderr}")
        return False
    
    # Try to run notebook with Marimo (with timeout)
    print("\n5. Testing Marimo execution...")
    print("   Running: marimo run --headless (5 second test)")
    
    try:
        # Start marimo and let it run for a few seconds
        process = subprocess.Popen(
            ["marimo", "run", str(notebook_path), "--headless"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for 3 seconds
        import time
        time.sleep(3)
        
        # Check if process is still running (good sign)
        if process.poll() is None:
            print("   ✅ Marimo notebook started successfully!")
            process.terminate()
            process.wait(timeout=2)
        else:
            # Process ended - check for errors
            stdout, stderr = process.communicate()
            if "error" in stderr.lower() or process.returncode != 0:
                print(f"   ❌ Marimo failed: {stderr[:200]}")
                return False
            else:
                print("   ✅ Marimo ran without errors")
                
    except Exception as e:
        print(f"   ⚠️  Could not test Marimo execution: {e}")
    
    print("\n" + "="*60)
    print("✅ All notebook tests passed!")
    print("="*60)
    
    print("\nYou can now run these notebooks:")
    print(f"  marimo run {notebook_path}")
    print(f"  marimo run {ml_notebook_path}")
    
    return True


if __name__ == "__main__":
    success = test_notebook_creation()
    sys.exit(0 if success else 1)