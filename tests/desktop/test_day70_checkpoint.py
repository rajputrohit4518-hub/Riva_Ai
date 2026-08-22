import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.desktop.checkpoint import RivaDesktopSystem

def test_desktop_system_checkpoint(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "settings.json"
        state_file = Path(tmpdir) / "crash_state.json"
        
        # Mock platform startup/registry calls to remain safe and cross-platform
        system = RivaDesktopSystem(str(config_file), str(state_file))
        monkeypatch.setattr(system.startup, "is_startup_enabled", lambda: False)
        monkeypatch.setattr(system.startup, "enable_startup", lambda: True)

        # Initialize runtime
        assert system.initialize_runtime() is True
        assert system.background_service.is_running is True
        
        # Verify settings & permissions interoperability
        assert system.settings.get("theme") == "dark"
        assert system.permissions.check_permission("voice_recording") is True
        
        # Shutdown runtime cleanly
        system.shutdown_runtime()
        assert system.background_service.is_running is False
        assert system.recovery.did_crash_occur() is False
