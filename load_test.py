import asyncio
import time
import random
import statistics
from typing import Dict, List
from app.observability.middleware import ObservabilityMiddleware
from app.router.models import RoutingDecision
from app.router.intents import Intent
from app.access.models import ToolName

# Mock Handler to simulate backend load
def mock_handler(request_data: dict, tracer=None) -> Dict:
    # Simulate DB/LLM I/O
    if tracer:
        tracer.start_span("mock_processing")
    
    time.sleep(random.uniform(0.05, 0.2)) # 50-200ms processing
    
    # Simulate 2% failure rate
    if random.random() < 0.02:
        raise Exception("Mock simulated DB timeout")
        
    if tracer:
        tracer.end_span("mock_processing")
        
    return {"success": True, "intent": Intent.MARKET_QUERY}

async def run_scenario(concurrent_users: int, duration_seconds: int = 5):
    print(f"\n--- Running Load Test Scenario: {concurrent_users} Concurrent Users ---")
    
    start_time = time.time()
    latencies = []
    failures = 0
    total_requests = 0

    async def worker():
        nonlocal total_requests, failures
        while time.time() - start_time < duration_seconds:
            req_start = time.time()
            try:
                # Wrap handler via middleware to simulate full pipeline
                ObservabilityMiddleware.process_request(
                    request_data={"query": "hello"}, 
                    handler=mock_handler, 
                    user_id=random.randint(1, 1000)
                )
                latencies.append((time.time() - req_start) * 1000)
            except Exception:
                failures += 1
            total_requests += 1

    tasks = [asyncio.create_task(worker()) for _ in range(concurrent_users)]
    await asyncio.gather(*tasks)
    
    success_rate = ((total_requests - failures) / total_requests) * 100 if total_requests else 0
    p95 = statistics.quantiles(latencies, n=100)[94] if latencies else 0
    
    print(f"Total Requests: {total_requests}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Failure Rate: {100 - success_rate:.2f}%")
    print(f"p50 Latency: {statistics.median(latencies) if latencies else 0:.2f}ms")
    print(f"p95 Latency: {p95:.2f}ms")
    print(f"Throughput: {total_requests / duration_seconds:.2f} req/s")

async def main():
    print("Initializing Farm360 Load Test Suite...")
    scenarios = [100, 500, 1000]
    for users in scenarios:
        await run_scenario(users)
        await asyncio.sleep(2) # Cooldown

if __name__ == "__main__":
    asyncio.run(main())
