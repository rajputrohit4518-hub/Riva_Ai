import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.diagnostics.manager import ProductionDiagnosticsManager

def test_system_diagnostics_structure():
    diag = ProductionDiagnosticsManager.get_system_diagnostics()
    
    assert "platform" in diag
    assert "python_version" in diag
    assert "cpu_usage_percent" in diag
    assert "memory" in diag
    assert "disk" in diag
    assert isinstance(diag["cpu_usage_percent"], float)
