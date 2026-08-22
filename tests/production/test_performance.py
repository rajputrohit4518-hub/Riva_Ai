import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.performance.manager import ProductionPerformanceManager

def test_performance_timing_and_metrics():
    manager = ProductionPerformanceManager()
    
    @manager.time_execution("mock_operation")
    def sample_task():
        time.sleep(0.01)
        return "done"
    
    res = sample_task()
    assert res == "done"
    
    metrics = manager.get_metrics()
    assert "mock_operation" in metrics
    assert metrics["mock_operation"]["count"] == 1
    assert metrics["mock_operation"]["avg_ms"] > 0
