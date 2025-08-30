#!/usr/bin/env python3
"""
Phase 2 Example: Multi-Agent Coordination
Demonstrates orchestration of multiple agents working together
"""

import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from agents import (
    AgentOrchestrator, 
    Task,
    DataAnalysisAgent,
    VisualizationAgent,
    MLAgent
)


def example_orchestrated_workflow():
    """Example of multiple agents working together"""
    print("=== Multi-Agent Orchestrated Workflow ===\n")
    
    # Create orchestrator
    orchestrator = AgentOrchestrator()
    
    # Register additional agents
    orchestrator.register_agent("visualization", VisualizationAgent())
    orchestrator.register_agent("ml", MLAgent())
    
    # Define workflow tasks
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv")
    
    tasks = [
        # Task 1: Analyze data
        Task(
            id="analyze_data",
            type="analyze",
            data={"type": "analyze", "data_path": data_path},
            agent_type="data_analysis",
            dependencies=[]
        ),
        
        # Task 2: Clean data (depends on analysis)
        Task(
            id="clean_data",
            type="clean",
            data={
                "type": "clean", 
                "data_path": data_path,
                "output_path": "/tmp/cleaned_sales.csv"
            },
            agent_type="data_analysis",
            dependencies=["analyze_data"]
        ),
        
        # Task 3: Create visualizations (depends on clean data)
        Task(
            id="visualize_data",
            type="auto",
            data={
                "viz_type": "auto",
                "data_path": "/tmp/cleaned_sales.csv"
            },
            agent_type="visualization",
            dependencies=["clean_data"]
        ),
        
        # Task 4: Train ML model (depends on clean data)
        Task(
            id="train_model",
            type="train",
            data={
                "ml_task": "train",
                "data_path": "/tmp/cleaned_sales.csv",
                "target_column": "revenue",
                "task_type": "regression"
            },
            agent_type="ml",
            dependencies=["clean_data"]
        ),
        
        # Task 5: Create report (depends on all previous tasks)
        Task(
            id="create_report",
            type="report",
            data={
                "viz_type": "report",
                "data_path": "/tmp/cleaned_sales.csv"
            },
            agent_type="visualization",
            dependencies=["analyze_data", "visualize_data", "train_model"]
        )
    ]
    
    # Execute workflow
    print("Executing workflow with dependencies...")
    results = orchestrator.execute_workflow(tasks)
    
    # Display results
    print("\n=== Workflow Results ===")
    print(f"Summary: {results['summary']}")
    
    for task_id, result in results['task_results'].items():
        print(f"\nTask: {task_id}")
        if 'error' in result:
            print(f"  Status: ❌ Failed")
            print(f"  Error: {result['error']}")
        else:
            print(f"  Status: ✅ Success")
            if 'metrics' in result:
                print(f"  Metrics: {result['metrics']}")
            if 'notebook_path' in result:
                print(f"  Output: {result['notebook_path']}")
    
    return orchestrator


async def example_parallel_execution():
    """Example of parallel task execution"""
    print("\n=== Parallel Task Execution ===\n")
    
    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("visualization", VisualizationAgent())
    
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv")
    
    # Define independent tasks that can run in parallel
    parallel_tasks = [
        Task(
            id="summary",
            type="summary",
            data={"type": "summary", "data_path": data_path},
            agent_type="data_analysis",
            dependencies=[]
        ),
        Task(
            id="viz_histogram",
            type="histogram",
            data={
                "viz_type": "histogram",
                "data_path": data_path,
                "columns": ["revenue"]
            },
            agent_type="visualization",
            dependencies=[]
        ),
        Task(
            id="viz_heatmap",
            type="heatmap",
            data={
                "viz_type": "heatmap",
                "data_path": data_path
            },
            agent_type="visualization",
            dependencies=[]
        )
    ]
    
    print("Executing tasks in parallel...")
    results = await orchestrator.execute_parallel(parallel_tasks)
    
    print("\n=== Parallel Execution Results ===")
    for task_id, result in results['results'].items():
        status = "✅" if 'error' not in result else "❌"
        print(f"{status} Task {task_id} completed")


def example_ml_pipeline():
    """Example of ML pipeline with multiple agents"""
    print("\n=== Machine Learning Pipeline ===\n")
    
    orchestrator = AgentOrchestrator()
    orchestrator.register_agent("ml", MLAgent())
    orchestrator.register_agent("visualization", VisualizationAgent())
    
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv")
    
    # ML Pipeline tasks
    ml_tasks = [
        # First analyze the data
        Task(
            id="data_analysis",
            type="analyze",
            data={"type": "analyze", "data_path": data_path},
            agent_type="data_analysis",
            dependencies=[]
        ),
        
        # Try AutoML to find best model
        Task(
            id="auto_ml",
            type="auto_ml",
            data={
                "ml_task": "auto_ml",
                "data_path": data_path,
                "target_column": "revenue"
            },
            agent_type="ml",
            dependencies=["data_analysis"]
        ),
        
        # Train the best model
        Task(
            id="train_best",
            type="train",
            data={
                "ml_task": "train",
                "data_path": data_path,
                "target_column": "revenue",
                "model_type": "auto"
            },
            agent_type="ml",
            dependencies=["auto_ml"]
        ),
        
        # Create visualization of results
        Task(
            id="visualize_results",
            type="dashboard",
            data={
                "viz_type": "dashboard",
                "data_path": data_path
            },
            agent_type="visualization",
            dependencies=["train_best"]
        )
    ]
    
    print("Executing ML pipeline...")
    results = orchestrator.execute_workflow(ml_tasks)
    
    print("\n=== ML Pipeline Results ===")
    
    # Show AutoML results
    if 'auto_ml' in results['task_results']:
        auto_ml_result = results['task_results']['auto_ml']
        if 'results' in auto_ml_result:
            print("\nAutoML Model Comparison:")
            for model, scores in auto_ml_result['results'].items():
                if 'mean_r2' in scores:
                    print(f"  {model}: R² = {scores['mean_r2']:.3f} (±{scores['std_r2']:.3f})")
            print(f"\nBest Model: {auto_ml_result.get('best_model')}")
    
    # Show training results
    if 'train_best' in results['task_results']:
        train_result = results['task_results']['train_best']
        if 'metrics' in train_result:
            print(f"\nTraining Metrics: {train_result['metrics']}")
        if 'feature_importance' in train_result:
            print("\nTop Features:")
            for feat, imp in list(train_result['feature_importance'].items())[:5]:
                print(f"  {feat}: {imp:.3f}")


def example_save_load_workflow():
    """Example of saving and loading workflows"""
    print("\n=== Save/Load Workflow ===\n")
    
    orchestrator = AgentOrchestrator()
    
    # Create a workflow
    data_path = str(Path(__file__).parent.parent / "data" / "sample" / "sales_data.csv")
    
    tasks = [
        Task(
            id="task1",
            type="analyze",
            data={"type": "analyze", "data_path": data_path},
            agent_type="data_analysis",
            dependencies=[]
        ),
        Task(
            id="task2",
            type="summary",
            data={"type": "summary", "data_path": data_path},
            agent_type="data_analysis",
            dependencies=["task1"]
        )
    ]
    
    # Save workflow
    workflow_path = Path("/tmp/workflow.json")
    orchestrator.save_workflow(workflow_path, tasks)
    print(f"Workflow saved to: {workflow_path}")
    
    # Load workflow
    loaded_tasks = orchestrator.load_workflow(workflow_path)
    print(f"Loaded {len(loaded_tasks)} tasks from workflow")
    
    # Execute loaded workflow
    results = orchestrator.execute_workflow(loaded_tasks)
    print(f"Execution complete: {results['summary']}")


if __name__ == "__main__":
    print("=" * 50)
    print("PHASE 2: Multi-Agent System Examples")
    print("=" * 50)
    
    # Run examples
    example_orchestrated_workflow()
    
    # Run async example
    print("\n" + "=" * 50)
    asyncio.run(example_parallel_execution())
    
    # Run ML pipeline
    print("\n" + "=" * 50)
    example_ml_pipeline()
    
    # Save/Load workflow
    print("\n" + "=" * 50)
    example_save_load_workflow()
    
    print("\n" + "=" * 50)
    print("Phase 2 Examples Complete!")
    print("=" * 50)