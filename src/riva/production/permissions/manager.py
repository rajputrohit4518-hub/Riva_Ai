from typing import Set, Dict

class ProductionToolPermissionManager:
    """Manages fine-grained execution permissions for tools in Riva Production."""

    def __init__(self):
        # Default allowed tool categories or specific tool names
        self.allowed_tools: Set[str] = {
            "calculator",
            "search",
            "system_info"
        }
        self.restricted_tools: Set[str] = {
            "file_deletion",
            "shell_execution",
            "registry_modification"
        }

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Checks if a tool is explicitly permitted for execution."""
        if tool_name in self.allowed_tools:
            return True
        if tool_name in self.restricted_tools:
            return False
        # Default policy for unregistered/unknown tools: require explicit grant
        return False

    def grant_tool(self, tool_name: str) -> None:
        """Grants permission to execute a tool."""
        self.restricted_tools.discard(tool_name)
        self.allowed_tools.add(tool_name)

    def revoke_tool(self, tool_name: str) -> None:
        """Revokes permission to execute a tool."""
        self.allowed_tools.discard(tool_name)
        self.restricted_tools.add(tool_name)
