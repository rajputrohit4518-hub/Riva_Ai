
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
            MemoryStore(str(tmp_path / "day14.db"))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day14_failed_execution_is_followed_by_correction(tmp_path):
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
                response="Self-correction complete: 150",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(session_id="day14-correction"),
        user_input="calculate 25 * 6",
    )

    assert decision_maker.calls == 3
    assert len(result.executions) == 2

    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None

    assert result.executions[1].status.value == "success"
    assert result.executions[1].result == "150"

    assert result.response == "Self-correction complete: 150"


def test_day14_execution_history_is_preserved_after_recovery(tmp_path):
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
                        "expression": "10 + 5",
                    },
                )

            if self.calls == 3:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "15 * 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovery chain complete.",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(session_id="day14-history"),
        user_input="recover chain",
    )

    assert decision_maker.calls == 4
    assert len(result.executions) == 3

    assert result.executions[0].status.value != "success"
    assert result.executions[1].result == "15"
    assert result.executions[2].result == "30"

    assert all(
        execution.status.value == "success"
        for execution in result.executions[1:]
    )

    assert result.response == "Recovery chain complete."


def test_day14_success_requires_no_correction(tmp_path):
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
                        "expression": "12 + 8",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Verified: 20",
            )

    decision_maker = DecisionMaker()
    loop = make_loop(tmp_path, decision_maker)

    result = loop.run(
        session=RivaSession(session_id="day14-success"),
        user_input="calculate 12 + 8",
    )

    assert decision_maker.calls == 2
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"
    assert result.executions[0].result == "20"
    assert result.response == "Verified: 20"


def test_day14_recovery_does_not_hide_failure(tmp_path):
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

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Failure handled.",
            )

    loop = make_loop(tmp_path, DecisionMaker())

    result = loop.run(
        session=RivaSession(session_id="day14-failure-history"),
        user_input="calculate",
    )

    assert len(result.executions) == 1
    assert result.executions[0].status.value != "success"
    assert result.executions[0].error is not None
    assert result.response == "Failure handled."
