import json
from typing import Dict, Any, List, Callable

class CrossDeviceEventBus:
    """Manages pub/sub event routing and real-time message broadcasting across distributed Riva nodes."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_topic: str, callback: Callable) -> None:
        """Subscribes a callback function to a specific event topic."""
        if event_topic not in self.subscribers:
            self.subscribers[event_topic] = []
        self.subscribers[event_topic].append(callback)

    def unsubscribe(self, event_topic: str, callback: Callable) -> None:
        """Unsubscribes a callback from an event topic."""
        if event_topic in self.subscribers:
            if callback in self.subscribers[event_topic]:
                self.subscribers[event_topic].remove(callback)

    def publish_local(self, event_topic: str, event_data: Dict[str, Any]) -> int:
        """Publishes an event locally to all subscribed listeners and returns notification count."""
        count = 0
        if event_topic in self.subscribers:
            for callback in self.subscribers[event_topic]:
                try:
                    callback(event_data)
                    count += 1
                except Exception:
                    pass
        return count

    @staticmethod
    def create_event_packet(event_topic: str, event_data: Dict[str, Any], source_node: str) -> str:
        """Serializes an event packet for transmission across nodes."""
        return json.dumps({
            "source_node": source_node,
            "topic": event_topic,
            "data": event_data
        })
