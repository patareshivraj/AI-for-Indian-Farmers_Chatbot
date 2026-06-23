from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_name: str
    duration_ms: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TraceContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: str
    user_id: Optional[int] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_duration_ms: float = 0.0
    events: List[TraceEvent] = Field(default_factory=list)

class LogLevel(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class StructuredLog(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
    level: LogLevel
    message: str
    user_id: Optional[int] = None
    intent: Optional[str] = None
    tool: Optional[str] = None
    latency_ms: Optional[float] = None
    status: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AlertSeverity(str, Enum):
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class SystemAlert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alert_id: str
    severity: AlertSeverity
    rule_name: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
