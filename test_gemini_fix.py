#!/usr/bin/env python3
"""
Test that Gemini API actually works with correct model name
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

# Test direct API call first
import google.generativeai as genai

api_key = 'AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8'
genai.configure(api_key=api_key)

print("Testing Gemini API directly...")
print("-" * 50)

# Try with correct model name
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello, API is working!' in exactly 5 words.")
    print(f"✅ API Response: {response.text}")
    print("✅ Gemini API is working!")
except Exception as e:
    print(f"❌ API Error: {e}")
    print("\nTrying alternative model names...")
    
    # Try other possible model names
    alternatives = ['gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
    for model_name in alternatives:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Reply with: working")
            print(f"✅ Model '{model_name}' works! Response: {response.text}")
            break
        except Exception as e2:
            print(f"❌ Model '{model_name}' failed: {str(e2)[:50]}...")

print("\n" + "=" * 50)
print("Now testing through our wrapper...")
print("-" * 50)

from llm import GeminiClient, LLMConfig

# Test with our wrapper
config = LLMConfig(api_key=api_key)
client = GeminiClient(config)

if client.enabled:
    print(f"✅ Client initialized with model: {config.model_name}")
    
    # Simple test
    result = client.analyze_data(
        "Test data with 5 rows and 3 columns",
        "test"
    )
    
    if 'error' not in result:
        print("✅ Analysis successful!")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    else:
        print(f"❌ Analysis failed: {result['error']}")
    
    # Check usage
    stats = client.get_usage_stats()
    print(f"\nUsage stats:")
    print(f"  API calls: {stats['api_calls']}")
    print(f"  Model: {stats['model']}")
else:
    print("❌ Client not enabled")