import time
from collections import defaultdict
from typing import Dict, List
from threading import RLock

class MetricsCollector:
    """In-memory metrics collector compatible with Prometheus format."""
    
    def __init__(self):
        self._counters: Dict[str, int] = defaultdict(int)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = RLock()

    def inc_counter(self, metric_name: str, value: int = 1) -> None:
        """Increments a counter metric (e.g. farm360_requests_total)."""
        with self._lock:
            self._counters[metric_name] += value

    def observe_latency(self, metric_name: str, duration_ms: float) -> None:
        """Records a duration for histogram/percentile calculations."""
        with self._lock:
            # For memory safety in production, we'd use a real histogram or reservoir sampling.
            # For Pilot V1, we maintain a bounded list.
            if len(self._histograms[metric_name]) > 10000:
                self._histograms[metric_name].pop(0)
            self._histograms[metric_name].append(duration_ms)

    def calculate_percentile(self, metric_name: str, percentile: float) -> float:
        with self._lock:
            data = self._histograms.get(metric_name)
            if not data:
                return 0.0
            sorted_data = sorted(data)
            index = int((percentile / 100.0) * len(sorted_data))
            if index >= len(sorted_data):
                index = len(sorted_data) - 1
            return sorted_data[index]

    def export_prometheus(self) -> str:
        """Exports metrics in Prometheus text-based exposition format."""
        lines = []
        with self._lock:
            for name, value in self._counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")
                
            for name, data in self._histograms.items():
                if not data:
                    continue
                # Export as summary with percentiles
                p50 = self.calculate_percentile(name, 50)
                p95 = self.calculate_percentile(name, 95)
                p99 = self.calculate_percentile(name, 99)
                lines.append(f"# TYPE {name} summary")
                lines.append(f'{name}{{quantile="0.5"}} {p50}')
                lines.append(f'{name}{{quantile="0.95"}} {p95}')
                lines.append(f'{name}{{quantile="0.99"}} {p99}')
                lines.append(f'{name}_count {len(data)}')
                lines.append(f'{name}_sum {sum(data)}')
                
        return "\n".join(lines) + "\n"

# Global Instance
metrics = MetricsCollector()
