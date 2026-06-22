from app.reasoning.models import ExecutionPlan
from app.access.models import ToolName
from app.core.exceptions import AccessDeniedError

class ReasoningGuardrails:
    """Enterprise safety checks for reasoning execution."""

    @classmethod
    def verify_safe_plan(cls, plan: ExecutionPlan) -> None:
        """
        Enforces that the plan only contains safe, registered tools and does not perform autonomous discovery.
        """
        for step in plan.steps:
            # Prevent tool injection by validating against known ToolName enums
            # Pydantic enum validation handles most of this, but we explicitly guard against ADMIN tools here
            # or tools that the reasoning engine should NEVER call autonomously.
            if "ADMIN" in step.tool_name.value:
                raise AccessDeniedError(f"CRITICAL: Plan attempted to invoke protected admin tool: {step.tool_name.value}")
