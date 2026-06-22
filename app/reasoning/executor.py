import time
from typing import Dict, Any
from app.reasoning.models import ExecutionPlan, PlanStep
from app.context.models import UserContext
from app.execution.executor import ExecutionEngine
from app.execution.models import ExecutionPlan as Phase5ExecutionPlan
from app.execution.models import ExecutionResult

class ReasoningExecutor:
    """Executes a multi-step deterministic plan."""

    def __init__(self, engine: ExecutionEngine):
        self.engine = engine

    def execute(self, plan: ExecutionPlan, context: UserContext) -> Dict[str, ExecutionResult]:
        """
        Executes the plan steps in dependency order.
        Returns a dictionary of step_id -> ExecutionResult.
        """
        results: Dict[int, ExecutionResult] = {}
        
        # Sort steps by ID initially, but we should respect depends_on.
        # Since validator ensures no cycles, we can iteratively execute steps that have their dependencies met.
        pending_steps = list(plan.steps)
        completed_step_ids = set()
        
        while pending_steps:
            # Find a step whose dependencies are all met
            executable_step = None
            for step in pending_steps:
                if all(dep in completed_step_ids for dep in step.depends_on):
                    executable_step = step
                    break
                    
            if not executable_step:
                # This should not happen if validation passed, but just in case
                break
                
            # Check if any dependencies actually failed. If so, abort this step and mark as failed.
            dep_failed = False
            for dep in executable_step.depends_on:
                if not results[dep].success:
                    dep_failed = True
                    break
                    
            if dep_failed:
                results[executable_step.step_id] = ExecutionResult(
                    success=False,
                    intent=plan.intent,
                    tool_name=executable_step.tool_name,
                    error="Dependency step failed.",
                    execution_time_ms=0
                )
            else:
                # Execute using Phase 5 ExecutionEngine
                # Convert Phase 8 PlanStep to Phase 5 ExecutionPlan
                p5_plan = Phase5ExecutionPlan(
                    intent=plan.intent,
                    tool_name=executable_step.tool_name,
                    parameters=executable_step.parameters,
                    priority=executable_step.priority
                )
                
                # ExecutionEngine takes a list of plans
                p5_results = self.engine.execute([p5_plan], context)
                
                if p5_results:
                    results[executable_step.step_id] = p5_results[0]
                else:
                    results[executable_step.step_id] = ExecutionResult(
                        success=False,
                        intent=plan.intent,
                        tool_name=executable_step.tool_name,
                        error="Execution engine returned no result.",
                        execution_time_ms=0
                    )
            
            completed_step_ids.add(executable_step.step_id)
            pending_steps.remove(executable_step)

        # Convert keys from step_id to tool_name string representation for easier synthesis
        tool_results = {str(plan.steps[i].tool_name.value): res for i, res in enumerate(results.values()) if i < len(plan.steps)}
        return tool_results
