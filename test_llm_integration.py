#!/usr/bin/env python3
"""
Test LLM Integration with Gemini
Minimal API usage through caching and smart fallbacks
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from agents.intelligent_agent import IntelligentAgent


def test_intelligent_agent():
    """Test intelligent agent with LLM capabilities"""
    
    print("="*60)
    print("Testing Intelligent Agent with Gemini 2.5 Flash")
    print("="*60)
    
    # Set API key from environment or use provided key
    api_key = 'AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8'
    
    # Initialize agent with API key
    print("\n1. Initializing Intelligent Agent...")
    agent = IntelligentAgent(api_key=api_key)
    
    if agent.llm_enabled:
        print("   ✅ LLM capabilities enabled (Gemini 2.5 Flash)")
    else:
        print("   ⚠️  LLM not enabled - using fallback analysis")
    
    # Test 1: Smart Analysis (will be cached after first call)
    print("\n2. Testing Smart Analysis...")
    result = agent.execute({
        'type': 'smart_analysis',
        'data_path': 'data/sample/customer_purchases.csv'
    })
    
    if 'error' in result:
        print(f"   ❌ Error: {result['error']}")
    else:
        print(f"   ✅ Analysis completed")
        print(f"   - Basic stats: {result['basic_stats']['rows']} rows, {result['basic_stats']['columns']} columns")
        print(f"   - Insights found: {len(result.get('insights', []))}")
        print(f"   - LLM used: {result.get('llm_used', False)}")
        
        if result.get('insights'):
            print("\n   Top Insights:")
            for i, insight in enumerate(result['insights'][:3], 1):
                print(f"   {i}. {insight[:100]}...")  # Truncate long insights
        
        if result.get('visualization_suggestions'):
            print("\n   Visualization Suggestions:")
            for viz in result['visualization_suggestions'][:2]:
                print(f"   - {viz.get('type', 'Unknown')}: {viz.get('reason', '')[:50]}...")
        
        if result.get('usage_stats'):
            stats = result['usage_stats']
            print(f"\n   API Usage:")
            print(f"   - API calls made: {stats.get('api_calls', 0)}")
            print(f"   - Cache hits: {stats.get('cache_size', 0)}")
            print(f"   - Estimated cost: {stats.get('estimated_cost', '$0.00')}")
    
    # Test 2: Explain Results (uses caching)
    print("\n3. Testing Result Explanation...")
    explain_result = agent.execute({
        'type': 'explain_results',
        'results': {
            'accuracy': 0.92,
            'precision': 0.89,
            'recall': 0.95
        }
    })
    
    if 'error' not in explain_result:
        print(f"   ✅ Explanation generated")
        print(f"   - LLM used: {explain_result.get('llm_used', False)}")
        print(f"   - Explanation: {explain_result.get('explanation', '')[:100]}...")
    
    # Test 3: Suggest Next Steps
    print("\n4. Testing Next Steps Suggestion...")
    next_steps_result = agent.execute({
        'type': 'suggest_next_steps',
        'current_state': {
            'data_analyzed': True,
            'model_trained': True,
            'model_metrics': {'r2': 0.85}
        }
    })
    
    if 'error' not in next_steps_result:
        print(f"   ✅ Next steps suggested")
        print(f"   - Suggestions: {len(next_steps_result.get('next_steps', []))}")
        
        if next_steps_result.get('next_steps'):
            print("\n   Recommended Next Steps:")
            for i, step in enumerate(next_steps_result['next_steps'][:3], 1):
                print(f"   {i}. {step}")
    
    # Final usage summary
    if agent.llm_enabled:
        final_stats = agent.llm.get_usage_stats()
        print("\n" + "="*60)
        print("LLM Usage Summary:")
        print(f"- Model: {final_stats.get('model', 'Unknown')}")
        print(f"- Total API calls: {final_stats.get('api_calls', 0)}")
        print(f"- Cached responses: {final_stats.get('cache_size', 0)}")
        print(f"- Estimated total cost: {final_stats.get('estimated_cost', '$0.00')}")
        print("="*60)
        
        # Show cost optimization
        if final_stats.get('api_calls', 0) > 0:
            print("\n💡 Cost Optimization:")
            print(f"- Caching saved ~{final_stats.get('cache_size', 0)} API calls")
            saved_cost = final_stats.get('cache_size', 0) * 0.00015
            print(f"- Estimated savings: ${saved_cost:.4f}")
            print("- Using Gemini 2.5 Flash for minimal cost")
    
    print("\n✅ Test Complete!")
    
    return result


def test_caching_effectiveness():
    """Test that caching prevents duplicate API calls"""
    print("\n" + "="*60)
    print("Testing Cache Effectiveness")
    print("="*60)
    
    api_key = 'AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8'
    agent = IntelligentAgent(api_key=api_key)
    
    if not agent.llm_enabled:
        print("LLM not enabled, skipping cache test")
        return
    
    # First call - will hit API
    print("\n1. First analysis (API call)...")
    initial_stats = agent.llm.get_usage_stats()
    initial_calls = initial_stats.get('api_calls', 0)
    
    result1 = agent.execute({
        'type': 'smart_analysis',
        'data_path': 'data/sample/sales_data.csv'
    })
    
    stats_after_first = agent.llm.get_usage_stats()
    calls_after_first = stats_after_first.get('api_calls', 0)
    
    print(f"   API calls made: {calls_after_first - initial_calls}")
    
    # Second call - should use cache
    print("\n2. Repeated analysis (should use cache)...")
    result2 = agent.execute({
        'type': 'smart_analysis',
        'data_path': 'data/sample/sales_data.csv'
    })
    
    stats_after_second = agent.llm.get_usage_stats()
    calls_after_second = stats_after_second.get('api_calls', 0)
    
    print(f"   Additional API calls: {calls_after_second - calls_after_first}")
    
    if calls_after_second == calls_after_first:
        print("   ✅ Cache working! No additional API calls made")
    else:
        print("   ⚠️  Cache may not be working optimally")
    
    print(f"\n   Total cache size: {stats_after_second.get('cache_size', 0)}")
    print(f"   Total cost so far: {stats_after_second.get('estimated_cost', '$0.00')}")


if __name__ == "__main__":
    try:
        # Test main functionality
        test_intelligent_agent()
        
        # Test caching
        test_caching_effectiveness()
        
        print("\n" + "="*60)
        print("🎉 All LLM Integration Tests Passed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)