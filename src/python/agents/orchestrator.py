"""
Phase 2: Agent Orchestrator for coordinating multiple agents
Simple, practical implementation without over-engineering
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import logging
from pathlib import Path
import json

from .base import BaseAgent, AgentConfig
from .data_analysis import DataAnalysisAgent

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Simple task representation"""
    id: str
    type: str
    data: Dict[str, Any]
    agent_type: str
    dependencies: List[str] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None


class AgentOrchestrator:
    """Coordinates multiple agents to complete complex tasks"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, Any] = {}
        
        # Register default agents
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register built-in agents"""
        self.register_agent("data_analysis", DataAnalysisAgent())
    
    def register_agent(self, name: str, agent: BaseAgent):
        """Register an agent for use"""
        self.agents[name] = agent
        logger.info(f"Registered agent: {name}")
    
    def create_task(self, task_id: str, task_type: str, data: Dict[str, Any], 
                    agent_type: str, dependencies: Optional[List[str]] = None) -> Task:
        """Create a new task"""
        task = Task(
            id=task_id,
            type=task_type,
            data=data,
            agent_type=agent_type,
            dependencies=dependencies or []
        )
        self.tasks[task_id] = task
        return task
    
    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a single task"""
        task = self.tasks.get(task_id)
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # Check dependencies
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != "completed":
                return {"error": f"Dependency {dep_id} not completed"}
        
        # Get agent
        agent = self.agents.get(task.agent_type)
        if not agent:
            return {"error": f"Agent {task.agent_type} not found"}
        
        # Execute
        task.status = "running"
        try:
            # Add dependency results to task data
            if task.dependencies:
                task.data["dependency_results"] = {
                    dep_id: self.tasks[dep_id].result 
                    for dep_id in task.dependencies
                }
            
            result = agent.execute(task.data)
            task.result = result
            task.status = "completed"
            self.results[task_id] = result
            return result
            
        except Exception as e:
            task.status = "failed"
            error_result = {"error": str(e)}
            task.result = error_result
            return error_result
    
    def execute_workflow(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute a workflow of tasks respecting dependencies"""
        # Add all tasks
        for task in tasks:
            self.tasks[task.id] = task
        
        # Sort tasks by dependencies (simple topological sort)
        sorted_tasks = self._topological_sort(tasks)
        
        results = {}
        for task in sorted_tasks:
            logger.info(f"Executing task: {task.id}")
            result = self.execute_task(task.id)
            results[task.id] = result
            
            if "error" in result:
                logger.error(f"Task {task.id} failed: {result['error']}")
                # Continue with other tasks that don't depend on this
        
        return {
            "workflow_complete": True,
            "task_results": results,
            "summary": self._generate_summary(results)
        }
    
    def _topological_sort(self, tasks: List[Task]) -> List[Task]:
        """Simple topological sort for task dependencies"""
        sorted_list = []
        visited = set()
        
        def visit(task: Task):
            if task.id in visited:
                return
            visited.add(task.id)
            
            # Visit dependencies first
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if dep_task:
                    visit(dep_task)
            
            sorted_list.append(task)
        
        for task in tasks:
            visit(task)
        
        return sorted_list
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of workflow execution"""
        total = len(results)
        successful = sum(1 for r in results.values() if "error" not in r)
        failed = total - successful
        
        return {
            "total_tasks": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0
        }
    
    async def execute_parallel(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute independent tasks in parallel (Phase 2 feature)"""
        # Group tasks by dependencies
        independent_tasks = [t for t in tasks if not t.dependencies]
        dependent_tasks = [t for t in tasks if t.dependencies]
        
        # Execute independent tasks in parallel
        async def run_task(task):
            return task.id, self.execute_task(task.id)
        
        # Run independent tasks concurrently
        results = {}
        if independent_tasks:
            task_coroutines = [run_task(t) for t in independent_tasks]
            task_results = await asyncio.gather(*task_coroutines)
            results.update(dict(task_results))
        
        # Then execute dependent tasks
        for task in self._topological_sort(dependent_tasks):
            results[task.id] = self.execute_task(task.id)
        
        return {
            "parallel_execution": True,
            "results": results
        }
    
    def save_workflow(self, filepath: Path, tasks: List[Task]):
        """Save workflow definition to file"""
        workflow = {
            "tasks": [
                {
                    "id": t.id,
                    "type": t.type,
                    "data": t.data,
                    "agent_type": t.agent_type,
                    "dependencies": t.dependencies
                }
                for t in tasks
            ]
        }
        filepath.write_text(json.dumps(workflow, indent=2))
    
    def load_workflow(self, filepath: Path) -> List[Task]:
        """Load workflow definition from file"""
        workflow = json.loads(filepath.read_text())
        tasks = []
        for task_def in workflow["tasks"]:
            task = Task(
                id=task_def["id"],
                type=task_def["type"],
                data=task_def["data"],
                agent_type=task_def["agent_type"],
                dependencies=task_def.get("dependencies", [])
            )
            tasks.append(task)
        return tasks