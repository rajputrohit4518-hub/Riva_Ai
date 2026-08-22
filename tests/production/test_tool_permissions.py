import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.permissions.manager import ProductionToolPermissionManager

def test_default_tool_permissions():
    manager = ProductionToolPermissionManager()
    assert manager.is_tool_allowed("calculator") is True
    assert manager.is_tool_allowed("shell_execution") is False
    assert manager.is_tool_allowed("unknown_random_tool") is False

def test_grant_and_revoke_tools():
    manager = ProductionToolPermissionManager()
    
    # Grant restricted tool
    manager.grant_tool("shell_execution")
    assert manager.is_tool_allowed("shell_execution") is True
    
    # Revoke allowed tool
    manager.revoke_tool("calculator")
    assert manager.is_tool_allowed("calculator") is False
