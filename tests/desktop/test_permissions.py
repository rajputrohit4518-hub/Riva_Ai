import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.desktop.permissions.manager import DesktopPermissionsManager

def test_default_permissions():
    manager = DesktopPermissionsManager()
    assert manager.check_permission("voice_recording") is True
    assert manager.check_permission("file_system_access") is False

def test_grant_and_revoke_permissions():
    manager = DesktopPermissionsManager()
    
    # Grant permission
    manager.grant_permission("file_system_access")
    assert manager.check_permission("file_system_access") is True
    
    # Revoke permission
    manager.revoke_permission("file_system_access")
    assert manager.check_permission("file_system_access") is False

def test_invalid_permission_handling():
    manager = DesktopPermissionsManager()
    # Should safely ignore unknown permissions
    manager.grant_permission("non_existent_perm")
    assert manager.check_permission("non_existent_perm") is False
