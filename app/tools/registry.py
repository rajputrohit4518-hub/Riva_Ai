from typing import Dict, List

from app.security.models import PermissionDecision
from app.security.permissions import PermissionEngine
from app.tools.models import ToolDefinition


class ToolRegistry:
    def __init__(
        self,
        permission_engine: PermissionEngine | None = None,
    ) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._permissions = permission_engine or PermissionEngine()

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool not found: {name}") from exc

    def remove(self, name: str) -> None:
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")

        del self._tools[name]

    def list(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def execute(self, name: str, **kwargs) -> str:
        tool = self.get(name)

        decision = self._permissions.evaluate(tool.risk_level)

        if decision == PermissionDecision.DENY:
            raise PermissionError(
                f"Tool execution denied: {tool.name}"
            )

        if decision == PermissionDecision.CONFIRM:
            raise PermissionError(
                f"Confirmation required for tool: {tool.name}"
            )

        return tool.executor(**kwargs)
