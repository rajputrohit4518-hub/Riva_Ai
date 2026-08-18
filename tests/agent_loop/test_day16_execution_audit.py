
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
            MemoryStore(str(tmp_path / "day16.db"))
        ),
    )

    return RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )


def test_day16_successful_execution_contains_audit_data(tmp_path):
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
                    tool_arguments={"expression": "25 * 6"},
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Done.",
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day16-success"),
        "calculate 25 * 6",
    )

    execution = result.executions[0]

    assert execution.execution_id
    assert execution.tool_name == "calculator"
    assert execution.status.value == "success"
    assert execution.result == "150"
    assert execution.error is None
    assert execution.completed_at is not None


def test_day16_failed_execution_contains_error_audit_data(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={"expression": "invalid arithmetic"},
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day16-failure"),
        "calculate invalid",
    )

    execution = result.executions[0]

    assert execution.execution_id
    assert execution.tool_name == "calculator"
    assert execution.status.value != "success"
    assert execution.error is not None
    assert "invalid arithmetic expression" in execution.error.lower()


def test_day16_execution_ids_are_unique(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls <= 3:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": f"{self.calls} + {self.calls}",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Complete.",
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day16-unique"),
        "run three calculations",
    )

    ids = [execution.execution_id for execution in result.executions]

    assert len(ids) == 3
    assert len(set(ids)) == 3


def test_day16_execution_order_is_preserved(tmp_path):
    class DecisionMaker:
        supports_multi_step = True

        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            if self.calls == 1:
                expression = "10 + 5"
            elif self.calls == 2:
                expression = "15 * 2"
            elif self.calls == 3:
                expression = "30 + 1"
            else:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response="Audit complete.",
                )

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={"expression": expression},
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day16-order"),
        "run audit sequence",
    )

    assert [e.result for e in result.executions] == [
        "15",
        "30",
        "31",
    ]

    assert all(
        e.completed_at is not None
        for e in result.executions
    )


def test_day16_recovery_keeps_failed_and_successful_audit_entries(tmp_path):
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
                        "expression": "12 + 8",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Recovered.",
            )

    result = make_loop(tmp_path, DecisionMaker()).run(
        RivaSession(session_id="day16-recovery"),
        "recover calculation",
    )

    assert len(result.executions) == 2

    failed, successful = result.executions

    assert failed.execution_id
    assert failed.status.value != "success"
    assert failed.error is not None

    assert successful.execution_id
    assert successful.status.value == "success"
    assert successful.result == "20"

    assert failed.execution_id != successful.execution_id
