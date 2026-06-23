import time
from datetime import datetime
from typing import Dict, Any, Optional
from app.observability.models import TraceContext, TraceEvent

class Tracer:
    """Manages request tracing and step durations."""
    
    def __init__(self, request_id: str, user_id: Optional[int] = None):
        self.context = TraceContext(request_id=request_id, user_id=user_id)
        self._start_times: Dict[str, float] = {}

    def start_span(self, name: str) -> None:
        """Starts timing a specific execution span (e.g. 'router', 'memory')."""
        self._start_times[name] = time.time()

    def end_span(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Ends the timing for a span and records it to the TraceContext."""
        if name not in self._start_times:
            return
            
        duration_ms = (time.time() - self._start_times[name]) * 1000
        event = TraceEvent(
            event_name=name,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        self.context.events.append(event)
        del self._start_times[name]

    def close(self) -> TraceContext:
        """Finalizes the trace context."""
        self.context.end_time = datetime.utcnow()
        self.context.total_duration_ms = (self.context.end_time - self.context.start_time).total_seconds() * 1000
        return self.context
