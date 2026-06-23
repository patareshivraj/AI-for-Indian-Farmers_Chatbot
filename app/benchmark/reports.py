import json
import os
from typing import Dict, Any

class BenchmarkReporter:
    """Generates Pilot Readiness Reports and Executive Summaries."""

    @classmethod
    def evaluate_readiness(cls, metrics: Dict[str, float]) -> bool:
        """Evaluates against strict readiness gates."""
        if metrics.get("intent_accuracy", 0) < 95.0: return False
        if metrics.get("tool_accuracy", 0) < 95.0: return False
        if metrics.get("memory_resolution_accuracy", 0) < 90.0: return False
        if metrics.get("reasoning_accuracy", 0) < 90.0: return False
        if metrics.get("multilingual_accuracy", 0) < 90.0: return False
        if metrics.get("session_isolation_score", 0) < 100.0: return False
        if metrics.get("pii_leaks", 1) > 0: return False
        if metrics.get("permission_violations", 1) > 0: return False
        if metrics.get("success_rate", 0) < 95.0: return False
        if metrics.get("error_rate", 100) >= 5.0: return False
        return True

    @classmethod
    def generate_json_summary(cls, metrics: Dict[str, float], output_path: str):
        is_ready = cls.evaluate_readiness(metrics)
        
        summary = {
            "overall_status": "PASS" if is_ready else "FAIL",
            "pilot_ready": is_ready,
            "intent_accuracy": metrics.get("intent_accuracy", 0),
            "reasoning_accuracy": metrics.get("reasoning_accuracy", 0),
            "memory_accuracy": metrics.get("memory_resolution_accuracy", 0),
            "security_score": 100 if (metrics.get("pii_leaks", 0) == 0 and metrics.get("permission_violations", 0) == 0) else 0,
            "recommendation": "APPROVED_FOR_PILOT" if is_ready else "REJECTED"
        }
        
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)
            
        return summary

    @classmethod
    def generate_markdown_report(cls, metrics: Dict[str, float], workload_results: Dict[str, Any], output_path: str):
        is_ready = cls.evaluate_readiness(metrics)
        status_text = "✅ APPROVED FOR PILOT" if is_ready else "❌ REJECTED"
        
        report = f"""# Farm360 AI Copilot - Pilot Readiness Report

## Executive Summary
**Status**: {status_text}

## 1. AI Accuracy Results
- **Intent Accuracy**: {metrics.get("intent_accuracy")}%
- **Tool Selection Accuracy**: {metrics.get("tool_accuracy")}%
- **Reasoning Plan Accuracy**: {metrics.get("reasoning_accuracy")}%
- **Entity Extraction**: {metrics.get("entity_extraction_accuracy")}%
- **Multilingual Support**: {metrics.get("multilingual_accuracy")}%

## 2. Context & Memory Results
- **Memory Resolution Accuracy**: {metrics.get("memory_resolution_accuracy")}%
- **Session Isolation Score**: {metrics.get("session_isolation_score")}% (100% required)

## 3. Security Results
- **PII Leaks Detected**: {metrics.get("pii_leaks")}
- **Permission Violations**: {metrics.get("permission_violations")}

## 4. Performance Results (1000 Concurrent Users)
- **Success Rate**: {workload_results.get("success_rate", 100.0):.2f}%
- **Error Rate**: {workload_results.get("error_rate", 0.0):.2f}%
- **Throughput**: {workload_results.get("throughput_rps", 0):.2f} req/s
- **Latency (p50)**: {workload_results.get("p50_latency_ms", 0):.2f} ms
- **Latency (p95)**: {workload_results.get("p95_latency_ms", 0):.2f} ms

## Recommendations
{"The AI Copilot has passed all production gates and is formally certified for pilot deployment to farmers and consultants." if is_ready else "The AI Copilot failed one or more production gates. Remediate issues before deployment."}
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
