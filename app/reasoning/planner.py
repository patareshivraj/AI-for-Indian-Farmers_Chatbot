import uuid
from app.router.models import RoutingDecision
from app.router.intents import Intent
from app.access.models import ToolName
from app.reasoning.models import ExecutionPlan, PlanStep

class ReasoningPlanner:
    """Creates deterministic execution plans based on routing intent."""

    # Map composite intents to a predefined multi-step sequence
    COMPOSITE_TEMPLATES = {
        Intent.SCHEME_ELIGIBILITY_QUERY: [
            PlanStep(step_id=1, tool_name=ToolName.GET_MY_PROFILE, parameters={}),
            PlanStep(step_id=2, tool_name=ToolName.GET_MY_LAND_RECORDS, parameters={}),
            PlanStep(step_id=3, tool_name=ToolName.SEARCH_SCHEMES, parameters={}, depends_on=[1, 2])
        ],
        Intent.FARM_HEALTH_QUERY: [
            PlanStep(step_id=1, tool_name=ToolName.GET_MY_ACTIVE_CROPS, parameters={}),
            PlanStep(step_id=2, tool_name=ToolName.GET_WEATHER, parameters={}, depends_on=[1]),
            PlanStep(step_id=3, tool_name=ToolName.GET_MY_INVENTORY, parameters={})
        ],
        Intent.CROP_PLANNING_QUERY: [
            PlanStep(step_id=1, tool_name=ToolName.GET_MARKET_PRICES, parameters={}),
            PlanStep(step_id=2, tool_name=ToolName.GET_WEATHER, parameters={}),
            PlanStep(step_id=3, tool_name=ToolName.GET_MY_LAND_RECORDS, parameters={})
        ]
    }

    @classmethod
    def create_plan(cls, decision: RoutingDecision) -> ExecutionPlan:
        """
        Generates an execution plan from the initial routing decision.
        If it's a standard single tool query, generates a 1-step plan.
        If it's a composite query, generates the multi-step plan.
        """
        plan_id = str(uuid.uuid4())
        
        if decision.intent in cls.COMPOSITE_TEMPLATES:
            # Multi-tool composite query
            template_steps = cls.COMPOSITE_TEMPLATES[decision.intent]
            # Copy template to avoid mutation, inject base parameters if needed
            steps = []
            for t_step in template_steps:
                new_step = PlanStep(
                    step_id=t_step.step_id,
                    tool_name=t_step.tool_name,
                    parameters=decision.parameters.copy(), # Pass original extracted parameters (like crop_name)
                    depends_on=t_step.depends_on,
                    priority=t_step.priority
                )
                steps.append(new_step)
        elif decision.tool_name:
            # Single tool query
            steps = [
                PlanStep(
                    step_id=1,
                    tool_name=decision.tool_name,
                    parameters=decision.parameters
                )
            ]
        else:
            # Unknown intent or no tool matched
            steps = []

        return ExecutionPlan(
            plan_id=plan_id,
            intent=decision.intent,
            steps=steps
        )
