from agents import function_tool


def calculate_expression(expression: str) -> str:
    """Calculate a basic arithmetic expression."""

    allowed = set("0123456789+-*/(). ")

    if not expression or any(char not in allowed for char in expression):
        return "Invalid arithmetic expression."

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception:
        return "Unable to calculate the expression."


@function_tool
def calculate(expression: str) -> str:
    """Calculate a basic arithmetic expression for Riva."""

    return calculate_expression(expression)
