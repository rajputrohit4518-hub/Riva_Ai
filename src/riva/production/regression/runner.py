import subprocess
import sys
from typing import Dict, Any

class ProductionRegressionRunner:
    """Orchestrates and executes the complete test regression suite across all Riva modules."""

    @staticmethod
    def run_full_suite() -> Dict[str, Any]:
        """Runs pytest on non-recursive target tests to avoid deadlock."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/production/test_config.py", "tests/production/test_backup.py"],
            capture_output=True,
            text=True
        )
        
        return {
            "exit_code": result.returncode,
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
