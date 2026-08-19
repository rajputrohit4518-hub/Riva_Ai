from app.tools.registry import ToolRegistry


def test_day31_register_and_lookup():
    registry = ToolRegistry()

    def calculator(expression):
        return expression

    tool = registry.register(
        "calculator",
        calculator,
        "Performs calculations.",
    )

    assert tool.name == "calculator"
    assert registry.has("calculator")
    assert registry.get("calculator").handler is calculator


def test_day31_registry_names():
    registry = ToolRegistry()

    registry.register("browser", lambda: None)
    registry.register("calculator", lambda: None)

    assert registry.names() == ["browser", "calculator"]


def test_day31_unregister():
    registry = ToolRegistry()

    registry.register("calculator", lambda: None)

    assert registry.unregister("calculator") is True
    assert registry.has("calculator") is False


def test_day31_invalid_tool_rejected():
    registry = ToolRegistry()

    try:
        registry.register("", lambda: None)
    except ValueError:
        pass
    else:
        raise AssertionError("Empty tool name should be rejected.")


def test_day31_non_callable_rejected():
    registry = ToolRegistry()

    try:
        registry.register("calculator", "not callable")
    except TypeError:
        pass
    else:
        raise AssertionError("Non-callable handler should be rejected.")
