import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class DesktopCrashRecoveryManager:
    """Manages application state snapshots and crash recovery logs for Riva Desktop."""

    def __init__(self, state_file_path: Optional[str] = None):
        if state_file_path:
            self.state_file_path = Path(state_file_path)
        else:
            self.state_file_path = Path.home() / ".riva" / "crash_state.json"

    def save_state(self, state_data: Dict[str, Any]) -> None:
        """Saves current session state snapshot for potential crash recovery."""
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump({"clean_exit": False, "state": state_data}, f, indent=4)
        except Exception:
            pass

    def mark_clean_exit(self) -> None:
        """Marks that the application exited normally."""
        try:
            if self.state_file_path.exists():
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["clean_exit"] = True
                with open(self.state_file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
        except Exception:
            pass

    def did_crash_occur(self) -> bool:
        """Checks if the previous session terminated unexpectedly."""
        if not self.state_file_path.exists():
            return False
        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return not data.get("clean_exit", True)
        except Exception:
            return False

    def recover_state(self) -> Optional[Dict[str, Any]]:
        """Retrieves the saved state data from the crashed session."""
        if not self.state_file_path.exists():
            return None
        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("state", None)
        except Exception:
            return None

    def clear_state(self) -> None:
        """Clears recovery state file after successful recovery or clean exit."""
        try:
            if self.state_file_path.exists():
                self.state_file_path.unlink()
        except Exception:
            pass
