from app.planner import ExecutionPlan, PlanStep, Planner


def test_planner_creates_single_tool_plan():
    planner = Planner()

    plan = planner.plan(
        goal="calculate 25 * 6",
        tool_name="calculator",
        arguments={"expression": "25 * 6"},
    )

    assert isinstance(plan, ExecutionPlan)
    assert plan.goal == "calculate 25 * 6"
    assert len(plan.steps) == 1
    assert plan.steps[0] == PlanStep(
        tool_name="calculator",
        arguments={"expression": "25 * 6"},
    )


def test_planner_plan_is_not_empty():
    planner = Planner()

    plan = planner.plan(
        goal="calculate 10 + 5",
        tool_name="calculator",
        arguments={"expression": "10 + 5"},
    )

    assert plan.is_empty is False


def test_planner_rejects_empty_goal():
    planner = Planner()

    try:
        planner.plan(
            goal="",
            tool_name="calculator",
            arguments={"expression": "1 + 1"},
        )
    except ValueError as exc:
        assert str(exc) == "Planning goal cannot be empty."
    else:
        raise AssertionError("Expected ValueError")


def test_planner_rejects_empty_tool_name():
    planner = Planner()

    try:
        planner.plan(
            goal="calculate 1 + 1",
            tool_name="",
            arguments={"expression": "1 + 1"},
        )
    except ValueError as exc:
        assert str(exc) == "Tool name cannot be empty."
    else:
        raise AssertionError("Expected ValueError")
