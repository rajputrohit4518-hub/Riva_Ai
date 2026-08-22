import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.notifications import CrossDeviceNotificationManager

def test_notification_dispatch_and_tracking():
    manager = CrossDeviceNotificationManager(node_id="desktop_primary")
    
    notif = manager.dispatch_notification(
        title="Incoming Call",
        message="John Doe is calling your mobile device",
        source_device="phone_companion",
        priority="high"
    )
    
    assert notif["title"] == "Incoming Call"
    assert notif["priority"] == "high"
    assert len(manager.get_unread_notifications()) == 1
    
    # Mark as read
    success = manager.mark_as_read(notif["notification_id"])
    assert success is True
    assert len(manager.get_unread_notifications()) == 0
