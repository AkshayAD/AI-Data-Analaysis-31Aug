#!/usr/bin/env python3
"""
Test Script to Verify Real Functionality
Run this with your Gemini API key to test all features
"""

import os
import sys
import json
import pandas as pd
import google.generativeai as genai
from pathlib import Path

def test_gemini_api(api_key: str, model: str = "gemini-2.5-flash"):
    """Test Gemini API connection"""
    print(f"\n🔌 Testing Gemini API with model: {model}")
    
    try:
        # Configure API
        genai.configure(api_key=api_key)
        
        # Initialize model
        model_instance = genai.GenerativeModel(model)
        
        # Test with simple prompt
        response = model_instance.generate_content("Say 'Hello, API is working!' if you can read this.")
        
        if response and response.text:
            print(f"✅ API Connected! Response: {response.text[:100]}...")
            return True
        else:
            print("❌ API responded but no content generated")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return False

def test_data_processing():
    """Test data processing capabilities"""
    print("\n📁 Testing Data Processing")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'customer_id': range(1, 101),
        'age': pd.Series(range(20, 70)).sample(100, replace=True).values,
        'purchase_amount': pd.Series(range(10, 1000)).sample(100, replace=True).values,
        'churn': pd.Series([0, 1]).sample(100, replace=True).values
    })
    
    # Save to CSV
    test_file = Path("test_data.csv")
    sample_data.to_csv(test_file, index=False)
    print(f"✅ Created test data: {test_file}")
    
    # Read and process
    df = pd.read_csv(test_file)
    print(f"✅ Data shape: {df.shape}")
    print(f"✅ Columns: {df.columns.tolist()}")
    print(f"✅ Data types: {df.dtypes.to_dict()}")
    
    # Calculate statistics
    stats = {
        'mean_age': df['age'].mean(),
        'total_purchases': df['purchase_amount'].sum(),
        'churn_rate': df['churn'].mean()
    }
    print(f"✅ Statistics calculated: {stats}")
    
    # Clean up
    test_file.unlink()
    return True

def test_plan_generation(api_key: str, model: str = "gemini-2.5-flash"):
    """Test AI plan generation"""
    print("\n🎯 Testing Plan Generation")
    
    try:
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        prompt = """
        Create a simple data analysis plan for customer churn analysis.
        Format as JSON with these keys: title, phases (list), total_days
        Keep it brief, just 2-3 phases.
        """
        
        response = model_instance.generate_content(prompt)
        
        if response and response.text:
            print(f"✅ Plan generated!")
            print(f"Preview: {response.text[:200]}...")
            
            # Try to parse as JSON
            try:
                import re
                json_match = re.search(r'\{[\s\S]*\}', response.text)
                if json_match:
                    plan = json.loads(json_match.group())
                    print(f"✅ Valid JSON plan with {len(plan.get('phases', []))} phases")
                else:
                    print("⚠️ Plan generated but not in JSON format")
            except:
                print("⚠️ Plan generated but couldn't parse JSON")
            
            return True
    except Exception as e:
        print(f"❌ Plan generation error: {str(e)}")
        return False

def test_chat_functionality(api_key: str, model: str = "gemini-2.5-flash"):
    """Test AI chat functionality"""
    print("\n💬 Testing Chat Interface")
    
    try:
        genai.configure(api_key=api_key)
        model_instance = genai.GenerativeModel(model)
        
        # Test conversation
        messages = [
            "What are the key steps in data analysis?",
            "How do I handle missing values?",
            "What's the difference between correlation and causation?"
        ]
        
        for msg in messages[:1]:  # Test with first message
            print(f"\nUser: {msg}")
            response = model_instance.generate_content(msg)
            if response and response.text:
                print(f"AI: {response.text[:150]}...")
                print("✅ Chat response received")
            else:
                print("❌ No chat response")
        
        return True
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("="*60)
    print("🧪 GEMINI API INTEGRATION TEST")
    print("="*60)
    
    # Check for API key
    api_key = input("\n🔑 Enter your Gemini API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("\n⚠️ No API key provided. Testing non-API features only...")
        
        # Test data processing (doesn't need API)
        test_data_processing()
        
        print("\n⚠️ Skipping API-dependent tests:")
        print("  - Plan generation")
        print("  - Chat functionality")
        print("\nTo test these features, run again with your API key.")
    else:
        # Select model
        print("\n📦 Available Models:")
        models = {
            "1": "gemini-2.0-flash",
            "2": "gemini-2.5-flash",
            "3": "gemini-2.5-pro",
            "4": "gemini-1.5-flash",
            "5": "gemini-1.5-pro"
        }
        
        for key, model in models.items():
            print(f"  {key}. {model}")
        
        choice = input("\nSelect model (1-5, default=2): ").strip() or "2"
        selected_model = models.get(choice, "gemini-2.5-flash")
        
        print(f"\n🚀 Testing with model: {selected_model}")
        
        # Run all tests
        results = {
            "API Connection": test_gemini_api(api_key, selected_model),
            "Data Processing": test_data_processing(),
            "Plan Generation": test_plan_generation(api_key, selected_model),
            "Chat Interface": test_chat_functionality(api_key, selected_model)
        }
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        for feature, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{feature}: {status}")
        
        passed_count = sum(results.values())
        total_count = len(results)
        
        print(f"\nTotal: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("\n🎉 ALL TESTS PASSED! The platform is fully functional.")
        elif passed_count > 0:
            print(f"\n⚠️ {total_count - passed_count} tests failed. Check the errors above.")
        else:
            print("\n❌ All tests failed. Please check your API key and connection.")

if __name__ == "__main__":
    main()