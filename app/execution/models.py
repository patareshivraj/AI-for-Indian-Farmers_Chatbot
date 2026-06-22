from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from app.router.intents import Intent
from app.access.models import ToolName

class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intent: Intent
    tool_name: Optional[ToolName]
    parameters: Dict[str, Any]
    requires_context: bool = True
    requires_permissions: bool = True
    priority: int = 1

class ExecutionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    intent: Intent
    tool_name: Optional[ToolName]
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ExecutionTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_name: str
    tool_name: Optional[ToolName]
    intent: Intent
    success: bool
    execution_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
