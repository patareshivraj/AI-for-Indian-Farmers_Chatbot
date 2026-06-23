import json
import logging
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from app.observability.models import StructuredLog, LogLevel

class StructuredLogger:
    """Provides JSON structured logging with strict PII sanitization."""

    SENSITIVE_KEYS = {
        "password", "adhar", "aadhar", "adhar_no", "aadhar_no", 
        "pan", "pan_no", "jwt", "token", "secret", "credentials", 
        "property_uid", "api_key", "database_url"
    }

    def __init__(self, name: str = "farm360"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @classmethod
    def sanitize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts sensitive information before logging."""
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, dict):
                sanitized[k] = cls.sanitize(v)
            elif any(s in k.lower() for s in cls.SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = v
        return sanitized

    def log(
        self,
        level: LogLevel,
        request_id: str,
        message: str,
        user_id: Optional[int] = None,
        intent: Optional[str] = None,
        tool: Optional[str] = None,
        latency_ms: Optional[float] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        log_entry = StructuredLog(
            request_id=request_id,
            level=level,
            message=message,
            user_id=user_id,
            intent=intent,
            tool=tool,
            latency_ms=latency_ms,
            status=status,
            metadata=self.sanitize(metadata or {})
        )
        
        # We output JSON format natively
        log_json = log_entry.model_dump_json()
        
        if level == LogLevel.INFO:
            self.logger.info(log_json)
        elif level == LogLevel.WARN:
            self.logger.warning(log_json)
        elif level == LogLevel.ERROR:
            self.logger.error(log_json)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(log_json)

# Global Instance
logger = StructuredLogger()
