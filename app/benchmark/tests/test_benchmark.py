import pytest
import os
import asyncio
from app.benchmark.personas import PersonaGenerator
from app.context.models import RoleEnum
from app.benchmark.workloads import WorkloadSimulator
from app.benchmark.metrics import BenchmarkMetrics
from app.benchmark.reports import BenchmarkReporter
from app.router.intents import Intent

@pytest.mark.asyncio
async def test_high_concurrency_workload():
    # Simulate a lightweight handler that just returns success
    def mock_handler(req, tracer=None):
        return type("Result", (), {"success": True, "intent": Intent.MARKET_QUERY})()
        
    results = await WorkloadSimulator.simulate_concurrency(mock_handler, concurrent_users=1000, duration_seconds=2)
    
    assert results["success_rate"] >= 95.0
    assert results["p95_latency_ms"] < 2000.0

def test_persona_generation():
    farmers = PersonaGenerator.generate_personas(RoleEnum.FARMER, 100)
    assert len(farmers) == 100
    assert "farm_size" in farmers[0]
    assert "crop_types" in farmers[0]
    
    consultants = PersonaGenerator.generate_personas(RoleEnum.CONSULTANT, 50)
    assert len(consultants) == 50
    assert "consultant_specialization" in consultants[0]

def test_benchmark_metrics_and_reporting():
    workload_results = {
        "concurrent_users": 1000,
        "success_rate": 99.5,
        "error_rate": 0.5,
        "p50_latency_ms": 150.0,
        "p95_latency_ms": 350.0,
        "throughput_rps": 500.0
    }
    
    suite_metrics = BenchmarkMetrics.compute_suite_metrics(workload_results)
    assert suite_metrics["intent_accuracy"] == 100.0
    
    output_dir = os.path.dirname(__file__)
    json_path = os.path.join(output_dir, "..", "benchmark_summary.json")
    md_path = os.path.join(output_dir, "..", "pilot_readiness_report.md")
    
    summary = BenchmarkReporter.generate_json_summary(suite_metrics, json_path)
    assert summary["pilot_ready"] is True
    assert summary["recommendation"] == "APPROVED_FOR_PILOT"
    
    BenchmarkReporter.generate_markdown_report(suite_metrics, workload_results, md_path)
    
    assert os.path.exists(json_path)
    assert os.path.exists(md_path)
