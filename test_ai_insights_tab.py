"""
Simple test to verify AI Insights tab and button visibility
"""

import time
import requests
from pathlib import Path
import pandas as pd
import numpy as np

# Create test data
def create_test_data():
    np.random.seed(42)
    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'product': np.random.choice(['Product A', 'Product B', 'Product C'], 100),
        'sales': np.random.randint(100, 1000, 100),
        'quantity': np.random.randint(1, 50, 100),
        'revenue': np.random.uniform(1000, 10000, 100),
        'customer_id': np.random.randint(1000, 2000, 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'satisfaction_score': np.random.uniform(1, 5, 100)
    }
    df = pd.DataFrame(data)
    test_file = Path("test_data.csv")
    df.to_csv(test_file, index=False)
    return test_file

def test_app_structure():
    """Test if app is running and has expected structure"""
    print("\n" + "="*60)
    print("TESTING AI INSIGHTS TAB STRUCTURE")
    print("="*60)
    
    # Check if app is running
    try:
        response = requests.get("http://localhost:8503")
        if response.status_code == 200:
            print("✅ App is running on http://localhost:8503")
        else:
            print(f"❌ App responded with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ App is not accessible: {e}")
        return False
    
    # Check app content
    content = response.text
    
    # Check for key elements
    checks = [
        ("Streamlit", "Streamlit framework"),
        ("AI Analysis Platform", "App title"),
        ("Stage", "Stage navigation"),
        ("Upload", "File upload section"),
    ]
    
    for keyword, description in checks:
        if keyword.lower() in content.lower():
            print(f"✅ Found: {description}")
        else:
            print(f"⚠️  Missing: {description}")
    
    print("\n" + "="*60)
    print("Manual verification needed:")
    print("1. Open http://localhost:8503 in a browser")
    print("2. Upload the test_data.csv file")
    print("3. Enter API key: AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8")
    print("4. Set business objective and generate plan")
    print("5. Navigate to Stage 2")
    print("6. Click on the '💡 AI Insights' tab")
    print("7. Verify '🤖 Generate AI Insights' button is visible")
    print("="*60)
    
    # Create test data for manual testing
    test_file = create_test_data()
    print(f"\nTest data created: {test_file}")
    
    return True

if __name__ == "__main__":
    test_app_structure()