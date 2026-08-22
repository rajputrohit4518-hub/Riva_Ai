from typing import Dict, Set

class DesktopPermissionsManager:
    """Manages user permissions and capability grants for the Riva Desktop application."""

    DEFAULT_PERMISSIONS: Dict[str, bool] = {
        "file_system_access": False,
        "desktop_automation": False,
        "voice_recording": True,
        "network_access": True,
        "clipboard_access": False
    }

    def __init__(self):
        self.permissions = self.DEFAULT_PERMISSIONS.copy()

    def check_permission(self, permission: str) -> bool:
        """Checks if a specific permission is granted."""
        return self.permissions.get(permission, False)

    def grant_permission(self, permission: str) -> None:
        """Grants a specific permission."""
        if permission in self.permissions:
            self.permissions[permission] = True

    def revoke_permission(self, permission: str) -> None:
        """Revokes a specific permission."""
        if permission in self.permissions:
            self.permissions[permission] = False

    def list_permissions(self) -> Dict[str, bool]:
        """Returns a copy of all current permissions."""
        return self.permissions.copy()
