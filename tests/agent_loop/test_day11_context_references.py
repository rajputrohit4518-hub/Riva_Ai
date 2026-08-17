from app.agent_loop.decision import DecisionMaker
from app.agent_loop.models import DecisionType
from app.context.models import ContextSnapshot


def make_context(last_response=None, messages=None):
    return ContextSnapshot(
        session_id="day11-test",
        recent_messages=messages or [],
        last_response=last_response,
        memories=[],
    )


def test_day11_multiply_previous_result():
    decision = DecisionMaker().decide(
        "multiply it by 5",
        make_context(
            last_response="10",
            messages=[
                {"role": "user", "content": "Calculate 10"},
                {"role": "assistant", "content": "10"},
            ],
        ),
    )

    assert decision.decision_type == DecisionType.USE_TOOL
    assert decision.tool_name == "calculator"
    assert decision.tool_arguments["expression"] == "10 * 5"


def test_day11_add_to_previous_result():
    decision = DecisionMaker().decide(
        "add 7 to it",
        make_context(last_response="10"),
    )

    assert decision.decision_type == DecisionType.USE_TOOL
    assert decision.tool_arguments["expression"] == "10 + 7"


def test_day11_subtract_from_previous_result():
    decision = DecisionMaker().decide(
        "subtract 3 from it",
        make_context(last_response="10"),
    )

    assert decision.decision_type == DecisionType.USE_TOOL
    assert decision.tool_arguments["expression"] == "10 - 3"


def test_day11_divide_previous_result():
    decision = DecisionMaker().decide(
        "divide it by 2",
        make_context(last_response="10"),
    )

    assert decision.decision_type == DecisionType.USE_TOOL
    assert decision.tool_arguments["expression"] == "10 / 2"


def test_day11_previous_message_reference():
    decision = DecisionMaker().decide(
        "what did you just say",
        make_context(
            last_response="15",
            messages=[
                {"role": "user", "content": "Calculate 10 + 5"},
                {"role": "assistant", "content": "15"},
            ],
        ),
    )

    assert decision.decision_type == DecisionType.RESPOND
    assert decision.response == "Calculate 10 + 5"


def test_day11_this_reference():
    decision = DecisionMaker().decide(
        "what was this",
        make_context(
            last_response="15",
            messages=[
                {"role": "user", "content": "Calculate 10 + 5"},
                {"role": "assistant", "content": "15"},
            ],
        ),
    )

    assert decision.decision_type == DecisionType.RESPOND
    assert decision.response == "Calculate 10 + 5"
