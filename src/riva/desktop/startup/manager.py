import os
import sys
from pathlib import Path
import platform

class DesktopStartupManager:
    """Manages system startup registration (launch on boot) for the Riva Desktop application."""

    def __init__(self, app_name: str = "RivaDesktop", executable_path: str = None):
        self.app_name = app_name
        self.executable_path = executable_path or sys.executable

    def is_startup_enabled(self) -> bool:
        """Checks if startup on boot is configured for the current platform."""
        system = platform.system()
        if system == "Windows":
            return self._check_windows_registry()
        elif system == "Darwin":
            return self._check_macos_plist()
        else:
            return self._check_linux_desktop_file()

    def enable_startup(self) -> bool:
        """Enables launch-on-boot configuration."""
        system = platform.system()
        if system == "Windows":
            return self._set_windows_registry(True)
        elif system == "Darwin":
            return self._set_macos_plist(True)
        else:
            return self._set_linux_desktop_file(True)

    def disable_startup(self) -> bool:
        """Disables launch-on-boot configuration."""
        system = platform.system()
        if system == "Windows":
            return self._set_windows_registry(False)
        elif system == "Darwin":
            return self._set_macos_plist(False)
        else:
            return self._set_linux_desktop_file(False)

    # Platform-specific implementations with safe stubs/mock support for testing
    def _check_windows_registry(self) -> bool:
        try:
            import winreg
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, self.app_name)
                return True
        except Exception:
            return False

    def _set_windows_registry(self, enable: bool) -> bool:
        try:
            import winreg
            key_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'"{self.executable_path}"')
                else:
                    try:
                        winreg.DeleteValue(key, self.app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            # Fallback for non-Windows test environments or restricted permissions
            return False

    def _check_macos_plist(self) -> bool:
        plist_path = Path.home() / "Library" / "LaunchAgents" / f"com.{self.app_name.lower()}.plist"
        return plist_path.exists()

    def _set_macos_plist(self, enable: bool) -> bool:
        try:
            plist_dir = Path.home() / "Library" / "LaunchAgents"
            plist_dir.mkdir(parents=True, exist_ok=True)
            plist_path = plist_dir / f"com.{self.app_name.lower()}.plist"
            if enable:
                content = f"<?xml version=\"1.0\"?><plist version=\"1.0\"><dict><key>Label</key><string>com.{self.app_name.lower()}</string><key>ProgramArguments</key><array><string>{self.executable_path}</string></array><key>RunAtLoad</key><true/></dict></plist>"
                plist_path.write_text(content, encoding="utf-8")
            else:
                if plist_path.exists():
                    plist_path.unlink()
            return True
        except Exception:
            return False

    def _check_linux_desktop_file(self) -> bool:
        desktop_path = Path.home() / ".config" / "autostart" / f"{self.app_name.lower()}.desktop"
        return desktop_path.exists()

    def _set_linux_desktop_file(self, enable: bool) -> bool:
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_path = autostart_dir / f"{self.app_name.lower()}.desktop"
            if enable:
                content = f"[Desktop Entry]\nType=Application\nName={self.app_name}\nExec={self.executable_path}\nX-GNOME-Autostart-enabled=true\n"
                desktop_path.write_text(content, encoding="utf-8")
            else:
                if desktop_path.exists():
                    desktop_path.unlink()
            return True
        except Exception:
            return False
