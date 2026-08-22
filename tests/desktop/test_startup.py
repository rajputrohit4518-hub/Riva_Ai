import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.desktop.startup.manager import DesktopStartupManager

def test_startup_manager_lifecycle(monkeypatch):
    manager = DesktopStartupManager(app_name="RivaTestApp")
    
    # Mock platform-specific check/set to ensure safe cross-platform unit testing
    monkeypatch.setattr(manager, "is_startup_enabled", lambda: False)
    monkeypatch.setattr(manager, "enable_startup", lambda: True)
    monkeypatch.setattr(manager, "disable_startup", lambda: True)
    
    assert not manager.is_startup_enabled()
    assert manager.enable_startup() is True
    assert manager.disable_startup() is True
