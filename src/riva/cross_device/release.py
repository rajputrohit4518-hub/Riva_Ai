import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

class CrossDeviceReleaseCandidate:
    """Validates cross-device modules, integration tests, and network topologies to certify Phase 8 (Cross-Device Architecture)."""

    def __init__(self):
        self.version = "1.0.0-phase8-rc1"

    def verify_readiness(self) -> Dict[str, Any]:
        """Runs pre-flight validation checks for the cross-device architecture release candidate."""
        # 1. Run pytest suite on individual test files to avoid recursive test collection confusion
        test_result = subprocess.run(
            [sys.executable, "-m", "pytest", 
             "tests/cross_device/test_bus.py",
             "tests/cross_device/test_clipboard.py",
             "tests/cross_device/test_cross_device.py",
             "tests/cross_device/test_delegation.py",
             "tests/cross_device/test_notifications.py",
             "tests/cross_device/test_pairing.py",
             "tests/cross_device/test_queue.py",
             "tests/cross_device/test_sync.py",
             "tests/cross_device/test_telemetry.py"
            ],
            capture_output=True,
            text=True
        )

        tests_passed = test_result.returncode == 0

        # 2. Check core cross-device module files exist
        required_files = [
            Path("src/riva/cross_device/manager.py"),
            Path("src/riva/cross_device/sync.py"),
            Path("src/riva/cross_device/pairing.py"),
            Path("src/riva/cross_device/delegation.py"),
            Path("src/riva/cross_device/bus.py"),
            Path("src/riva/cross_device/queue.py"),
            Path("src/riva/cross_device/clipboard.py"),
            Path("src/riva/cross_device/notifications.py"),
            Path("src/riva/cross_device/telemetry.py")
        ]
        structure_intact = all(f.exists() for f in required_files)

        return {
            "version": self.version,
            "tests_passed": tests_passed,
            "structure_intact": structure_intact,
            "ready_for_release": tests_passed and structure_intact
        }
