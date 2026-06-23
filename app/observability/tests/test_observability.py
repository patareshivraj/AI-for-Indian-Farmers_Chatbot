import pytest
import time
from app.observability.logger import StructuredLogger, LogLevel
from app.observability.tracer import Tracer
from app.observability.metrics import MetricsCollector
from app.observability.alerts import AlertManager
from app.observability.models import AlertSeverity

def test_logger_sanitizes_pii():
    data = {
        "user_input": "My aadhaar is 1234-5678-9012",
        "aadhar": "1234-5678-9012",
        "pan_no": "ABCDE1234F",
        "nested": {
            "password": "supersecret"
        },
        "safe_key": "safe_value"
    }
    sanitized = StructuredLogger.sanitize(data)
    
    assert sanitized["aadhar"] == "[REDACTED]"
    assert sanitized["pan_no"] == "[REDACTED]"
    assert sanitized["nested"]["password"] == "[REDACTED]"
    assert sanitized["safe_key"] == "safe_value"
    # Note: Text scanning for PII inside strings is usually handled by the Regex/Security layer,
    # The logger sanitizes explicitly known sensitive keys to prevent accidental leaks.

def test_tracer_records_durations():
    tracer = Tracer(request_id="test-123")
    tracer.start_span("db_query")
    time.sleep(0.01) # 10ms
    tracer.end_span("db_query", metadata={"rows": 5})
    
    ctx = tracer.close()
    
    assert len(ctx.events) == 1
    assert ctx.events[0].event_name == "db_query"
    assert ctx.events[0].duration_ms >= 10.0
    assert ctx.total_duration_ms >= 10.0

def test_metrics_collector():
    metrics = MetricsCollector()
    metrics.inc_counter("requests", 1)
    metrics.inc_counter("requests", 2)
    
    metrics.observe_latency("latency", 50.0)
    metrics.observe_latency("latency", 100.0)
    metrics.observe_latency("latency", 150.0)
    
    assert metrics._counters["requests"] == 3
    assert metrics.calculate_percentile("latency", 50) == 100.0
    assert metrics.calculate_percentile("latency", 99) == 150.0
    
    prom_output = metrics.export_prometheus()
    assert "TYPE requests counter" in prom_output
    assert "requests 3" in prom_output
    assert 'latency{quantile="0.5"} 100.0' in prom_output

def test_alert_manager_thresholds():
    manager = AlertManager()
    
    # Test high latency warning
    manager.check_thresholds({"p95_latency": 2500.0})
    assert len(manager.active_alerts) == 1
    assert manager.active_alerts[0].rule_name == "HIGH_LATENCY"
    
    # Test error rate > 5% (with enough volume)
    manager.check_thresholds({
        "farm360_requests_success_total": 40,
        "farm360_requests_error_total": 11 # 11/51 = > 20%
    })
    
    assert len(manager.active_alerts) == 2
    assert manager.active_alerts[1].rule_name == "HIGH_ERROR_RATE"
