import pytest
from app.router.intents import Intent
from app.access.models import ToolName
from app.router.models import RoutingDecision
from app.context.models import UserContext, BaseUser, Permissions, RoleEnum
from app.reasoning.models import ExecutionPlan, PlanStep
from app.reasoning.planner import ReasoningPlanner
from app.reasoning.validator import PlanValidator, PlanValidationError
from app.reasoning.guardrails import ReasoningGuardrails
from app.reasoning.executor import ReasoningExecutor
from app.reasoning.engine import ReasoningEngine
from app.execution.executor import ExecutionEngine
from app.execution.models import ExecutionResult
from app.core.exceptions import AccessDeniedError
from unittest.mock import Mock

def test_planner_creates_single_step():
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={"crop": "soybean"}, confidence=1.0)
    plan = ReasoningPlanner.create_plan(decision)
    
    assert len(plan.steps) == 1
    assert plan.steps[0].tool_name == ToolName.GET_MARKET_PRICES
    assert plan.steps[0].parameters == {"crop": "soybean"}

def test_planner_creates_composite_step():
    decision = RoutingDecision(intent=Intent.SCHEME_ELIGIBILITY_QUERY, tool_name=None, parameters={"state": "MH"}, confidence=1.0)
    plan = ReasoningPlanner.create_plan(decision)
    
    assert len(plan.steps) == 3
    assert plan.steps[0].tool_name == ToolName.GET_MY_PROFILE
    assert plan.steps[2].tool_name == ToolName.SEARCH_SCHEMES
    assert plan.steps[2].depends_on == [1, 2]
    assert plan.steps[2].parameters == {"state": "MH"} # Injected context

def test_validator_rejects_empty_plan():
    plan = ExecutionPlan(plan_id="123", intent=Intent.MARKET_QUERY, steps=[])
    with pytest.raises(PlanValidationError):
        PlanValidator.validate(plan)

def test_validator_rejects_circular_dependency():
    steps = [
        PlanStep(step_id=1, tool_name=ToolName.GET_MARKET_PRICES, depends_on=[2]),
        PlanStep(step_id=2, tool_name=ToolName.GET_WEATHER, depends_on=[1])
    ]
    plan = ExecutionPlan(plan_id="123", intent=Intent.FARM_HEALTH_QUERY, steps=steps)
    with pytest.raises(PlanValidationError, match="circular dependencies"):
        PlanValidator.validate(plan)

def test_guardrails_blocks_admin_tools():
    # Mocking step to bypass Pydantic enum validation for testing guardrail logic
    step = Mock()
    step.tool_name.value = "ADMIN_DELETE_DATABASE"
    plan = ExecutionPlan(plan_id="123", intent=Intent.MARKET_QUERY, steps=[])
    plan.steps = [step]
    with pytest.raises(AccessDeniedError, match="ADMIN"):
        ReasoningGuardrails.verify_safe_plan(plan)

def test_reasoning_executor_aborts_on_dependency_failure():
    mock_phase5_engine = Mock()
    mock_phase5_engine.execute.return_value = [ExecutionResult(success=False, intent=Intent.PROFILE_QUERY, tool_name=ToolName.GET_MY_PROFILE, error="Failed", execution_time_ms=0)]
    
    executor = ReasoningExecutor(mock_phase5_engine)
    plan = ExecutionPlan(
        plan_id="1",
        intent=Intent.SCHEME_ELIGIBILITY_QUERY,
        steps=[
            PlanStep(step_id=1, tool_name=ToolName.GET_MY_PROFILE),
            PlanStep(step_id=2, tool_name=ToolName.SEARCH_SCHEMES, depends_on=[1])
        ]
    )
    
    user = BaseUser(user_id=1, role=RoleEnum.FARMER, name="Test")
    perms = Permissions()
    ctx = UserContext(user=user, permissions=perms)
    
    results = executor.execute(plan, ctx)
    
    # SEARCH_SCHEMES should fail automatically because step 1 failed, without being sent to Phase 5 engine
    assert results[ToolName.SEARCH_SCHEMES.value].success is False
    assert results[ToolName.SEARCH_SCHEMES.value].error == "Dependency step failed."
    assert mock_phase5_engine.execute.call_count == 1 # Only called for step 1

def test_reasoning_engine_e2e_success():
    mock_phase5_engine = Mock()
    mock_phase5_engine.execute.return_value = [ExecutionResult(success=True, intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, data={"price": 100}, execution_time_ms=10)]
    
    engine = ReasoningEngine(ReasoningExecutor(mock_phase5_engine))
    decision = RoutingDecision(intent=Intent.MARKET_QUERY, tool_name=ToolName.GET_MARKET_PRICES, parameters={}, confidence=1.0)
    
    user = BaseUser(user_id=1, role=RoleEnum.FARMER, name="Test")
    perms = Permissions()
    ctx = UserContext(user=user, permissions=perms)
    
    result = engine.process(decision, ctx)
    assert result.success is True
    assert result.steps_executed == 1
    assert result.tool_results[ToolName.GET_MARKET_PRICES.value] == {"price": 100}
