import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.bus import CrossDeviceEventBus

def test_event_bus_pub_sub():
    bus = CrossDeviceEventBus(node_id="desktop_primary")
    received_events = []

    def sample_listener(data: dict):
        received_events.append(data)

    bus.subscribe("notification_push", sample_listener)
    
    # Publish local event
    notified_count = bus.publish_local("notification_push", {"message": "Hello from companion device!"})
    
    assert notified_count == 1
    assert len(received_events) == 1
    assert received_events[0]["message"] == "Hello from companion device!"

def test_event_packet_serialization():
    packet_str = CrossDeviceEventBus.create_event_packet("sync_alert", {"status": "synced"}, "tablet_1")
    parsed = json.loads(packet_str)
    
    assert parsed["source_node"] == "tablet_1"
    assert parsed["topic"] == "sync_alert"
    assert parsed["data"]["status"] == "synced"
