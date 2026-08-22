import time
import uuid
from typing import Dict, Any, List, Optional

class CrossDeviceNotificationManager:
    """Manages routing, forwarding, and action handling for notifications across connected Riva devices."""

    def __init__(self, node_id: str, max_notifications: int = 100):
        self.node_id = node_id
        self.max_notifications = max_notifications
        self.notifications: List[Dict[str, Any]] = []

    def dispatch_notification(self, title: str, message: str, source_device: Optional[str] = None, priority: str = "normal", target_device: Optional[str] = None) -> Dict[str, Any]:
        """Creates and records a notification for dispatch across devices."""
        notif = {
            "notification_id": str(uuid.uuid4()),
            "source_device": source_device or self.node_id,
            "target_device": target_device or "broadcast",
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": time.time(),
            "read": False
        }
        
        self.notifications.insert(0, notif)
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop()

        return notif

    def mark_as_read(self, notification_id: str) -> bool:
        """Marks a specific notification as read."""
        for notif in self.notifications:
            if notif["notification_id"] == notification_id:
                notif["read"] = True
                return True
        return False

    def get_unread_notifications(self) -> List[Dict[str, Any]]:
        """Returns all unread notifications."""
        return [n for n in self.notifications if not n["read"]]
