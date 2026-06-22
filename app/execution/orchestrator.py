import time
from typing import List, Optional
from app.context.builder import ContextBuilder
from app.router.router import QueryRouter
from app.execution.planner import ExecutionPlanner
from app.execution.executor import ExecutionEngine
from app.execution.models import ExecutionResult

class Farm360Orchestrator:
    """Main entry point for AI Operations. Glues Context -> Router -> Execution."""
    
    def __init__(
        self,
        context_builder: ContextBuilder,
        query_router: QueryRouter,
        execution_planner: ExecutionPlanner,
        execution_engine: ExecutionEngine
    ):
        self.context_builder = context_builder
        self.query_router = query_router
        self.execution_planner = execution_planner
        self.execution_engine = execution_engine

    def run(self, user_id: int, question: str) -> ExecutionResult:
        """Process a question end-to-end and return the execution result."""
        start_time = time.time()
        
        # 1. Build Secure Context
        context = self.context_builder.build(user_id)
        
        # 2. Route Query
        decision = self.query_router.route(question)
        
        # 3. Handle Unknown / Unsupported
        if not decision.tool_name:
            return ExecutionResult(
                success=False,
                intent=decision.intent,
                tool_name=None,
                error="Query not understood or unsupported.",
                execution_time_ms=int((time.time() - start_time) * 1000)
            )
            
        # 4. Plan Execution
        plans = self.execution_planner.create_plan(decision)
        
        # 5. Execute Tools
        results = self.execution_engine.execute(plans, context)
        
        # For V1, we only have one plan per decision, so return the first result
        final_result = results[0] if results else ExecutionResult(
            success=False,
            intent=decision.intent,
            tool_name=decision.tool_name,
            error="No execution results produced.",
            execution_time_ms=int((time.time() - start_time) * 1000)
        )
        
        # Append full orchestrator duration to the final result (or modify it)
        # Note: final_result.execution_time_ms is just the tool/agent time.
        # We can leave it as tool execution time or update to full request time.
        
        return final_result
