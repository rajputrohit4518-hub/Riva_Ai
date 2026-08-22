import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

class ProductionConfigManager:
    """Manages centralized configuration, environment overrides, and schema validation for Riva Production."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "environment": "production",
        "log_level": "INFO",
        "api_host": "0.0.0.0",
        "api_port": 8000,
        "database_url": "sqlite:///riva_prod.db",
        "security": {
            "require_auth": True,
            "max_payload_size_mb": 10
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = Path.home() / ".riva" / "config.json"
        
        self.config = self._load_and_merge()

    def _load_and_merge(self) -> Dict[str, Any]:
        """Loads configuration from disk and applies environment variable overrides."""
        cfg = self.DEFAULT_CONFIG.copy()
        
        # Load from disk if exists
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    disk_cfg = json.load(f)
                    cfg.update(disk_cfg)
            except Exception:
                pass

        # Environment variable overrides (e.g., RIVA_ENVIRONMENT, RIVA_LOG_LEVEL, RIVA_API_PORT)
        if env_env := os.getenv("RIVA_ENVIRONMENT"):
            cfg["environment"] = env_env
        if env_log := os.getenv("RIVA_LOG_LEVEL"):
            cfg["log_level"] = env_log
        if env_port := os.getenv("RIVA_API_PORT"):
            try:
                cfg["api_port"] = int(env_port)
            except ValueError:
                pass
        if env_db := os.getenv("RIVA_DATABASE_URL"):
            cfg["database_url"] = env_db

        return cfg

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieves a configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Sets a configuration value and persists to disk."""
        self.config[key] = value
        self.save()

    def save(self) -> None:
        """Persists current configuration to disk."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass
