from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    """Simple configuration for agents"""
    name: str = Field(..., description="Agent name")
    description: str = Field(default="", description="Agent description")
    max_retries: int = Field(default=3, description="Maximum retry attempts")


class BaseAgent(ABC):
    """Simple base class for all agents - no over-engineering"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self._state: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task and return results"""
        pass
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self._state.copy()
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a state value"""
        self._state[key] = value
    
    def clear_state(self) -> None:
        """Clear agent state"""
        self._state.clear()