import time
from app.execution.agents.base import BaseAgent
from app.execution.models import ExecutionPlan, ExecutionResult
from app.router.intents import Intent
from app.context.models import UserContext
from app.tools.registry import ExecutableToolRegistry

class SchemeAgent(BaseAgent):
    
    _supported_intents = {
        Intent.SCHEME_QUERY
    }

    def __init__(self, tool_registry: ExecutableToolRegistry):
        self.tool_registry = tool_registry

    def can_handle(self, intent: Intent) -> bool:
        return intent in self._supported_intents

    def execute(self, plan: ExecutionPlan, context: UserContext) -> ExecutionResult:
        start_time = time.time()
        
        if not plan.tool_name:
            return ExecutionResult(
                success=False,
                intent=plan.intent,
                tool_name=None,
                error="SchemeAgent requires a tool_name to execute.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        try:
            tool = self.tool_registry.get_tool(plan.tool_name)
            result = tool.execute(context, **plan.parameters)
            
            return ExecutionResult(
                success=result.success,
                intent=plan.intent,
                tool_name=plan.tool_name,
                data=result.data,
                error=result.message if not result.success else None,
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                intent=plan.intent,
                tool_name=plan.tool_name,
                error=f"Scheme retrieval failed: {str(e)}",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
