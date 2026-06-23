import time
import uuid
from typing import Callable, Any, Optional
from app.observability.logger import logger, LogLevel
from app.observability.tracer import Tracer
from app.observability.metrics import metrics

class ObservabilityMiddleware:
    """Wraps requests to provide end-to-end tracing, metrics, and structured logging."""

    @classmethod
    def process_request(cls, request_data: dict, handler: Callable[..., Any], user_id: Optional[int] = None) -> Any:
        request_id = f"req_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        tracer = Tracer(request_id=request_id, user_id=user_id)
        tracer.start_span("total_request")
        
        metrics.inc_counter("farm360_requests_total")
        
        status = "success"
        error_msg = None
        result = None
        intent_name = None
        
        try:
            # We inject tracer into kwargs if handler needs it, or use contextvars in a real app
            result = handler(request_data, tracer=tracer)
            
            # Extract intent from result if possible (assumes ReasoningResult or ExecutionResult)
            if hasattr(result, "success") and not result.success:
                status = "error"
                metrics.inc_counter("farm360_requests_error_total")
                if hasattr(result, "error"):
                    error_msg = result.error
            else:
                metrics.inc_counter("farm360_requests_success_total")
                
            if hasattr(result, "intent"):
                intent_name = result.intent.value
                metrics.inc_counter(f"farm360_intent_{intent_name}_total")
                
        except Exception as e:
            status = "error"
            error_msg = str(e)
            metrics.inc_counter("farm360_requests_error_total")
            raise e
        finally:
            tracer.end_span("total_request")
            trace_ctx = tracer.close()
            
            metrics.observe_latency("farm360_latency_ms", trace_ctx.total_duration_ms)
            
            log_level = LogLevel.ERROR if status == "error" else LogLevel.INFO
            logger.log(
                level=log_level,
                request_id=request_id,
                message=f"Request completed with status: {status}",
                user_id=user_id,
                intent=intent_name,
                latency_ms=trace_ctx.total_duration_ms,
                status=status,
                metadata={
                    "error": error_msg,
                    "traces": [t.model_dump() for t in trace_ctx.events]
                }
            )
            
        return result
