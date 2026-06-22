import time
from typing import List
from app.context.models import UserContext
from app.execution.models import ExecutionPlan, ExecutionResult, ExecutionTrace
from app.execution.resolver import AgentResolver
from app.execution.errors import AgentExecutionError

class ExecutionEngine:
    """Executes a list of plans sequentially and tracks metrics."""
    
    def __init__(self, agent_resolver: AgentResolver):
        self.agent_resolver = agent_resolver
        self.traces: List[ExecutionTrace] = []

    def execute(self, plans: List[ExecutionPlan], context: UserContext) -> List[ExecutionResult]:
        results = []
        
        for plan in sorted(plans, key=lambda x: x.priority):
            agent = self.agent_resolver.resolve(plan.intent)
            
            if not agent:
                error_msg = f"No agent found to handle intent {plan.intent.value}"
                result = ExecutionResult(
                    success=False,
                    intent=plan.intent,
                    tool_name=plan.tool_name,
                    error=error_msg,
                    execution_time_ms=0
                )
                self._record_trace("None", plan, result)
                results.append(result)
                continue
                
            try:
                result = agent.execute(plan, context)
            except Exception as e:
                result = ExecutionResult(
                    success=False,
                    intent=plan.intent,
                    tool_name=plan.tool_name,
                    error=f"Engine execution failure: {str(e)}",
                    execution_time_ms=0
                )
                
            self._record_trace(agent.__class__.__name__, plan, result)
            results.append(result)
            
        return results
        
    def _record_trace(self, agent_name: str, plan: ExecutionPlan, result: ExecutionResult):
        trace = ExecutionTrace(
            agent_name=agent_name,
            tool_name=plan.tool_name,
            intent=plan.intent,
            success=result.success,
            execution_time_ms=result.execution_time_ms
        )
        self.traces.append(trace)
