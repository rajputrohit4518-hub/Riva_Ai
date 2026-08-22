import time
from typing import Dict, Any, List, Optional

class DistributedTelemetryManager:
    """Aggregates and inspects telemetry logs and metrics collected across distributed Riva nodes."""

    def __init__(self, node_id: str, max_logs: int = 500):
        self.node_id = node_id
        self.max_logs = max_logs
        self.telemetry_logs: List[Dict[str, Any]] = []

    def ingest_log(self, level: str, message: str, source_device: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ingests a log entry from a local or remote node."""
        entry = {
            "source_device": source_device or self.node_id,
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time()
        }
        
        self.telemetry_logs.insert(0, entry)
        if len(self.telemetry_logs) > self.max_logs:
            self.telemetry_logs.pop()

        return entry

    def query_logs(self, level: Optional[str] = None, source_device: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries aggregated telemetry logs by severity level or source device."""
        results = self.telemetry_logs
        if level:
            level_upper = level.upper()
            results = [log for log in results if log["level"] == level_upper]
        if source_device:
            results = [log for log in results if log["source_device"] == source_device]
        return results
