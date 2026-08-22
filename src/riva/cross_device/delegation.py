import json
from typing import Dict, Any, Callable, Optional

class CrossDeviceToolDelegation:
    """Manages the remote dispatch and execution delegation of tools across connected Riva devices."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.registered_local_tools: Dict[str, Callable] = {}

    def register_tool(self, tool_name: str, func: Callable) -> None:
        """Registers a local tool that can be executed directly or delegated."""
        self.registered_local_tools[tool_name] = func

    def delegate_execution(self, target_node_id: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Formats a remote tool execution payload for dispatch to a target device."""
        return json.dumps({
            "source_node": self.node_id,
            "target_node": target_node_id,
            "action": "execute_tool",
            "tool_name": tool_name,
            "arguments": arguments
        })

    def handle_incoming_delegation(self, payload_json: str) -> Dict[str, Any]:
        """Receives a delegated tool execution request and executes it locally if permitted."""
        try:
            payload = json.loads(payload_json)
            tool_name = payload.get("tool_name")
            arguments = payload.get("arguments", {})

            if tool_name not in self.registered_local_tools:
                return {"success": False, "error": f"Tool '{tool_name}' not found on node {self.node_id}"}

            func = self.registered_local_tools[tool_name]
            result = func(**arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
