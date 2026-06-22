from typing import List
from app.router.models import RoutingDecision
from app.execution.models import ExecutionPlan

class ExecutionPlanner:
    """Converts a routing decision into an ordered list of Execution Plans."""

    def create_plan(self, decision: RoutingDecision) -> List[ExecutionPlan]:
        # Future-proofing: In V1, we simply map 1-to-1.
        # In later phases, we could break down complex intents into multiple plans.
        
        # If UNKNOWN intent, return empty plan
        if not decision.tool_name:
            return []
            
        plan = ExecutionPlan(
            intent=decision.intent,
            tool_name=decision.tool_name,
            parameters=decision.parameters,
            requires_context=True,
            requires_permissions=True,
            priority=1
        )
        
        return [plan]
