import json
from pathlib import Path
from typing import Any, Dict

class DesktopSettingsManager:
    """Manages persistent user settings for the Riva Desktop application."""
    
    DEFAULT_SETTINGS: Dict[str, Any] = {
        "theme": "dark",
        "voice_enabled": True,
        "wake_word_active": False,
        "api_endpoint": "http://localhost:8000",
        "log_level": "INFO",
        "hotkey": "Ctrl+Space"
    }

    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".riva" / "desktop_settings.json"
        
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """Loads settings from disk, falling back to defaults if missing or corrupted."""
        if not self.config_path.exists():
            return self.DEFAULT_SETTINGS.copy()
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge with defaults to ensure new keys are always present
                return {**self.DEFAULT_SETTINGS, **saved}
        except Exception:
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self) -> None:
        """Persists current settings to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save_settings()
