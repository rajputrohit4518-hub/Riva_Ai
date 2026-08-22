import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.sync import CrossDeviceStateSync

def test_state_sync_versioning_and_merge():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "sync_state.json"
        sync_manager = CrossDeviceStateSync(str(state_file))
        
        # Initial local update
        v1 = sync_manager.update_local_state("theme", "dark")
        assert v1 == 2
        assert sync_manager.local_state["preferences"]["theme"] == "dark"
        
        # Receive remote update with higher version vector
        remote_payload = {
            "version": 5,
            "device_id": "tablet_companion",
            "preferences": {
                "theme": "light",
                "notifications": True
            }
        }
        
        merged = sync_manager.receive_remote_state(remote_payload)
        assert merged is True
        assert sync_manager.local_state["version"] == 5
        assert sync_manager.local_state["preferences"]["theme"] == "light"
        assert sync_manager.local_state["preferences"]["notifications"] is True
        
        # Receive obsolete remote update with lower version vector (should ignore)
        obsolete_payload = {
            "version": 3,
            "device_id": "phone_companion",
            "preferences": {"theme": "contrast"}
        }
        merged_obsolete = sync_manager.receive_remote_state(obsolete_payload)
        assert merged_obsolete is False
        assert sync_manager.local_state["preferences"]["theme"] == "light"
