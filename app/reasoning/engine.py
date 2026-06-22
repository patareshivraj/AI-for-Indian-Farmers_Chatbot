import time
from app.router.models import RoutingDecision
from app.context.models import UserContext
from app.reasoning.models import ReasoningResult
from app.reasoning.planner import ReasoningPlanner
from app.reasoning.validator import PlanValidator
from app.reasoning.guardrails import ReasoningGuardrails
from app.reasoning.executor import ReasoningExecutor
from app.reasoning.synthesizer import ResultSynthesizer

class ReasoningEngine:
    """Master facade for the Phase 8 Advanced Reasoning Layer."""

    def __init__(self, executor: ReasoningExecutor):
        self.executor = executor

    def process(self, decision: RoutingDecision, context: UserContext) -> ReasoningResult:
        """
        Executes the full reasoning pipeline: Plan -> Validate -> Execute -> Synthesize
        """
        start_time = time.time()
        
        # 1. Create Execution Plan
        plan = ReasoningPlanner.create_plan(decision)
        
        if not plan.steps:
            return ReasoningResult(
                success=False,
                plan_id=plan.plan_id,
                steps_executed=0,
                tool_results={},
                summary="No plan could be generated for the given intent.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        # 2. Guardrails & Validation
        try:
            ReasoningGuardrails.verify_safe_plan(plan)
            PlanValidator.validate(plan)
        except Exception as e:
            return ReasoningResult(
                success=False,
                plan_id=plan.plan_id,
                steps_executed=0,
                tool_results={},
                summary=f"Plan validation failed: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )

        # 3. Execute
        tool_results = self.executor.execute(plan, context)
        
        # 4. Synthesize
        total_time_ms = int((time.time() - start_time) * 1000)
        return ResultSynthesizer.synthesize(plan, tool_results, execution_time_ms=total_time_ms)
