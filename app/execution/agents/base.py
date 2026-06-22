from abc import ABC, abstractmethod
from typing import Optional
from app.context.models import UserContext
from app.router.intents import Intent
from app.execution.models import ExecutionPlan, ExecutionResult

class BaseAgent(ABC):
    
    @abstractmethod
    def can_handle(self, intent: Intent) -> bool:
        """Determines if the agent can handle the specific intent."""
        pass
        
    @abstractmethod
    def execute(self, plan: ExecutionPlan, context: UserContext) -> ExecutionResult:
        """Executes the plan safely within the given context."""
        pass
