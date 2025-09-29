"""Base agent class for the agentic research system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all research agents."""
    
    def __init__(self, agent_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Name of the agent
            config: Optional configuration dictionary
        """
        self.agent_name = agent_name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")
        self.execution_history = []
        
    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: Task specification dictionary
            
        Returns:
            Task execution results
        """
        pass
    
    def log_execution(self, task: Dict[str, Any], result: Dict[str, Any], 
                     status: str = "completed") -> None:
        """
        Log task execution details.
        
        Args:
            task: Task that was executed
            result: Execution results
            status: Execution status
        """
        execution_record = {
            'timestamp': datetime.now().isoformat(),
            'agent_name': self.agent_name,
            'task': task,
            'result': result,
            'status': status
        }
        
        self.execution_history.append(execution_record)
        self.logger.info(f"Task {status}: {task.get('type', 'unknown')}")
    
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this agent supports.
        
        Returns:
            List of capability names
        """
        return getattr(self, 'capabilities', [])
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate if this agent can handle the given task.
        
        Args:
            task: Task specification
            
        Returns:
            True if agent can handle the task
        """
        task_type = task.get('type')
        return task_type in self.get_capabilities()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of agent execution history.
        
        Returns:
            Summary dictionary
        """
        if not self.execution_history:
            return {
                'agent_name': self.agent_name,
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0
            }
        
        successful = sum(1 for record in self.execution_history 
                        if record['status'] == 'completed')
        failed = sum(1 for record in self.execution_history 
                    if record['status'] == 'failed')
        
        return {
            'agent_name': self.agent_name,
            'total_executions': len(self.execution_history),
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': successful / len(self.execution_history) * 100,
            'last_execution': self.execution_history[-1]['timestamp']
        }