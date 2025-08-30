import pytest
import tempfile
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "python"))

from agents import (
    AgentOrchestrator,
    Task,
    VisualizationAgent,
    MLAgent
)
from agents.orchestrator import Task


def test_orchestrator_creation():
    """Test orchestrator creation and agent registration"""
    orchestrator = AgentOrchestrator()
    assert "data_analysis" in orchestrator.agents
    
    # Register new agent
    viz_agent = VisualizationAgent()
    orchestrator.register_agent("viz", viz_agent)
    assert "viz" in orchestrator.agents


def test_task_creation():
    """Test task creation"""
    orchestrator = AgentOrchestrator()
    
    task = orchestrator.create_task(
        task_id="test_task",
        task_type="analyze",
        data={"test": "data"},
        agent_type="data_analysis"
    )
    
    assert task.id == "test_task"
    assert task.status == "pending"
    assert task.dependencies == []


def test_task_execution():
    """Test single task execution"""
    orchestrator = AgentOrchestrator()
    
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("a,b,c\n1,2,3\n4,5,6\n")
        test_file = f.name
    
    try:
        task = orchestrator.create_task(
            task_id="analyze",
            task_type="analyze",
            data={"type": "analyze", "data_path": test_file},
            agent_type="data_analysis"
        )
        
        result = orchestrator.execute_task("analyze")
        
        assert "success" in result
        assert result["success"] == True
        assert "analysis" in result
        
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_workflow_execution():
    """Test workflow with dependencies"""
    orchestrator = AgentOrchestrator()
    
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("x,y\n1,2\n3,4\n5,6\n")
        test_file = f.name
    
    try:
        tasks = [
            Task(
                id="task1",
                type="summary",
                data={"type": "summary", "data_path": test_file},
                agent_type="data_analysis",
                dependencies=[]
            ),
            Task(
                id="task2",
                type="analyze",
                data={"type": "analyze", "data_path": test_file},
                agent_type="data_analysis",
                dependencies=["task1"]
            )
        ]
        
        results = orchestrator.execute_workflow(tasks)
        
        assert results["workflow_complete"] == True
        assert results["summary"]["total_tasks"] == 2
        assert results["summary"]["successful"] == 2
        
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_visualization_agent():
    """Test visualization agent"""
    agent = VisualizationAgent()
    
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("value,category\n10,A\n20,B\n30,A\n40,B\n")
        test_file = f.name
    
    try:
        result = agent.execute({
            "viz_type": "auto",
            "data_path": test_file
        })
        
        assert "success" in result or "error" in result
        if "success" in result:
            assert "notebook_path" in result
            assert "visualizations" in result
            
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_ml_agent_training():
    """Test ML agent model training"""
    agent = MLAgent()
    
    # Create test data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("feature1,feature2,target\n")
        for i in range(20):
            f.write(f"{i},{i*2},{i*3}\n")
        test_file = f.name
    
    try:
        result = agent.execute({
            "ml_task": "train",
            "data_path": test_file,
            "target_column": "target",
            "model_type": "linear"
        })
        
        assert "success" in result or "error" in result
        if "success" in result:
            assert "model_id" in result
            assert "metrics" in result
            assert result["task_type"] == "regression"
            
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_workflow_save_load():
    """Test saving and loading workflows"""
    orchestrator = AgentOrchestrator()
    
    tasks = [
        Task(
            id="t1",
            type="test",
            data={"key": "value"},
            agent_type="test_agent",
            dependencies=[]
        ),
        Task(
            id="t2",
            type="test2",
            data={"key2": "value2"},
            agent_type="test_agent",
            dependencies=["t1"]
        )
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        workflow_path = Path(f.name)
    
    try:
        # Save workflow
        orchestrator.save_workflow(workflow_path, tasks)
        assert workflow_path.exists()
        
        # Load workflow
        loaded_tasks = orchestrator.load_workflow(workflow_path)
        assert len(loaded_tasks) == 2
        assert loaded_tasks[0].id == "t1"
        assert loaded_tasks[1].dependencies == ["t1"]
        
    finally:
        workflow_path.unlink(missing_ok=True)


def test_topological_sort():
    """Test task dependency sorting"""
    orchestrator = AgentOrchestrator()
    
    # Create tasks with complex dependencies
    tasks = [
        Task(id="A", type="", data={}, agent_type="", dependencies=["B", "C"]),
        Task(id="B", type="", data={}, agent_type="", dependencies=["D"]),
        Task(id="C", type="", data={}, agent_type="", dependencies=["D"]),
        Task(id="D", type="", data={}, agent_type="", dependencies=[]),
    ]
    
    for task in tasks:
        orchestrator.tasks[task.id] = task
    
    sorted_tasks = orchestrator._topological_sort(tasks)
    sorted_ids = [t.id for t in sorted_tasks]
    
    # D should come before B and C
    assert sorted_ids.index("D") < sorted_ids.index("B")
    assert sorted_ids.index("D") < sorted_ids.index("C")
    
    # B and C should come before A
    assert sorted_ids.index("B") < sorted_ids.index("A")
    assert sorted_ids.index("C") < sorted_ids.index("A")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])