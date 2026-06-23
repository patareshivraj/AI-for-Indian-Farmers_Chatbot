import uuid
from typing import Dict, Any, List
from app.observability.models import SystemAlert, AlertSeverity
from app.observability.logger import logger, LogLevel

class AlertManager:
    """Manages active alerts and thresholds."""
    
    def __init__(self):
        self.active_alerts: List[SystemAlert] = []

    def trigger_alert(self, severity: AlertSeverity, rule_name: str, message: str, metadata: Dict[str, Any] = None):
        alert = SystemAlert(
            alert_id=str(uuid.uuid4()),
            severity=severity,
            rule_name=rule_name,
            message=message,
            metadata=metadata or {}
        )
        self.active_alerts.append(alert)
        
        # Log critical alerts immediately
        log_level = LogLevel.CRITICAL if severity == AlertSeverity.CRITICAL else LogLevel.WARN
        logger.log(
            level=log_level,
            request_id="SYSTEM",
            message=f"ALERT [{rule_name}]: {message}",
            metadata=metadata
        )

    def check_thresholds(self, metrics: Dict[str, float]):
        """Evaluates thresholds based on current metrics."""
        
        # P95 > 2s
        if metrics.get("p95_latency", 0) > 2000:
            self.trigger_alert(AlertSeverity.WARNING, "HIGH_LATENCY", "p95 latency exceeded 2000ms")
            
        # Error Rate > 5%
        successes = metrics.get("farm360_requests_success_total", 0)
        failures = metrics.get("farm360_requests_error_total", 0)
        total = successes + failures
        if total > 50: # Only alert if we have enough sample size
            error_rate = (failures / total) * 100
            if error_rate > 5.0:
                self.trigger_alert(AlertSeverity.WARNING, "HIGH_ERROR_RATE", f"Error rate is {error_rate:.1f}%")

    def get_active_alerts(self) -> List[SystemAlert]:
        return self.active_alerts

# Global Instance
alert_manager = AlertManager()
