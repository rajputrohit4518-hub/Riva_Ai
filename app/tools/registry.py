from __future__ import annotations

from typing import Any, Callable

from app.tools.models import ToolDefinition


class ToolRegistry:
    """
    Central registry for Riva tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str | ToolDefinition,
        handler: Callable[..., Any] | None = None,
        description: str = "",
        category: str = "general",
        risk_level: str = "low",
        requires_confirmation: bool = False,
    ) -> ToolDefinition:

        if isinstance(name, ToolDefinition):
            if handler is not None:
                raise TypeError(
                    "handler must not be supplied when registering "
                    "a ToolDefinition."
                )
            definition = name

        else:
            tool_name = name.strip()

            if not tool_name:
                raise ValueError("Tool name cannot be empty.")

            if not callable(handler):
                raise TypeError("Tool handler must be callable.")

            definition = ToolDefinition(
                name=tool_name,
                description=description.strip(),
                executor=handler,
                category=category,
                risk_level=risk_level,
                requires_confirmation=requires_confirmation,
            )

        if definition.name in self._tools:
            raise ValueError(
                f"Tool '{definition.name}' is already registered."
            )

        self._tools[definition.name] = definition
        return definition

    def unregister(self, name: str) -> bool:
        return self._tools.pop(name.strip(), None) is not None

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name.strip())

    def has(self, name: str) -> bool:
        return name.strip() in self._tools

    def names(self) -> list[str]:
        return sorted(self._tools)

    def list(self) -> list[ToolDefinition]:
        return [
            self._tools[name]
            for name in sorted(self._tools)
        ]

    def execute(self, name: str, **kwargs: Any) -> Any:
        definition = self.get(name)

        if definition is None:
            raise KeyError(f"Unknown tool: {name}")

        risk = definition.risk_level.lower()

        if risk == "critical":
            raise PermissionError(
                f"Tool '{name}' execution denied."
            )

        if risk == "medium":
            raise PermissionError(
                f"Tool '{name}': Confirmation required."
            )

        if definition.requires_confirmation and risk != "low":
            raise PermissionError(
                f"Tool '{name}' requires confirmation."
            )

        return definition.executor(**kwargs)

    def clear(self) -> None:
        self._tools.clear()

    def __len__(self) -> int:
        return len(self._tools)
