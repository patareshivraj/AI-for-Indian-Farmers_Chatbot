import time
from typing import Dict
from app.reasoning.models import ExecutionPlan, ReasoningResult
from app.execution.models import ExecutionResult

class ResultSynthesizer:
    """Combines multiple execution results into a unified ReasoningResult."""

    @classmethod
    def synthesize(cls, plan: ExecutionPlan, tool_results: Dict[str, ExecutionResult], execution_time_ms: float) -> ReasoningResult:
        """
        Synthesizes the outputs of multiple tools into a single structured payload.
        """
        success = True
        extracted_data = {}
        steps_executed = len(tool_results)
        
        # If any core step failed, we can mark the overall reasoning as failed or partially failed.
        # For strict deterministic enterprise use, if any step fails, we flag the whole reasoning as failed.
        for tool_name, result in tool_results.items():
            if not result.success:
                success = False
            # Extract inner data dictionary
            extracted_data[tool_name] = result.data if result.success else {"error": result.error}
            
        summary = "Execution completed successfully." if success else "Execution encountered errors in one or more steps."

        return ReasoningResult(
            success=success,
            plan_id=plan.plan_id,
            steps_executed=steps_executed,
            tool_results=extracted_data,
            summary=summary,
            execution_time_ms=execution_time_ms
        )
