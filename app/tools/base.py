from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.access.models import ToolName
from app.context.models import UserContext
from app.access.guard import ToolExecutionGuard
from app.access.registry import ToolMetadata, ToolRegistry as AccessRegistry

class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    data: Optional[Any] = None
    message: str = ""
    source: str
    tool_name: ToolName
    timestamp: datetime

class BaseTool(ABC):
    
    def __init__(self, guard: ToolExecutionGuard, db_session=None):
        self.guard = guard
        self.db_session = db_session

    @property
    @abstractmethod
    def tool_name(self) -> ToolName:
        pass

    def get_metadata(self) -> ToolMetadata:
        return AccessRegistry.get_metadata(self.tool_name)

    def validate_access(self, context: UserContext, target_farmer_id: Optional[int] = None):
        self.guard.validate(context, self.tool_name, target_farmer_id)

    @abstractmethod
    def execute(self, context: UserContext, **kwargs) -> ToolResult:
        pass
