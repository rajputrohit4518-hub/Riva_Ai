import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.manager import CrossDeviceManager

def test_node_registration_and_discovery():
    manager = CrossDeviceManager(node_id="desktop_primary", port=8765)
    
    # Register a companion mobile/tablet node
    manager.register_node("tablet_companion", "192.168.1.50", 8765)
    
    assert "tablet_companion" in manager.list_nodes()
    node_info = manager.get_node("tablet_companion")
    assert node_info["host"] == "192.168.1.50"
    assert node_info["status"] == "active"
    
    # Unregister node
    manager.unregister_node("tablet_companion")
    assert "tablet_companion" not in manager.list_nodes()

def test_payload_serialization():
    payload_str = CrossDeviceManager.create_payload("sync_state", {"theme": "dark"}, "desktop_primary")
    parsed = json.loads(payload_str)
    
    assert parsed["source_node"] == "desktop_primary"
    assert parsed["action"] == "sync_state"
    assert parsed["data"]["theme"] == "dark"
