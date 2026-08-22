from riva.desktop.settings.manager import DesktopSettingsManager
from riva.desktop.permissions.manager import DesktopPermissionsManager
from riva.desktop.background.service import BackgroundOperationService
from riva.desktop.startup.manager import DesktopStartupManager
from riva.desktop.recovery.manager import DesktopCrashRecoveryManager

class RivaDesktopSystem:
    """Orchestrates all desktop subsystems into a unified Riva Desktop runtime."""

    def __init__(self, config_path: str = None, state_file_path: str = None):
        self.settings = DesktopSettingsManager(config_path)
        self.permissions = DesktopPermissionsManager()
        self.startup = DesktopStartupManager()
        self.recovery = DesktopCrashRecoveryManager(state_file_path)
        self.background_service = BackgroundOperationService()

    def initialize_runtime(self) -> bool:
        """Performs startup checks, crash recovery evaluation, and background loop start."""
        # Check if previous session crashed
        if self.recovery.did_crash_occur():
            # Handle or log recovery state
            self.recovery.clear_state()

        # Mark session start in crash manager
        self.recovery.save_state({"status": "running", "theme": self.settings.get("theme")})
        
        # Start background tasks if enabled
        if self.settings.get("voice_enabled", True):
            self.background_service.start()

        return True

    def shutdown_runtime(self) -> None:
        """Gracefully shuts down background services and marks clean exit."""
        self.background_service.stop()
        self.recovery.mark_clean_exit()
        self.recovery.clear_state()
