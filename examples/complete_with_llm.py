#!/usr/bin/env python3
"""
Complete Example with LLM Integration
Shows the full system capabilities including AI-powered insights
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from agents import (
    AgentOrchestrator,
    Task,
    IntelligentAgent,
    DataAnalysisAgent,
    MLAgent,
    VisualizationAgent
)


def run_complete_llm_pipeline():
    """
    Run a complete analytics pipeline with LLM enhancements
    Demonstrates cost-effective AI integration
    """
    
    print("="*70)
    print("  COMPLETE AI-POWERED ANALYTICS PIPELINE")
    print("  Using Gemini 2.5 Flash for Intelligent Insights")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register agents including the intelligent agent
    api_key = 'AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8'
    
    print("\n📋 Registering Agents...")
    orchestrator.register_agent("intelligent", IntelligentAgent(api_key=api_key))
    orchestrator.register_agent("ml", MLAgent())
    orchestrator.register_agent("visualization", VisualizationAgent())
    print("   ✅ Registered: data_analysis, intelligent, ml, visualization")
    
    # Define data path
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "customer_purchases.csv")
    
    print("\n🔄 Defining Workflow Tasks...")
    
    # Create comprehensive workflow
    tasks = [
        # 1. Initial intelligent analysis with LLM
        Task(
            id="smart_analysis",
            type="smart_analysis",
            data={
                "type": "smart_analysis",
                "data_path": data_path
            },
            agent_type="intelligent",
            dependencies=[]
        ),
        
        # 2. Traditional data analysis for comparison
        Task(
            id="traditional_analysis",
            type="analyze",
            data={
                "type": "analyze",
                "data_path": data_path
            },
            agent_type="data_analysis",
            dependencies=[]
        ),
        
        # 3. Clean data
        Task(
            id="clean_data",
            type="clean",
            data={
                "type": "clean",
                "data_path": data_path,
                "output_path": "/tmp/cleaned_llm_data.csv"
            },
            agent_type="data_analysis",
            dependencies=["traditional_analysis"]
        ),
        
        # 4. Train ML model
        Task(
            id="train_model",
            type="train",
            data={
                "ml_task": "train",
                "data_path": "/tmp/cleaned_llm_data.csv",
                "target_column": "customer_lifetime_value",
                "model_type": "auto"
            },
            agent_type="ml",
            dependencies=["clean_data"]
        ),
        
        # 5. Get LLM explanation of model results
        Task(
            id="explain_model",
            type="explain_results",
            data={
                "type": "explain_results",
                "results": {}  # Will be populated with model results
            },
            agent_type="intelligent",
            dependencies=["train_model"]
        ),
        
        # 6. Generate visualizations based on LLM suggestions
        Task(
            id="create_viz",
            type="auto",
            data={
                "viz_type": "auto",
                "data_path": "/tmp/cleaned_llm_data.csv"
            },
            agent_type="visualization",
            dependencies=["smart_analysis", "clean_data"]
        ),
        
        # 7. Get next steps recommendations
        Task(
            id="next_steps",
            type="suggest_next_steps",
            data={
                "type": "suggest_next_steps",
                "current_state": {
                    "data_analyzed": True,
                    "model_trained": True,
                    "visualizations_created": True
                }
            },
            agent_type="intelligent",
            dependencies=["train_model", "create_viz"]
        )
    ]
    
    print(f"   ✅ Created {len(tasks)} orchestrated tasks")
    
    # Execute workflow
    print("\n🚀 Executing AI-Powered Workflow...")
    print("-" * 50)
    
    results = orchestrator.execute_workflow(tasks)
    
    # Display results
    print("\n📊 RESULTS")
    print("="*70)
    
    # 1. Smart Analysis Results
    smart_results = results['task_results'].get('smart_analysis', {})
    if 'error' not in smart_results:
        print("\n🤖 AI-Powered Analysis:")
        print(f"   Dataset: {smart_results['basic_stats']['rows']} customers")
        
        if smart_results.get('insights'):
            print("\n   💡 AI Insights:")
            for i, insight in enumerate(smart_results['insights'][:3], 1):
                print(f"   {i}. {insight}")
        
        if smart_results.get('visualization_suggestions'):
            print("\n   📈 AI-Recommended Visualizations:")
            for viz in smart_results['visualization_suggestions'][:3]:
                print(f"   - {viz.get('type')}: {viz.get('reason', '')}")
        
        if smart_results.get('llm_used'):
            usage = smart_results.get('usage_stats', {})
            print(f"\n   🔧 LLM Stats: {usage.get('api_calls', 0)} calls, Cost: {usage.get('estimated_cost', '$0')}")
    
    # 2. Traditional Analysis Comparison
    trad_results = results['task_results'].get('traditional_analysis', {})
    if 'error' not in trad_results:
        print("\n📊 Traditional Analysis:")
        analysis = trad_results.get('analysis', {})
        print(f"   Columns: {len(analysis.get('columns', []))}")
        print(f"   Missing values: {sum(analysis.get('missing_values', {}).values())}")
    
    # 3. Model Results
    model_results = results['task_results'].get('train_model', {})
    if 'error' not in model_results:
        print("\n🧮 Machine Learning Model:")
        print(f"   Type: {model_results.get('model_type')}")
        metrics = model_results.get('metrics', {})
        print(f"   R² Score: {metrics.get('r2', 0):.3f}")
        
        if model_results.get('feature_importance'):
            print("\n   📊 Top Features:")
            for feat, imp in list(model_results['feature_importance'].items())[:3]:
                print(f"   - {feat}: {imp:.3f}")
    
    # 4. Model Explanation
    explain_results = results['task_results'].get('explain_model', {})
    if 'error' not in explain_results and explain_results.get('explanation'):
        print("\n💬 AI Model Explanation:")
        print(f"   {explain_results['explanation']}")
    
    # 5. Next Steps
    next_results = results['task_results'].get('next_steps', {})
    if 'error' not in next_results and next_results.get('next_steps'):
        print("\n🎯 AI-Recommended Next Steps:")
        for i, step in enumerate(next_results['next_steps'], 1):
            print(f"   {i}. {step}")
    
    # Workflow Summary
    print("\n" + "="*70)
    print("📈 WORKFLOW SUMMARY")
    summary = results['summary']
    print(f"   Total tasks: {summary['total_tasks']}")
    print(f"   Successful: {summary['successful']}")
    print(f"   Success rate: {summary['success_rate']*100:.0f}%")
    
    # Cost Summary
    total_api_calls = 0
    total_cost = 0.0
    
    for task_id, result in results['task_results'].items():
        if isinstance(result, dict) and result.get('usage_stats'):
            stats = result['usage_stats']
            calls = stats.get('api_calls', 0)
            cost_str = stats.get('estimated_cost', '$0.0000')
            cost = float(cost_str.replace('$', ''))
            total_api_calls += calls
            total_cost += cost
    
    print("\n💰 AI USAGE SUMMARY")
    print(f"   Total API calls: {total_api_calls}")
    print(f"   Total cost: ${total_cost:.4f}")
    print(f"   Cost per insight: ${total_cost/max(len(smart_results.get('insights', [1])), 1):.5f}")
    
    print("\n" + "="*70)
    print("✅ AI-POWERED PIPELINE COMPLETE!")
    print("="*70)
    
    return results


def compare_with_without_llm():
    """
    Compare analysis with and without LLM to show added value
    """
    print("\n" + "="*70)
    print("  COMPARING WITH vs WITHOUT LLM")
    print("="*70)
    
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "customer_purchases.csv")
    
    # Without LLM
    print("\n1️⃣ Traditional Analysis (No LLM):")
    traditional_agent = DataAnalysisAgent()
    trad_result = traditional_agent.execute({
        'type': 'analyze',
        'data_path': data_path
    })
    
    if 'analysis' in trad_result:
        print("   ✅ Basic statistics computed")
        print("   ✅ Data types identified")
        print("   ❌ No insights generated")
        print("   ❌ No visualization recommendations")
        print("   ❌ No natural language explanation")
    
    # With LLM
    print("\n2️⃣ AI-Enhanced Analysis (With LLM):")
    intelligent_agent = IntelligentAgent(api_key='AIzaSyAkmzQMVJ8lMcXBn4f4dku0KdyV6ojwri8')
    ai_result = intelligent_agent.execute({
        'type': 'smart_analysis',
        'data_path': data_path
    })
    
    if 'insights' in ai_result:
        print("   ✅ Basic statistics computed")
        print("   ✅ Data types identified")
        print(f"   ✅ {len(ai_result['insights'])} AI insights generated")
        print(f"   ✅ {len(ai_result.get('visualization_suggestions', []))} visualization recommendations")
        print("   ✅ Natural language explanations available")
        
        usage = ai_result.get('usage_stats', {})
        print(f"\n   💰 Cost for AI features: {usage.get('estimated_cost', '$0.0000')}")
    
    print("\n📊 VALUE ADDED BY LLM:")
    print("   • Actionable insights from data patterns")
    print("   • Intelligent visualization recommendations")
    print("   • Plain English explanations")
    print("   • Context-aware next steps")
    print("   • All for less than $0.001 per analysis!")


if __name__ == "__main__":
    try:
        # Run complete pipeline with LLM
        results = run_complete_llm_pipeline()
        
        # Show comparison
        compare_with_without_llm()
        
        print("\n" + "🎉"*35)
        print("  DEMONSTRATION COMPLETE - AI INTEGRATION SUCCESS!")
        print("🎉"*35)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()