from app.agent_loop.loop import RivaAgentLoop
from app.agent_loop.models import AgentDecision, DecisionType
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def make_loop(tmp_path, decision_maker):
    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(tmp_path / "day13.db"))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day13_successful_tool_is_verified(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "25 * 6",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Verified result: 150",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day13-verified",
        ),
        user_input="calculate 25 * 6",
    )

    assert decision_maker.calls == 2
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"
    assert result.executions[0].result == "150"
    assert result.response == "Verified result: 150"


def test_day13_failed_tool_can_be_corrected(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "invalid arithmetic",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "25 * 6",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Corrected and verified: 150",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day13-correction",
        ),
        user_input="calculate 25 * 6",
    )

    assert decision_maker.calls == 3
    assert len(result.executions) == 2

    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None

    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "150"

    assert result.response == "Corrected and verified: 150"


def test_day13_multiple_failed_attempts_then_success(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls <= 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "invalid arithmetic",
                    },
                )

            if self.calls == 3:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "10 + 5",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovered after multiple failures.",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day13-multiple-recovery",
        ),
        user_input="recover calculation",
    )

    assert decision_maker.calls == 4
    assert len(result.executions) == 3

    assert result.executions[0].status.value != "success"
    assert result.executions[1].status.value != "success"

    assert result.executions[2].status.value == "success"
    assert result.executions[2].result == "15"

    assert result.response == "Recovered after multiple failures."


def test_day13_failed_execution_is_preserved_for_audit(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "bad expression",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Failure recorded.",
            )

    loop = make_loop(tmp_path, DecisionMaker())

    result = loop.run(
        session=RivaSession(
            session_id="day13-audit",
        ),
        user_input="calculate",
    )

    assert len(result.executions) == 1
    assert result.executions[0].tool_name == "calculator"
    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None


def test_day13_successful_recovery_preserves_all_execution_history(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "bad expression",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "5 * 5",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Final answer: 25",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(
            session_id="day13-history",
        ),
        user_input="calculate 5 * 5",
    )

    assert len(result.executions) == 2

    assert result.executions[0].tool_name == "calculator"
    assert result.executions[0].status.value != "success"

    assert result.executions[1].tool_name == "calculator"
    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "25"

    assert result.response == "Final answer: 25"
