import socket
import json
from typing import Dict, Any, List, Optional

class CrossDeviceManager:
    """Manages node discovery, registration, and secure payload routing across distributed Riva devices."""

    def __init__(self, node_id: str, port: int = 8765):
        self.node_id = node_id
        self.port = port
        self.registered_nodes: Dict[str, Dict[str, Any]] = {}

    def register_node(self, target_node_id: str, host: str, port: int) -> None:
        """Registers a remote Riva node in the local network topology."""
        self.registered_nodes[target_node_id] = {
            "host": host,
            "port": port,
            "status": "active"
        }

    def unregister_node(self, target_node_id: str) -> None:
        """Removes a remote node from the active registry."""
        self.registered_nodes.pop(target_node_id, None)

    def get_node(self, target_node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves configuration and status for a registered node."""
        return self.registered_nodes.get(target_node_id)

    def list_nodes(self) -> List[str]:
        """Returns a list of all active registered node IDs."""
        return list(self.registered_nodes.keys())

    @staticmethod
    def create_payload(action: str, data: Dict[str, Any], source_node: str) -> str:
        """Serializes a cross-device command or data payload."""
        return json.dumps({
            "source_node": source_node,
            "action": action,
            "data": data
        })
