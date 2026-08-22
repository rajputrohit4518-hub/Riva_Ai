import time
import functools
from typing import Any, Callable, Dict, Tuple

class ProductionPerformanceManager:
    """Provides execution timing, memoization, and performance metrics for Riva Production."""

    def __init__(self):
        self._metrics: Dict[str, list] = {}

    def time_execution(self, func_name: str) -> Callable:
        """Decorator to measure and record function execution latency."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration = (time.perf_counter() - start_time) * 1000.0 # milliseconds
                    if func_name not in self._metrics:
                        self._metrics[func_name] = []
                    self._metrics[func_name].append(duration)
            return wrapper
        return decorator

    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Returns statistical latency metrics for tracked operations."""
        summary = {}
        for name, timings in self._metrics.items():
            if timings:
                summary[name] = {
                    "count": len(timings),
                    "avg_ms": sum(timings) / len(timings),
                    "max_ms": max(timings),
                    "min_ms": min(timings)
                }
        return summary

    def clear_metrics(self) -> None:
        """Clears recorded performance metrics."""
        self._metrics.clear()
