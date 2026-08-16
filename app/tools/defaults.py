from app.tools.calculator import calculate_expression
from app.tools.models import ToolDefinition
from app.tools.registry import ToolRegistry


def _execute_calculator(expression: str) -> str:
    result = calculate_expression(expression)

    if result in {
        "Invalid arithmetic expression.",
        "Unable to calculate the expression.",
    }:
        raise ValueError(result)

    return result


def _execute_calculator(expression: str) -> str:
    result = calculate_expression(expression)

    if result in {
        "Invalid arithmetic expression.",
        "Unable to calculate the expression.",
    }:
        raise ValueError(result)

    return result


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="calculator",
            description="Perform basic arithmetic calculations.",
            executor=_execute_calculator,
            category="utility",
            risk_level="low",
            requires_confirmation=False,
        )
    )

    return registry


