from typing import Dict, Any
from app.observability.metrics import metrics
from app.observability.alerts import alert_manager

class ProductionDashboard:
    """Aggregates metrics and alerts for the /dashboard endpoint."""

    @classmethod
    def get_dashboard_data(cls) -> Dict[str, Any]:
        """Returns JSON representation of system state."""
        
        # In a real system, metrics would be fetched from Prometheus API.
        # Here we read our in-memory metrics.
        total_reqs = metrics._counters.get("farm360_requests_total", 0)
        success_reqs = metrics._counters.get("farm360_requests_success_total", 0)
        error_reqs = metrics._counters.get("farm360_requests_error_total", 0)
        
        error_rate = (error_reqs / total_reqs * 100) if total_reqs > 0 else 0.0
        
        return {
            "traffic": {
                "total_requests": total_reqs,
                "error_rate_percentage": round(error_rate, 2),
            },
            "performance": {
                "latency_p50_ms": round(metrics.calculate_percentile("farm360_latency_ms", 50), 2),
                "latency_p95_ms": round(metrics.calculate_percentile("farm360_latency_ms", 95), 2),
                "latency_p99_ms": round(metrics.calculate_percentile("farm360_latency_ms", 99), 2),
            },
            "ai_metrics": {
                intent.replace("farm360_intent_", "").replace("_total", ""): count 
                for intent, count in metrics._counters.items() if "farm360_intent_" in intent
            },
            "security": {
                "denied_requests": metrics._counters.get("farm360_security_denials_total", 0),
                "blocked_pii": metrics._counters.get("farm360_security_pii_blocks_total", 0)
            },
            "active_alerts": [
                {
                    "rule": a.rule_name,
                    "severity": a.severity.value,
                    "message": a.message
                } for a in alert_manager.get_active_alerts()
            ]
        }
