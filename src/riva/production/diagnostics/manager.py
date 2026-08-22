import sys
import platform
import psutil
from typing import Any, Dict

class ProductionDiagnosticsManager:
    """Gathers system and runtime health diagnostics for Riva Production."""

    @staticmethod
    def get_system_diagnostics() -> Dict[str, Any]:
        """Collects current CPU, memory, disk, and platform statistics."""
        try:
            virtual_memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            cpu_usage = psutil.cpu_percent(interval=0.1)
        except Exception:
            virtual_memory = None
            disk_usage = None
            cpu_usage = 0.0

        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": sys.version,
            "cpu_usage_percent": cpu_usage,
            "memory": {
                "total": virtual_memory.total if virtual_memory else 0,
                "available": virtual_memory.available if virtual_memory else 0,
                "percent_used": virtual_memory.percent if virtual_memory else 0.0
            },
            "disk": {
                "total": disk_usage.total if disk_usage else 0,
                "free": disk_usage.free if disk_usage else 0,
                "percent_used": disk_usage.percent if disk_usage else 0.0
            }
        }
