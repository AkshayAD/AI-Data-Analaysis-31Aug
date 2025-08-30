"""
Base Agent Class for Agentic Marimo System

Provides the foundational structure for all specialized agents that interact
with Marimo notebooks for data analysis and machine learning tasks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid
import logging
from datetime import datetime


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Represents a task to be executed by an agent"""
    id: str
    type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    created_at: datetime
    deadline: Optional[datetime] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TaskResult:
    """Represents the result of a task execution"""
    task_id: str
    agent_id: str
    status: str
    result: Any
    notebook_id: Optional[str] = None
    execution_time: float = 0.0
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the system.
    
    This class provides common functionality for agent lifecycle management,
    task handling, and Marimo notebook interaction.
    """
    
    def __init__(self, 
                 agent_id: str = None,
                 name: str = None,
                 marimo_bridge = None,
                 config: Dict[str, Any] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            marimo_bridge: Bridge to Marimo runtime
            config: Agent configuration dictionary
        """
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"Agent_{self.agent_id[:8]}"
        self.marimo_bridge = marimo_bridge
        self.config = config or {}
        
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Task] = None
        self.task_history: List[TaskResult] = []
        self.active_notebooks: Dict[str, str] = {}
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.agent_id}")
        self._setup_logging()
        
        self.capabilities = self._define_capabilities()
        
    def _setup_logging(self):
        """Configure logging for the agent"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[%(asctime)s] [{self.name}] %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    @abstractmethod
    def _define_capabilities(self) -> Dict[str, bool]:
        """
        Define agent capabilities.
        
        Returns:
            Dictionary mapping capability names to boolean values
        """
        pass
    
    @abstractmethod
    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a specific task.
        
        Args:
            task: Task to be processed
            
        Returns:
            TaskResult containing the execution results
        """
        pass
    
    async def execute(self, task: Task) -> TaskResult:
        """
        Execute a task with proper lifecycle management.
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult with execution details
        """
        self.logger.info(f"Executing task {task.id} of type {task.type}")
        self.status = AgentStatus.BUSY
        self.current_task = task
        
        start_time = datetime.now()
        
        try:
            result = await self.process_task(task)
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.task_history.append(result)
            self.logger.info(f"Task {task.id} completed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.id}: {str(e)}")
            self.status = AgentStatus.ERROR
            
            result = TaskResult(
                task_id=task.id,
                agent_id=self.agent_id,
                status="failed",
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds()
            )
            
            self.task_history.append(result)
            return result
            
        finally:
            self.status = AgentStatus.IDLE
            self.current_task = None
    
    async def create_notebook(self, 
                            template: str = None,
                            parameters: Dict[str, Any] = None) -> str:
        """
        Create a new Marimo notebook.
        
        Args:
            template: Template name to use
            parameters: Parameters to pass to the notebook
            
        Returns:
            Notebook ID
        """
        if not self.marimo_bridge:
            raise RuntimeError("Marimo bridge not configured")
            
        notebook_id = await self.marimo_bridge.create_notebook(
            agent_id=self.agent_id,
            template=template,
            parameters=parameters
        )
        
        self.active_notebooks[notebook_id] = template or "custom"
        self.logger.info(f"Created notebook {notebook_id} from template {template}")
        
        return notebook_id
    
    async def execute_notebook_cell(self, 
                                   notebook_id: str,
                                   code: str,
                                   cell_id: str = None) -> Dict[str, Any]:
        """
        Execute code in a notebook cell.
        
        Args:
            notebook_id: ID of the notebook
            code: Python code to execute
            cell_id: Optional specific cell ID
            
        Returns:
            Execution results
        """
        if notebook_id not in self.active_notebooks:
            raise ValueError(f"Notebook {notebook_id} not found in active notebooks")
            
        result = await self.marimo_bridge.execute_cell(
            notebook_id=notebook_id,
            code=code,
            cell_id=cell_id
        )
        
        self.logger.debug(f"Executed cell in notebook {notebook_id}")
        return result
    
    async def get_notebook_state(self, notebook_id: str) -> Dict[str, Any]:
        """
        Get the current state of a notebook.
        
        Args:
            notebook_id: ID of the notebook
            
        Returns:
            Notebook state including variables and outputs
        """
        if notebook_id not in self.active_notebooks:
            raise ValueError(f"Notebook {notebook_id} not found in active notebooks")
            
        state = await self.marimo_bridge.get_notebook_state(notebook_id)
        return state
    
    async def close_notebook(self, notebook_id: str):
        """
        Close a notebook and clean up resources.
        
        Args:
            notebook_id: ID of the notebook to close
        """
        if notebook_id in self.active_notebooks:
            await self.marimo_bridge.close_notebook(notebook_id)
            del self.active_notebooks[notebook_id]
            self.logger.info(f"Closed notebook {notebook_id}")
    
    def can_handle_task(self, task_type: str) -> bool:
        """
        Check if agent can handle a specific task type.
        
        Args:
            task_type: Type of task to check
            
        Returns:
            True if agent can handle the task type
        """
        return task_type in self.capabilities and self.capabilities[task_type]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Dictionary containing agent status information
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "current_task": self.current_task.id if self.current_task else None,
            "active_notebooks": list(self.active_notebooks.keys()),
            "task_history_count": len(self.task_history),
            "capabilities": self.capabilities
        }
    
    async def cleanup(self):
        """Clean up agent resources"""
        self.logger.info("Cleaning up agent resources")
        
        # Close all active notebooks
        notebook_ids = list(self.active_notebooks.keys())
        for notebook_id in notebook_ids:
            await self.close_notebook(notebook_id)
        
        self.status = AgentStatus.OFFLINE
        self.logger.info("Agent cleanup completed")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.agent_id}, name={self.name}, status={self.status.value})"