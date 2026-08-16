from app.capabilities.models import (
    Capability,
    PermissionLevel,
)
from app.capabilities.registry import CapabilityRegistry
from app.tools.registry import ToolRegistry


class CapabilityAdapter:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        capability_registry: CapabilityRegistry,
    ) -> None:
        self._tools = tool_registry
        self._capabilities = capability_registry

    def expose_tool(
        self,
        tool_name: str,
        permission: PermissionLevel = PermissionLevel.NONE,
    ) -> Capability:

        try:
            tool = self._tools.get(tool_name)
        except KeyError as exc:
            raise ValueError(
                f"Cannot expose unknown tool: {tool_name}"
            ) from exc

        capability = Capability(
            name=tool.name,
            description=tool.description,
            permission=permission,
            execute=tool.executor,
        )

        self._capabilities.register(capability)

        return capability

    def expose_all(
        self,
        permission: PermissionLevel = PermissionLevel.NONE,
    ) -> list[Capability]:

        capabilities: list[Capability] = []

        for tool in self._tools.list():
            capabilities.append(
                self.expose_tool(
                    tool.name,
                    permission=permission,
                )
            )

        return capabilities
