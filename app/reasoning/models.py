from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.router.intents import Intent
from app.access.models import ToolName

class PlanStep(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step_id: int
    tool_name: ToolName
    parameters: Dict[str, Any] = Field(default_factory=dict)
    depends_on: List[int] = Field(default_factory=list)
    priority: int = 1

class ExecutionPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_id: str
    intent: Intent
    steps: List[PlanStep]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReasoningResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    success: bool
    plan_id: str
    steps_executed: int
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    summary: Optional[str] = None
    execution_time_ms: float
