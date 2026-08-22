import json
from pathlib import Path
from typing import Dict, Any, Optional

class CrossDeviceStateSync:
    """Manages state synchronization, version tracking, and conflict resolution across distributed Riva devices."""

    def __init__(self, state_file_path: Optional[str] = None):
        self.state_file_path = Path(state_file_path) if state_file_path else Path.home() / ".riva" / "device_sync_state.json"
        self.local_state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Loads state from local storage or returns a default schema."""
        if self.state_file_path.exists():
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "version": 1,
            "device_id": "primary_desktop",
            "preferences": {},
            "last_updated": 0
        }

    def update_local_state(self, key: str, value: Any) -> int:
        """Updates a state value locally and increments the state version vector."""
        self.local_state["preferences"][key] = value
        self.local_state["version"] += 1
        self._persist_state()
        return self.local_state["version"]

    def receive_remote_state(self, remote_payload: Dict[str, Any]) -> bool:
        """Merges remote state using a Last-Write-Wins / Vector Clock strategy."""
        remote_version = remote_payload.get("version", 0)
        local_version = self.local_state.get("version", 0)

        if remote_version > local_version:
            self.local_state["version"] = remote_version
            self.local_state["preferences"].update(remote_payload.get("preferences", {}))
            self._persist_state()
            return True
        return False

    def _persist_state(self) -> None:
        """Persists current state to disk."""
        try:
            self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(self.local_state, f, indent=4)
        except Exception:
            pass
