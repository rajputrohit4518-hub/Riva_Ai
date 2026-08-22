import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.telemetry import DistributedTelemetryManager

def test_telemetry_ingestion_and_query():
    manager = DistributedTelemetryManager(node_id="desktop_primary")
    
    manager.ingest_log("INFO", "Device sync completed successfully", source_device="tablet_1", metadata={"duration_ms": 120})
    manager.ingest_log("ERROR", "Failed to connect to companion node", source_device="phone_1", metadata={"error_code": 503})
    manager.ingest_log("INFO", "Local task queue processed", source_device="desktop_primary")
    
    # Query all error logs
    error_logs = manager.query_logs(level="ERROR")
    assert len(error_logs) == 1
    assert error_logs[0]["metadata"]["error_code"] == 503
    
    # Query logs from tablet_1
    tablet_logs = manager.query_logs(source_device="tablet_1")
    assert len(tablet_logs) == 1
    assert tablet_logs[0]["message"] == "Device sync completed successfully"
