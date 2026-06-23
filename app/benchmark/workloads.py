import asyncio
import time
import random
import statistics
from typing import Dict, Any, List
from app.observability.middleware import ObservabilityMiddleware
from app.router.models import RoutingDecision
from app.router.intents import Intent
from app.execution.models import ExecutionResult

class WorkloadSimulator:
    """Simulates high-concurrency workloads for benchmarking."""
    
    @classmethod
    async def simulate_concurrency(cls, handler, concurrent_users: int, duration_seconds: int = 5) -> Dict[str, Any]:
        start_time = time.time()
        latencies = []
        failures = 0
        total_requests = 0

        async def worker():
            nonlocal total_requests, failures
            while time.time() - start_time < duration_seconds:
                req_start = time.time()
                try:
                    # In a real benchmark this would pull from the dataset
                    ObservabilityMiddleware.process_request(
                        request_data={"query": "benchmark test"}, 
                        handler=handler, 
                        user_id=random.randint(10001, 11000)
                    )
                    latencies.append((time.time() - req_start) * 1000)
                except Exception:
                    failures += 1
                total_requests += 1

        tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]
        await asyncio.gather(*tasks)
        
        success_rate = ((total_requests - failures) / total_requests) * 100 if total_requests else 0
        p50 = statistics.median(latencies) if latencies else 0
        p95 = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 2 else p50
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 2 else p50
        
        return {
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "success_rate": success_rate,
            "error_rate": 100 - success_rate,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "p99_latency_ms": p99,
            "throughput_rps": total_requests / duration_seconds
        }
