from app.tools.calculator import calculate_expression
from app.tools.models import ToolDefinition
from app.tools.registry import ToolRegistry


def _execute_calculator(expression: str) -> str:
    result = calculate_expression(expression)

    if result in {
        "Invalid arithmetic expression.",
        "Invalid characters in expression.",
        "Unable to calculate the expression.",
    }:
        raise ValueError("Invalid arithmetic expression.")

    # Preserve the historical tool-execution representation for
    # division results while keeping Calculator.calculate() canonical.
    if "/" in expression:
        try:
            numeric = float(result)
            if numeric.is_integer():
                return f"{numeric:.1f}"
        except (TypeError, ValueError):
            pass

    return result

def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register("calculator", _execute_calculator, "Perform basic arithmetic calculations.", category="utility")

    return registry



