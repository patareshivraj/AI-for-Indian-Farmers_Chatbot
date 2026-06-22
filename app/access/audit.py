import logging
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.context.models import RoleEnum
from app.access.models import ToolName

class ToolAccessAuditEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user_id: int
    role: RoleEnum
    tool_name: ToolName
    target_resource: str | None
    allowed: bool
    timestamp: datetime

class AuditLogger:
    """Logs all tool access attempts for compliance and debugging."""
    
    def __init__(self):
        self.logger = logging.getLogger("ToolAccessAudit")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, entry: ToolAccessAuditEntry):
        """Persists the audit entry."""
        status = "GRANTED" if entry.allowed else "DENIED"
        message = (
            f"[{status}] User {entry.user_id} ({entry.role.value}) "
            f"attempted {entry.tool_name.value} "
            f"on resource {entry.target_resource}"
        )
        if entry.allowed:
            self.logger.info(message)
        else:
            self.logger.warning(message)
