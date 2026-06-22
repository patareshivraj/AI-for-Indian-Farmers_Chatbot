from typing import Optional
from datetime import datetime

from app.core.exceptions import AccessDeniedError
from app.context.models import UserContext
from app.access.models import ToolName
from app.access.resolver import ToolAccessResolver
from app.access.ownership import OwnershipValidator
from app.access.registry import ToolRegistry
from app.access.audit import AuditLogger, ToolAccessAuditEntry

class ToolExecutionGuard:
    """Final authorization layer before tool execution."""

    def __init__(self):
        self.resolver = ToolAccessResolver()
        self.ownership_validator = OwnershipValidator()
        self.audit_logger = AuditLogger()

    def validate(self, context: UserContext, tool_name: ToolName, target_farmer_id: Optional[int] = None) -> None:
        """
        Validates if the user can execute the tool.
        Raises AccessDeniedError if unauthorized.
        """
        profile = self.resolver.resolve(context)
        metadata = ToolRegistry.get_metadata(tool_name)
        
        # 1. Check Tool Allowlist
        is_tool_allowed = tool_name in profile.allowed_tools
        
        # 2. Check Ownership Bounds
        is_ownership_valid = self.ownership_validator.validate(profile, target_farmer_id)
        
        # 3. Check Metadata specific constraints
        if metadata.requires_assignment_validation and target_farmer_id is not None:
            if target_farmer_id not in profile.accessible_farmer_ids:
                is_ownership_valid = False
                
        if metadata.requires_farmer_context and target_farmer_id is not None:
            if target_farmer_id not in profile.accessible_farmer_ids:
                is_ownership_valid = False

        allowed = is_tool_allowed and is_ownership_valid

        # Audit
        audit_entry = ToolAccessAuditEntry(
            user_id=context.user.user_id,
            role=context.user.role,
            tool_name=tool_name,
            target_resource=str(target_farmer_id) if target_farmer_id else "Global",
            allowed=allowed,
            timestamp=datetime.utcnow()
        )
        self.audit_logger.log(audit_entry)

        if not allowed:
            reason = "Tool not allowed" if not is_tool_allowed else "Unauthorized farmer access"
            raise AccessDeniedError(
                f"Access denied for User {context.user.user_id} executing {tool_name.value}. Reason: {reason}"
            )
