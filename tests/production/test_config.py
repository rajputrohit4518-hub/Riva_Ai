import sys
import tempfile
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.config.manager import ProductionConfigManager

def test_default_production_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        manager = ProductionConfigManager(str(config_file))
        
        assert manager.get("environment") == "production"
        assert manager.get("log_level") == "INFO"
        assert manager.get("api_port") == 8000

def test_environment_variable_overrides(monkeypatch):
    monkeypatch.setenv("RIVA_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RIVA_API_PORT", "9090")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "config.json"
        manager = ProductionConfigManager(str(config_file))
        
        assert manager.get("log_level") == "DEBUG"
        assert manager.get("api_port") == 9090
