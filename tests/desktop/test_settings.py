import sys
from pathlib import Path

# Ensure project root is in sys.path so 'riva' package can be found
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tempfile
from riva.desktop.settings.manager import DesktopSettingsManager

def test_default_settings():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "settings.json"
        manager = DesktopSettingsManager(str(config_file))
        
        assert manager.get("theme") == "dark"
        assert manager.get("voice_enabled") is True
        assert manager.get("hotkey") == "Ctrl+Space"

def test_update_and_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "settings.json"
        manager = DesktopSettingsManager(str(config_file))
        
        manager.set("theme", "light")
        manager.set("wake_word_active", True)
        
        assert manager.get("theme") == "light"
        assert manager.get("wake_word_active") is True
        
        manager_reloaded = DesktopSettingsManager(str(config_file))
        assert manager_reloaded.get("theme") == "light"
        assert manager_reloaded.get("wake_word_active") is True
