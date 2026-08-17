from datetime import datetime, timezone
from app.core.identity import IDENTITY
from app.core.session import RivaSession
from app.agents.assistant import create_riva_agent
from app.tools.calculator import calculate_expression
from app.tools.defaults import create_default_registry
from app.tools.models import ToolDefinition
from app.tools.registry import ToolRegistry


def test_riva_identity():
    assert IDENTITY.name == "Riva"
    assert IDENTITY.version == "0.1.0"


def test_session():
    session = RivaSession(session_id="test-session")

    session.add_message("user", "Hello Riva")

    assert len(session.history()) == 1
    assert session.history()[0]["content"] == "Hello Riva"


def test_riva_agent():
    agent = create_riva_agent()

    assert agent.name == "Riva"


def test_calculator():
    result = calculate_expression("25 * 6")

    assert result == "150"


def test_registry():
    registry = create_default_registry()

    calculator = registry.get("calculator")

    assert calculator.name == "calculator"
    assert calculator.category == "utility"
    assert calculator.risk_level == "low"


def test_registry_execution():
    registry = create_default_registry()

    result = registry.execute(
        "calculator",
        expression="25 * 6",
    )

    assert result == "150"


def test_registry_duplicate_protection():
    registry = ToolRegistry()

    tool = ToolDefinition(
        name="test",
        description="Test tool",
        executor=lambda: "ok",
    )

    registry.register(tool)

    try:
        registry.register(tool)
        assert False, "Duplicate registration should fail"
    except ValueError:
        pass
 

def test_low_risk_tool_is_allowed():
    registry = create_default_registry()

    result = registry.execute(
        "calculator",
        expression="10 + 5",
    )

    assert result == "15"


def test_medium_risk_tool_requires_confirmation():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="medium_tool",
            description="Test medium-risk tool",
            executor=lambda: "executed",
            risk_level="medium",
        )
    )

    try:
        registry.execute("medium_tool")
        assert False, "Medium-risk tool should require confirmation"
    except PermissionError as exc:
        assert "Confirmation required" in str(exc)


def test_critical_tool_is_denied():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="dangerous_tool",
            description="Test critical tool",
            executor=lambda: "executed",
            risk_level="critical",
        )
    )

    try:
        registry.execute("dangerous_tool")
        assert False, "Critical tool should be denied"
    except PermissionError as exc:
        assert "execution denied" in str(exc)

from app.core.execution import ExecutionStatus
from app.core.executor import ExecutionEngine


def test_execution_engine_success():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    execution = engine.execute(
        "calculator",
        expression="25 * 6",
    )

    assert execution.status == ExecutionStatus.SUCCESS
    assert execution.tool_name == "calculator"
    assert execution.result == "150"
    assert execution.execution_id
    assert execution.completed_at is not None


def test_execution_engine_denied():
    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="dangerous_tool",
            description="Test dangerous tool",
            executor=lambda: "should not run",
            risk_level="critical",
        )
    )

    engine = ExecutionEngine(registry)

    execution = engine.execute("dangerous_tool")

    assert execution.status == ExecutionStatus.DENIED
    assert execution.error is not None
    assert execution.completed_at is not None

from pathlib import Path

from app.security.audit import AuditLogger


def test_audit_logger(tmp_path: Path):
    audit_path = tmp_path / "audit.jsonl"

    logger = AuditLogger(str(audit_path))

    event = logger.create_event(
        execution_id="test-execution",
        tool_name="calculator",
        status="success",
        result="150",
    )

    logger.record(event)

    assert audit_path.exists()

    lines = audit_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1
    assert "test-execution" in lines[0]
    assert "calculator" in lines[0]
    assert "success" in lines[0]

from app.memory.store import MemoryStore


def test_memory_save_and_get(tmp_path):
    database = tmp_path / "memory.db"

    store = MemoryStore(str(database))

    memory = store.save(
        key="preferred_language",
        value="Python",
        category="preference",
    )

    assert memory.key == "preferred_language"
    assert memory.value == "Python"

    loaded = store.get("preferred_language")

    assert loaded is not None
    assert loaded.value == "Python"
    assert loaded.category == "preference"


def test_memory_update(tmp_path):
    database = tmp_path / "memory.db"

    store = MemoryStore(str(database))

    store.save(
        key="favorite_color",
        value="blue",
        category="preference",
    )

    store.save(
        key="favorite_color",
        value="green",
        category="preference",
    )

    memory = store.get("favorite_color")

    assert memory is not None
    assert memory.value == "green"

    assert len(store.list_all()) == 1


def test_memory_delete(tmp_path):
    database = tmp_path / "memory.db"

    store = MemoryStore(str(database))

    store.save(
        key="temporary",
        value="test",
    )

    assert store.delete("temporary") is True
    assert store.get("temporary") is None

    assert store.delete("temporary") is False

from app.memory.manager import MemoryManager


def test_memory_manager_remember_and_recall(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    manager.remember(
        key="assistant_name",
        value="Riva",
        category="identity",
    )

    memory = manager.recall("assistant_name")

    assert memory is not None
    assert memory.value == "Riva"
    assert memory.category == "identity"


def test_memory_manager_forget(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    manager.remember(
        key="temporary",
        value="remove me",
    )

    assert manager.forget("temporary") is True
    assert manager.recall("temporary") is None


def test_memory_manager_rejects_empty_key(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    try:
        manager.remember("", "value")
        assert False, "Empty key should be rejected"
    except ValueError as exc:
        assert "key" in str(exc).lower()


def test_memory_manager_rejects_empty_value(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    try:
        manager.remember("key", "")
        assert False, "Empty value should be rejected"
    except ValueError as exc:
        assert "value" in str(exc).lower()

from app.memory.policy import (
    MemoryAction,
    MemoryCategory,
    MemoryPolicy,
)


def test_memory_policy_explicit_memory():
    policy = MemoryPolicy()

    decision = policy.evaluate(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    assert decision.action == MemoryAction.REMEMBER
    assert decision.category == MemoryCategory.PREFERENCE


def test_memory_policy_empty_data():
    policy = MemoryPolicy()

    decision = policy.evaluate(
        key="",
        value="",
    )

    assert decision.action == MemoryAction.IGNORE


def test_memory_policy_unknown_category():
    policy = MemoryPolicy()

    decision = policy.evaluate(
        key="something",
        value="important",
        category="unknown",
    )

    assert decision.action == MemoryAction.REMEMBER
    assert decision.category == MemoryCategory.GENERAL


def test_memory_manager_uses_policy(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        store=MemoryStore(str(database)),
        policy=MemoryPolicy(),
    )

    memory = manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    assert memory is not None
    assert memory.category == "preference"

def test_memory_search(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    manager.remember(
        key="favorite_editor",
        value="VS Code",
        category="preference",
    )

    results = manager.search("Python")

    assert len(results) == 1
    assert results[0].key == "favorite_language"


def test_memory_search_multiple_words(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    manager.remember(
        key="work_project",
        value="Riva personal AI assistant",
        category="project",
    )

    results = manager.search("personal AI")

    assert len(results) == 1
    assert results[0].key == "work_project"


def test_memory_search_empty_query(tmp_path):
    database = tmp_path / "memory.db"

    manager = MemoryManager(
        MemoryStore(str(database))
    )

    manager.remember(
        key="test",
        value="value",
    )

    assert manager.search("") == []

from app.context.engine import ContextEngine


def test_context_engine_builds_snapshot(tmp_path):
    database = tmp_path / "memory.db"

    memory_manager = MemoryManager(
        MemoryStore(str(database))
    )

    memory_manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    session = RivaSession(
        session_id="context-test"
    )

    session.add_message(
        "user",
        "What language do I prefer?"
    )

    engine = ContextEngine(memory_manager)

    context = engine.build(
        session=session,
        query="language Python",
    )

    assert context.session_id == "context-test"
    assert len(context.recent_messages) == 1
    assert len(context.memories) == 1
    assert context.memories[0].value == "Python"


def test_context_engine_empty_memory(tmp_path):
    database = tmp_path / "memory.db"

    memory_manager = MemoryManager(
        MemoryStore(str(database))
    )

    session = RivaSession(
        session_id="empty-context"
    )

    engine = ContextEngine(memory_manager)

    context = engine.build(
        session=session,
        query="something unknown",
    )

    assert context.session_id == "empty-context"
    assert context.recent_messages == []
    assert context.memories == []

from app.orchestration.orchestrator import RivaOrchestrator


def test_orchestrator_prepare(tmp_path):
    database = tmp_path / "memory.db"

    memory_manager = MemoryManager(
        MemoryStore(str(database))
    )

    memory_manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    registry = create_default_registry()

    orchestrator = RivaOrchestrator(
        registry=registry,
        memory_manager=memory_manager,
    )

    session = RivaSession(
        session_id="orchestration-test"
    )

    result = orchestrator.prepare(
        session=session,
        user_input="What language do I prefer?"
    )

    assert result.session_id == "orchestration-test"
    assert result.user_input == (
        "What language do I prefer?"
    )

    assert len(result.context.recent_messages) == 1


def test_orchestrator_tool_execution(tmp_path):
    database = tmp_path / "memory.db"

    memory_manager = MemoryManager(
        MemoryStore(str(database))
    )

    registry = create_default_registry()

    orchestrator = RivaOrchestrator(
        registry=registry,
        memory_manager=memory_manager,
    )

    session = RivaSession(
        session_id="tool-test"
    )

    result = orchestrator.prepare(
        session=session,
        user_input="Calculate 25 * 6"
    )

    result = orchestrator.execute_tool(
        result,
        "calculator",
        expression="25 * 6",
    )

    assert len(result.executions) == 1
    assert result.executions[0].result == "150"


def test_orchestrator_response(tmp_path):
    database = tmp_path / "memory.db"

    registry = create_default_registry()

    orchestrator = RivaOrchestrator(
        registry=registry,
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    session = RivaSession(
        session_id="response-test"
    )

    result = orchestrator.prepare(
        session=session,
        user_input="Hello Riva",
    )

    result = orchestrator.respond(
        result,
        "Hello! How can I help?",
    )

    assert result.response == (
        "Hello! How can I help?"
    )


def test_orchestrator_rejects_empty_input(tmp_path):
    database = tmp_path / "memory.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    session = RivaSession(
        session_id="empty-test"
    )

    try:
        orchestrator.prepare(
            session=session,
            user_input="   ",
        )

        assert False, (
            "Empty input should be rejected"
        )

    except ValueError as exc:
        assert "input" in str(exc).lower()

from app.agent_loop.decision import DecisionMaker
from app.agent_loop.loop import RivaAgentLoop
from app.agent_loop.models import AgentDecision, DecisionType
from app.agent_loop.models import DecisionType


def test_decision_maker_calculator():
    maker = DecisionMaker()

    decision = maker.decide(
        "Calculate 25 * 6"
    )

    assert decision.decision_type == DecisionType.USE_TOOL
    assert decision.tool_name == "calculator"
    assert decision.tool_arguments == {
        "expression": "25 * 6"
    }


def test_decision_maker_greeting():
    maker = DecisionMaker()

    decision = maker.decide("Hello Riva")

    assert decision.decision_type == DecisionType.RESPOND
    assert decision.response is not None


def test_agent_loop_calculator(tmp_path):
    database = tmp_path / "memory.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-loop-test"
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response == "150"
    assert len(result.executions) == 1
    assert result.executions[0].result == "150"


def test_agent_loop_greeting(tmp_path):
    database = tmp_path / "memory.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="greeting-test"
    )

    result = loop.run(
        session=session,
        user_input="Hello Riva",
    )

    assert "Hello" in result.response
    assert result.executions == []

from app.planner.models import PlanStepType
from app.planner.planner import RivaPlanner


def test_planner_calculator():
    planner = RivaPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 6"
    )

    assert plan.goal == "Calculate 25 * 6"
    assert len(plan.steps) == 2

    assert plan.steps[0].step_type == PlanStepType.TOOL
    assert plan.steps[0].tool_name == "calculator"
    assert plan.steps[0].arguments == {
        "expression": "25 * 6"
    }

    assert plan.steps[1].step_type == PlanStepType.VERIFY


def test_planner_response():
    planner = RivaPlanner()

    plan = planner.create_plan(
        "Hello Riva"
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].step_type == PlanStepType.RESPOND


def test_planner_rejects_empty_input():
    planner = RivaPlanner()

    try:
        planner.create_plan("   ")
        assert False, "Empty input should fail"
    except ValueError as exc:
        assert "input" in str(exc).lower()

from app.planner.executor import PlanExecutor


def test_plan_executor_calculator():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    planner = RivaPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 6"
    )

    executor = PlanExecutor(engine)

    result = executor.execute(plan)

    assert result.success is True
    assert result.outputs[0] == "150"
    assert result.outputs[1] == "Verified: 150"


def test_plan_executor_response():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    planner = RivaPlanner()

    plan = planner.create_plan(
        "Hello Riva"
    )

    result = PlanExecutor(engine).execute(plan)

    assert result.success is True
    assert len(result.outputs) == 1


def test_plan_executor_missing_tool():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    plan = ExecutionPlan(
        goal="bad plan",
        steps=[
            PlanStep(
                step_id="step_1",
                step_type=PlanStepType.TOOL,
                description="Missing tool",
            )
        ],
    )

    result = PlanExecutor(engine).execute(plan)

    assert result.success is False
    assert "missing tool" in result.error.lower()

from app.planner.models import ExecutionPlan, PlanStep

from app.verification.correction import SelfCorrector
from app.verification.models import VerificationStatus
from app.verification.verifier import ResultVerifier


def test_result_verifier_success():
    verifier = ResultVerifier()

    result = verifier.verify("150")

    assert result.status == VerificationStatus.PASSED


def test_result_verifier_empty_result():
    verifier = ResultVerifier()

    result = verifier.verify("")

    assert result.status == VerificationStatus.FAILED


def test_result_verifier_none_result():
    verifier = ResultVerifier()

    result = verifier.verify(None)

    assert result.status == VerificationStatus.FAILED


def test_self_corrector_success():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    planner = RivaPlanner()

    plan = planner.create_plan(
        "Calculate 25 * 6"
    )

    executor = PlanExecutor(engine)

    corrector = SelfCorrector(
        executor=executor,
        max_attempts=2,
    )

    result = corrector.run(plan)

    assert result.success is True
    assert result.attempts == 1
    assert "150" in result.outputs


def test_self_corrector_rejects_invalid_attempt_limit():
    registry = create_default_registry()
    engine = ExecutionEngine(registry)

    executor = PlanExecutor(engine)

    try:
        SelfCorrector(
            executor=executor,
            max_attempts=0,
        )

        assert False, (
            "Invalid attempt limit should fail"
        )

    except ValueError as exc:
        assert "max_attempts" in str(exc)

from app.brain.models import (
    BrainDecision,
    BrainDecisionType,
)


def test_brain_decision_response():
    decision = BrainDecision(
        decision_type=BrainDecisionType.RESPOND,
        response="Hello!",
    )

    assert decision.decision_type == (
        BrainDecisionType.RESPOND
    )

    assert decision.response == "Hello!"


def test_brain_decision_tool():
    decision = BrainDecision(
        decision_type=BrainDecisionType.TOOL,
        tool_name="calculator",
        tool_arguments={
            "expression": "25 * 6",
        },
    )

    assert decision.decision_type == (
        BrainDecisionType.TOOL
    )

    assert decision.tool_name == "calculator"

    assert decision.tool_arguments == {
        "expression": "25 * 6",
    }


def test_brain_decision_default_arguments():
    decision = BrainDecision(
        decision_type=BrainDecisionType.RESPOND,
    )

    assert decision.tool_arguments == {}

from app.brain.gateway import BrainGateway


def test_brain_gateway_accepts_response():
    registry = create_default_registry()

    gateway = BrainGateway(registry)

    decision = BrainDecision(
        decision_type=BrainDecisionType.RESPOND,
        response="Hello!",
    )

    result = gateway.validate(decision)

    assert result == decision


def test_brain_gateway_accepts_known_tool():
    registry = create_default_registry()

    gateway = BrainGateway(registry)

    decision = BrainDecision(
        decision_type=BrainDecisionType.TOOL,
        tool_name="calculator",
        tool_arguments={
            "expression": "25 * 6",
        },
    )

    result = gateway.validate(decision)

    assert result == decision


def test_brain_gateway_rejects_unknown_tool():
    registry = create_default_registry()

    gateway = BrainGateway(registry)

    decision = BrainDecision(
        decision_type=BrainDecisionType.TOOL,
        tool_name="destroy_computer",
    )

    try:
        gateway.validate(decision)
        assert False, "Unknown tool should be rejected"
    except ValueError as exc:
        assert "unknown tool" in str(exc).lower()


def test_brain_gateway_rejects_missing_response():
    registry = create_default_registry()

    gateway = BrainGateway(registry)

    decision = BrainDecision(
        decision_type=BrainDecisionType.RESPOND,
    )

    try:
        gateway.validate(decision)
        assert False, "Empty response should be rejected"
    except ValueError as exc:
        assert "response" in str(exc).lower()


def test_brain_gateway_rejects_tool_with_response():
    registry = create_default_registry()

    gateway = BrainGateway(registry)

    decision = BrainDecision(
        decision_type=BrainDecisionType.TOOL,
        tool_name="calculator",
        response="I calculated it.",
    )

    try:
        gateway.validate(decision)
        assert False, (
            "Tool decision with response should fail"
        )
    except ValueError as exc:
        assert "response" in str(exc).lower()

from app.runtime.runtime import RivaRuntime


def test_runtime_calculator(tmp_path):
    database = tmp_path / "memory.db"

    memory = MemoryManager(
        MemoryStore(str(database))
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="runtime-calculator"
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.success is True
    assert result.response == "Verified: 150"
    assert "150" in result.tool_outputs


def test_runtime_empty_input(tmp_path):
    database = tmp_path / "memory.db"

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    session = RivaSession(
        session_id="runtime-empty"
    )

    try:
        runtime.handle(
            session=session,
            user_input="   ",
        )

        assert False, (
            "Empty runtime input should fail"
        )

    except ValueError as exc:
        assert "input" in str(exc).lower()


def test_runtime_session_is_preserved(tmp_path):
    database = tmp_path / "memory.db"

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    session = RivaSession(
        session_id="runtime-session"
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 10 + 5",
    )

    assert result.session_id == "runtime-session"
    assert result.user_input == "Calculate 10 + 5"

from app.capabilities.models import (
    Capability,
    PermissionLevel,
)
from app.capabilities.policy import CapabilityPolicy
from app.capabilities.registry import CapabilityRegistry


def test_capability_registry_registers_capability():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculator",
        description="Performs calculations.",
        permission=PermissionLevel.NONE,
        execute=lambda expression: "150",
    )

    registry.register(capability)

    assert registry.has("calculator") is True
    assert registry.get("calculator") == capability


def test_capability_registry_names():
    registry = CapabilityRegistry()

    registry.register(
        Capability(
            name="web",
            description="Web access.",
            permission=PermissionLevel.CONFIRM,
            execute=lambda: None,
        )
    )

    registry.register(
        Capability(
            name="calculator",
            description="Calculations.",
            permission=PermissionLevel.NONE,
            execute=lambda: None,
        )
    )

    assert registry.names() == [
        "calculator",
        "web",
    ]


def test_capability_registry_rejects_duplicate():
    registry = CapabilityRegistry()

    capability = Capability(
        name="calculator",
        description="Calculations.",
        permission=PermissionLevel.NONE,
        execute=lambda: None,
    )

    registry.register(capability)

    try:
        registry.register(capability)
        assert False, (
            "Duplicate capability should fail"
        )
    except ValueError as exc:
        assert "already registered" in str(exc)


def test_capability_policy_none():
    policy = CapabilityPolicy()

    capability = Capability(
        name="calculator",
        description="Calculations.",
        permission=PermissionLevel.NONE,
        execute=lambda: None,
    )

    assert policy.can_execute(
        capability
    ) is True


def test_capability_policy_confirmation():
    policy = CapabilityPolicy()

    capability = Capability(
        name="browser",
        description="Browser access.",
        permission=PermissionLevel.CONFIRM,
        execute=lambda: None,
    )

    assert policy.can_execute(
        capability,
        confirmed=False,
    ) is False

    assert policy.can_execute(
        capability,
        confirmed=True,
    ) is True


def test_capability_policy_elevated_blocked():
    policy = CapabilityPolicy()

    capability = Capability(
        name="system_admin",
        description="Administrative system access.",
        permission=PermissionLevel.ELEVATED,
        execute=lambda: None,
    )

    assert policy.can_execute(
        capability,
        confirmed=True,
    ) is False

from app.capabilities.adapter import CapabilityAdapter


def test_capability_adapter_exposes_calculator():
    tools = create_default_registry()
    capabilities = CapabilityRegistry()

    adapter = CapabilityAdapter(
        tool_registry=tools,
        capability_registry=capabilities,
    )

    capability = adapter.expose_tool(
        "calculator"
    )

    assert capability.name == "calculator"
    assert capabilities.has("calculator") is True


def test_capability_adapter_preserves_permission():
    tools = create_default_registry()
    capabilities = CapabilityRegistry()

    adapter = CapabilityAdapter(
        tool_registry=tools,
        capability_registry=capabilities,
    )

    capability = adapter.expose_tool(
        "calculator",
        permission=PermissionLevel.CONFIRM,
    )

    assert capability.permission == (
        PermissionLevel.CONFIRM
    )


def test_capability_adapter_unknown_tool():
    tools = create_default_registry()
    capabilities = CapabilityRegistry()

    adapter = CapabilityAdapter(
        tool_registry=tools,
        capability_registry=capabilities,
    )

    try:
        adapter.expose_tool(
            "does_not_exist"
        )

        assert False, (
            "Unknown tool should be rejected"
        )

    except ValueError as exc:
        assert "unknown tool" in str(exc).lower()


def test_capability_adapter_expose_all():
    tools = create_default_registry()
    capabilities = CapabilityRegistry()

    adapter = CapabilityAdapter(
        tool_registry=tools,
        capability_registry=capabilities,
    )

    exposed = adapter.expose_all()

    assert len(exposed) == len(tools.list())

    for capability in exposed:
        assert capabilities.has(
            capability.name
        )


from app.desktop.catalog import DesktopApplicationCatalog
from app.desktop.models import DesktopActionResult
from app.desktop.verifier import DesktopVerifier


def test_desktop_catalog_has_safe_applications():
    catalog = DesktopApplicationCatalog()

    assert "notepad" in catalog.names()
    assert "calculator" in catalog.names()


def test_desktop_catalog_rejects_unknown_application():
    catalog = DesktopApplicationCatalog()

    result = catalog.find(
        "definitely_not_allowed"
    )

    assert result is None


def test_desktop_action_result_success():
    result = DesktopActionResult(
        success=True,
        application="notepad",
        message="Application launched.",
        pid=1234,
    )

    assert result.success is True
    assert result.pid == 1234


def test_desktop_verifier_rejects_missing_pid():
    verifier = DesktopVerifier()

    result = DesktopActionResult(
        success=True,
        application="notepad",
        message="Application launched.",
        pid=None,
    )

    verified = verifier.verify(result)

    assert verified.success is False
    assert "process ID" in verified.message

from app.desktop.capability import DesktopCapability


def test_desktop_capability_definition():
    desktop = DesktopCapability()

    capability = desktop.capability()

    assert capability.name == "desktop.launch"
    assert capability.permission == (
        PermissionLevel.CONFIRM
    )
    assert callable(capability.execute)


def test_desktop_capability_custom_permission():
    desktop = DesktopCapability()

    capability = desktop.capability(
        permission=PermissionLevel.NONE
    )

    assert capability.permission == (
        PermissionLevel.NONE
    )


def test_desktop_capability_unknown_application():
    desktop = DesktopCapability()

    result = desktop.launch(
        "definitely_not_allowed"
    )

    assert result.success is False
    assert "not allowed" in result.message.lower()

from app.devices.models import (
    Device,
    DeviceType,
)
from app.devices.registry import DeviceRegistry
from app.devices.resolver import DeviceResolver


def test_device_registry_registers_device():
    registry = DeviceRegistry()

    device = Device(
        device_id="desktop-main",
        name="Riva Desktop",
        device_type=DeviceType.DESKTOP,
    )

    registry.register(device)

    assert registry.get(
        "desktop-main"
    ) == device


def test_device_registry_rejects_duplicate():
    registry = DeviceRegistry()

    device = Device(
        device_id="desktop-main",
        name="Riva Desktop",
        device_type=DeviceType.DESKTOP,
    )

    registry.register(device)

    try:
        registry.register(device)
        assert False, (
            "Duplicate device should fail"
        )
    except ValueError as exc:
        assert "already registered" in str(exc)


def test_device_registry_online():
    registry = DeviceRegistry()

    registry.register(
        Device(
            device_id="desktop-main",
            name="Desktop",
            device_type=DeviceType.DESKTOP,
            online=True,
        )
    )

    registry.register(
        Device(
            device_id="phone-main",
            name="Phone",
            device_type=DeviceType.PHONE,
            online=False,
        )
    )

    online = registry.online()

    assert len(online) == 1
    assert online[0].device_id == "desktop-main"


def test_device_resolver_by_type():
    registry = DeviceRegistry()

    device = Device(
        device_id="desktop-main",
        name="Desktop",
        device_type=DeviceType.DESKTOP,
    )

    registry.register(device)

    resolver = DeviceResolver(registry)

    result = resolver.resolve(
        DeviceType.DESKTOP
    )

    assert result == device


def test_device_resolver_missing_type():
    registry = DeviceRegistry()

    resolver = DeviceResolver(registry)

    result = resolver.resolve(
        DeviceType.PHONE
    )

    assert result is None


def test_device_resolver_rejects_offline_device():
    registry = DeviceRegistry()

    registry.register(
        Device(
            device_id="phone-main",
            name="Phone",
            device_type=DeviceType.PHONE,
            online=False,
        )
    )

    resolver = DeviceResolver(registry)

    try:
        resolver.resolve_by_id(
            "phone-main"
        )

        assert False, (
            "Offline device should be rejected"
        )

    except RuntimeError as exc:
        assert "offline" in str(exc).lower()

from app.devices.router import DeviceCapabilityRouter
from app.devices.routing import RoutingDecision


def test_device_capability_router_routes_to_desktop():
    registry = DeviceRegistry()

    desktop = Device(
        device_id="desktop-main",
        name="Riva Desktop",
        device_type=DeviceType.DESKTOP,
        online=True,
    )

    registry.register(desktop)

    resolver = DeviceResolver(registry)

    router = DeviceCapabilityRouter(
        resolver
    )

    capability = Capability(
        name="desktop.launch",
        description="Launch desktop application.",
        permission=PermissionLevel.CONFIRM,
        execute=lambda application: None,
    )

    result = router.route(
        capability,
        DeviceType.DESKTOP,
    )

    assert result == desktop


def test_device_capability_router_rejects_missing_device():
    registry = DeviceRegistry()

    resolver = DeviceResolver(registry)

    router = DeviceCapabilityRouter(
        resolver
    )

    capability = Capability(
        name="phone.media",
        description="Play media.",
        permission=PermissionLevel.NONE,
        execute=lambda: None,
    )

    try:
        router.route(
            capability,
            DeviceType.PHONE,
        )

        assert False, (
            "Missing device should fail"
        )

    except RuntimeError as exc:
        assert "no online device" in str(
            exc
        ).lower()


def test_device_capability_router_routes_by_id():
    registry = DeviceRegistry()

    phone = Device(
        device_id="phone-main",
        name="Riva Phone",
        device_type=DeviceType.PHONE,
        online=True,
    )

    registry.register(phone)

    resolver = DeviceResolver(registry)

    router = DeviceCapabilityRouter(
        resolver
    )

    capability = Capability(
        name="phone.notification",
        description="Send notification.",
        permission=PermissionLevel.NONE,
        execute=lambda: None,
    )

    result = router.route_by_device(
        capability,
        "phone-main",
    )

    assert result == phone


def test_routing_decision():
    device = Device(
        device_id="desktop-main",
        name="Desktop",
        device_type=DeviceType.DESKTOP,
    )

    decision = RoutingDecision(
        capability_name="desktop.launch",
        device=device,
    )

    assert decision.capability_name == (
        "desktop.launch"
    )

    assert decision.device == device

from app.devices.identity import DeviceIdentity
from app.devices.trust import DeviceTrustManager


def test_device_identity_registration():
    manager = DeviceTrustManager()

    identity = DeviceIdentity(
        device_id="desktop-main",
        owner_id="riva-user",
        fingerprint="desktop-fingerprint-001",
    )

    manager.register_identity(identity)

    assert manager.get_identity(
        "desktop-main"
    ) == identity


def test_device_identity_starts_untrusted():
    manager = DeviceTrustManager()

    manager.register_identity(
        DeviceIdentity(
            device_id="phone-main",
            owner_id="riva-user",
            fingerprint="phone-fingerprint-001",
        )
    )

    assert manager.is_trusted(
        "phone-main"
    ) is False


def test_device_can_be_trusted():
    manager = DeviceTrustManager()

    manager.register_identity(
        DeviceIdentity(
            device_id="phone-main",
            owner_id="riva-user",
            fingerprint="phone-fingerprint-001",
        )
    )

    manager.trust("phone-main")

    assert manager.is_trusted(
        "phone-main"
    ) is True


def test_device_trust_can_be_revoked():
    manager = DeviceTrustManager()

    manager.register_identity(
        DeviceIdentity(
            device_id="phone-main",
            owner_id="riva-user",
            fingerprint="phone-fingerprint-001",
        )
    )

    manager.trust("phone-main")
    manager.revoke("phone-main")

    assert manager.is_trusted(
        "phone-main"
    ) is False


def test_unknown_device_is_not_trusted():
    manager = DeviceTrustManager()

    assert manager.is_trusted(
        "unknown-device"
    ) is False


def test_device_identity_rejects_empty_device_id():
    manager = DeviceTrustManager()

    try:
        manager.register_identity(
            DeviceIdentity(
                device_id="",
                owner_id="riva-user",
                fingerprint="fingerprint",
            )
        )

        assert False, (
            "Empty device ID should fail"
        )

    except ValueError as exc:
        assert "device id" in str(exc).lower()


def test_device_identity_rejects_empty_fingerprint():
    manager = DeviceTrustManager()

    try:
        manager.register_identity(
            DeviceIdentity(
                device_id="desktop-main",
                owner_id="riva-user",
                fingerprint="",
            )
        )

        assert False, (
            "Empty fingerprint should fail"
        )

    except ValueError as exc:
        assert "fingerprint" in str(exc).lower()

from app.devices.pairing import DevicePairingManager


def test_pairing_request_creation():
    trust = DeviceTrustManager()

    pairing = DevicePairingManager(
        trust_manager=trust,
    )

    request = pairing.create_request(
        device_id="phone-main",
        owner_id="riva-user",
        fingerprint="phone-fingerprint",
    )

    assert request.device_id == "phone-main"
    assert len(request.code) == 6
    assert request.completed is False


def test_pairing_success():
    trust = DeviceTrustManager()

    pairing = DevicePairingManager(
        trust_manager=trust,
    )

    request = pairing.create_request(
        device_id="phone-main",
        owner_id="riva-user",
        fingerprint="phone-fingerprint",
    )

    result = pairing.confirm(
        request.request_id,
        request.code,
    )

    assert result.success is True
    assert result.device_id == "phone-main"
    assert trust.is_trusted(
        "phone-main"
    ) is True


def test_pairing_rejects_wrong_code():
    trust = DeviceTrustManager()

    pairing = DevicePairingManager(
        trust_manager=trust,
    )

    request = pairing.create_request(
        device_id="phone-main",
        owner_id="riva-user",
        fingerprint="phone-fingerprint",
    )

    result = pairing.confirm(
        request.request_id,
        "000000",
    )

    assert result.success is False
    assert "invalid" in result.message.lower()
    assert trust.is_trusted(
        "phone-main"
    ) is False


def test_pairing_rejects_unknown_request():
    trust = DeviceTrustManager()

    pairing = DevicePairingManager(
        trust_manager=trust,
    )

    result = pairing.confirm(
        "missing-request",
        "123456",
    )

    assert result.success is False
    assert "not found" in result.message.lower()


def test_pairing_cannot_be_completed_twice():
    trust = DeviceTrustManager()

    pairing = DevicePairingManager(
        trust_manager=trust,
    )

    request = pairing.create_request(
        device_id="phone-main",
        owner_id="riva-user",
        fingerprint="phone-fingerprint",
    )

    first = pairing.confirm(
        request.request_id,
        request.code,
    )

    second = pairing.confirm(
        request.request_id,
        request.code,
    )

    assert first.success is True
    assert second.success is False
    assert "completed" in second.message.lower()


def test_pairing_ttl_must_be_positive():
    trust = DeviceTrustManager()

    try:
        DevicePairingManager(
            trust_manager=trust,
            ttl_seconds=0,
        )

        assert False, (
            "Invalid TTL should fail"
        )

    except ValueError as exc:
        assert "ttl" in str(exc).lower()

from app.devices.sessions import DeviceSessionManager


def test_untrusted_device_cannot_connect():
    trust = DeviceTrustManager()
    sessions = DeviceSessionManager(trust)

    result = sessions.connect(
        "unknown-device"
    )

    assert result.success is False
    assert "not trusted" in result.message.lower()


def test_trusted_device_can_connect():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="desktop-main",
            owner_id="riva-user",
            fingerprint="desktop-fingerprint",
        )
    )

    trust.trust("desktop-main")

    sessions = DeviceSessionManager(trust)

    result = sessions.connect(
        "desktop-main"
    )

    assert result.success is True
    assert result.device_id == "desktop-main"
    assert result.session_id


def test_session_heartbeat():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="phone-main",
            owner_id="riva-user",
            fingerprint="phone-fingerprint",
        )
    )

    trust.trust("phone-main")

    sessions = DeviceSessionManager(trust)

    connected = sessions.connect(
        "phone-main"
    )

    heartbeat = sessions.heartbeat(
        connected.session_id
    )

    assert heartbeat.success is True
    assert "heartbeat" in heartbeat.message.lower()


def test_session_disconnect():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="phone-main",
            owner_id="riva-user",
            fingerprint="phone-fingerprint",
        )
    )

    trust.trust("phone-main")

    sessions = DeviceSessionManager(trust)

    connected = sessions.connect(
        "phone-main"
    )

    result = sessions.disconnect(
        connected.session_id
    )

    assert result.success is True
    assert sessions.is_connected(
        "phone-main"
    ) is False


def test_active_sessions():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="desktop-main",
            owner_id="riva-user",
            fingerprint="desktop-fingerprint",
        )
    )

    trust.trust("desktop-main")

    sessions = DeviceSessionManager(trust)

    sessions.connect("desktop-main")

    active = sessions.active_sessions()

    assert len(active) == 1
    assert active[0].device_id == "desktop-main"
    assert active[0].active is True


def test_disconnected_session_is_not_active():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="desktop-main",
            owner_id="riva-user",
            fingerprint="desktop-fingerprint",
        )
    )

    trust.trust("desktop-main")

    sessions = DeviceSessionManager(trust)

    connected = sessions.connect(
        "desktop-main"
    )

    sessions.disconnect(
        connected.session_id
    )

    assert sessions.active_sessions() == []

from app.devices.events import DeviceEvent
from app.devices.event_bus import DeviceEventBus
from app.devices.event_router import DeviceEventRouter


def test_device_event_creation():
    event = DeviceEvent.create(
        event_type="device.connected",
        source_device_id="desktop-main",
        payload={
            "name": "Riva Desktop",
        },
    )

    assert event.event_id
    assert event.event_type == (
        "device.connected"
    )
    assert event.source_device_id == (
        "desktop-main"
    )
    assert event.target_device_id is None
    assert event.payload["name"] == (
        "Riva Desktop"
    )


def test_device_event_can_target_device():
    event = DeviceEvent.create(
        event_type="command.request",
        source_device_id="desktop-main",
        target_device_id="phone-main",
        payload={
            "command": "notify",
        },
    )

    assert event.target_device_id == (
        "phone-main"
    )


def test_event_bus_delivers_event():
    bus = DeviceEventBus()

    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(
        "device.connected",
        handler,
    )

    event = DeviceEvent.create(
        event_type="device.connected",
        source_device_id="desktop-main",
        payload={},
    )

    bus.publish(event)

    assert len(received) == 1
    assert received[0] == event


def test_event_bus_does_not_deliver_other_event_types():
    bus = DeviceEventBus()

    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(
        "device.connected",
        handler,
    )

    bus.publish(
        DeviceEvent.create(
            event_type="device.disconnected",
            source_device_id="desktop-main",
            payload={},
        )
    )

    assert received == []


def test_event_bus_unsubscribe():
    bus = DeviceEventBus()

    received = []

    def handler(event):
        received.append(event)

    bus.subscribe(
        "device.connected",
        handler,
    )

    bus.unsubscribe(
        "device.connected",
        handler,
    )

    bus.publish(
        DeviceEvent.create(
            event_type="device.connected",
            source_device_id="desktop-main",
            payload={},
        )
    )

    assert received == []


def test_event_bus_history():
    bus = DeviceEventBus()

    event = DeviceEvent.create(
        event_type="test.event",
        source_device_id="desktop-main",
        payload={"value": 42},
    )

    bus.publish(event)

    history = bus.history()

    assert len(history) == 1
    assert history[0] == event


def test_event_bus_history_is_copy():
    bus = DeviceEventBus()

    event = DeviceEvent.create(
        event_type="test.event",
        source_device_id="desktop-main",
        payload={},
    )

    bus.publish(event)

    history = bus.history()
    history.clear()

    assert len(bus.history()) == 1


def test_event_bus_rejects_empty_event_type():
    bus = DeviceEventBus()

    try:
        bus.subscribe(
            "",
            lambda event: None,
        )

        assert False, (
            "Empty event type should fail"
        )

    except ValueError as exc:
        assert "event type" in str(exc).lower()


def test_event_router_publishes_to_bus():
    bus = DeviceEventBus()
    router = DeviceEventRouter(bus)

    received = []

    bus.subscribe(
        "test.command",
        received.append,
    )

    event = DeviceEvent.create(
        event_type="test.command",
        source_device_id="desktop-main",
        payload={
            "command": "hello",
        },
    )

    router.publish(event)

    assert received == [event]

from app.devices.authorization import EventAuthorization
from app.devices.event_authorizer import DeviceEventAuthorizer


def create_trusted_device_session():
    trust = DeviceTrustManager()

    trust.register_identity(
        DeviceIdentity(
            device_id="desktop-main",
            owner_id="riva-user",
            fingerprint="desktop-fingerprint",
        )
    )

    trust.trust("desktop-main")

    sessions = DeviceSessionManager(trust)

    connection = sessions.connect(
        "desktop-main"
    )

    assert connection.success is True

    return trust, sessions


def test_event_authorizer_rejects_unknown_device():
    trust = DeviceTrustManager()
    sessions = DeviceSessionManager(trust)

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    event = DeviceEvent.create(
        event_type="test.event",
        source_device_id="unknown-device",
        payload={},
    )

    result = authorizer.authorize(event)

    assert result.decision == (
        EventAuthorization.DENY
    )
    assert "trusted" in result.reason.lower()


def test_event_authorizer_rejects_disconnected_device():
    trust = DeviceTrustManager()
    sessions = DeviceSessionManager(trust)

    trust.register_identity(
        DeviceIdentity(
            device_id="desktop-main",
            owner_id="riva-user",
            fingerprint="desktop-fingerprint",
        )
    )

    trust.trust("desktop-main")

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    event = DeviceEvent.create(
        event_type="test.event",
        source_device_id="desktop-main",
        payload={},
    )

    result = authorizer.authorize(event)

    assert result.decision == (
        EventAuthorization.DENY
    )
    assert "session" in result.reason.lower()


def test_event_authorizer_rejects_unauthorized_event():
    trust, sessions = (
        create_trusted_device_session()
    )

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    event = DeviceEvent.create(
        event_type="dangerous.command",
        source_device_id="desktop-main",
        payload={},
    )

    result = authorizer.authorize(event)

    assert result.decision == (
        EventAuthorization.DENY
    )
    assert "authorized" in result.reason.lower()


def test_event_authorizer_allows_authorized_event():
    trust, sessions = (
        create_trusted_device_session()
    )

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    authorizer.allow(
        "desktop-main",
        "device.status",
    )

    event = DeviceEvent.create(
        event_type="device.status",
        source_device_id="desktop-main",
        payload={
            "status": "ready",
        },
    )

    result = authorizer.authorize(event)

    assert result.decision == (
        EventAuthorization.ALLOW
    )


def test_event_authorizer_revoke():
    trust, sessions = (
        create_trusted_device_session()
    )

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    authorizer.allow(
        "desktop-main",
        "device.status",
    )

    authorizer.revoke(
        "desktop-main",
        "device.status",
    )

    event = DeviceEvent.create(
        event_type="device.status",
        source_device_id="desktop-main",
        payload={},
    )

    result = authorizer.authorize(event)

    assert result.decision == (
        EventAuthorization.DENY
    )


def test_event_authorizer_rejects_empty_device_id():
    trust = DeviceTrustManager()
    sessions = DeviceSessionManager(trust)

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    try:
        authorizer.allow(
            "",
            "device.status",
        )

        assert False, (
            "Empty device ID should fail"
        )

    except ValueError as exc:
        assert "device id" in str(exc).lower()


def test_event_authorizer_rejects_empty_event_type():
    trust = DeviceTrustManager()
    sessions = DeviceSessionManager(trust)

    authorizer = DeviceEventAuthorizer(
        trust,
        sessions,
    )

    try:
        authorizer.allow(
            "desktop-main",
            "",
        )

        assert False, (
            "Empty event type should fail"
        )

    except ValueError as exc:
        assert "event type" in str(exc).lower()

import uuid

from app.capabilities.registry import CapabilityRegistry
from app.command_router import UnifiedCommandRouter
from app.core_command_models import CommandRequest


def test_unified_command_router_routes_command():
    capability_registry = CapabilityRegistry()

    executed = []

    capability = Capability(
        name="test.command",
        description="Test command.",
        permission=PermissionLevel.NONE,
        execute=lambda value: executed.append(value)
        or "done",
    )

    capability_registry.register(
        capability
    )

    device_registry = DeviceRegistry()

    device_registry.register(
        Device(
            device_id="desktop-main",
            name="Desktop",
            device_type=DeviceType.DESKTOP,
            online=True,
        )
    )

    resolver = DeviceResolver(
        device_registry
    )

    device_router = DeviceCapabilityRouter(
        resolver
    )

    router = UnifiedCommandRouter(
        capabilities=capability_registry,
        devices=device_router,
    )

    request = CommandRequest(
        command_id=str(uuid.uuid4()),
        capability_name="test.command",
        device_type=DeviceType.DESKTOP,
        arguments={
            "value": "hello",
        },
    )

    result = router.execute(request)

    assert result.success is True
    assert result.device_id == (
        "desktop-main"
    )
    assert executed == ["hello"]


def test_unified_command_router_missing_capability():
    capabilities = CapabilityRegistry()

    devices = DeviceRegistry()

    devices.register(
        Device(
            device_id="desktop-main",
            name="Desktop",
            device_type=DeviceType.DESKTOP,
        )
    )

    router = UnifiedCommandRouter(
        capabilities=capabilities,
        devices=DeviceCapabilityRouter(
            DeviceResolver(devices)
        ),
    )

    request = CommandRequest(
        command_id="command-1",
        capability_name="missing.capability",
        device_type=DeviceType.DESKTOP,
        arguments={},
    )

    result = router.execute(request)

    assert result.success is False
    assert "not found" in result.message.lower()


def test_unified_command_router_missing_device():
    capabilities = CapabilityRegistry()

    capabilities.register(
        Capability(
            name="phone.command",
            description="Phone command.",
            permission=PermissionLevel.NONE,
            execute=lambda: "done",
        )
    )

    devices = DeviceRegistry()

    router = UnifiedCommandRouter(
        capabilities=capabilities,
        devices=DeviceCapabilityRouter(
            DeviceResolver(devices)
        ),
    )

    request = CommandRequest(
        command_id="command-2",
        capability_name="phone.command",
        device_type=DeviceType.PHONE,
        arguments={},
    )

    result = router.execute(request)

    assert result.success is False
    assert "no online device" in (
        result.message.lower()
    )


def test_unified_command_router_execution_failure():
    capabilities = CapabilityRegistry()

    def failing_command():
        raise RuntimeError(
            "test failure"
        )

    capabilities.register(
        Capability(
            name="test.failure",
            description="Failure test.",
            permission=PermissionLevel.NONE,
            execute=failing_command,
        )
    )

    devices = DeviceRegistry()

    devices.register(
        Device(
            device_id="desktop-main",
            name="Desktop",
            device_type=DeviceType.DESKTOP,
        )
    )

    router = UnifiedCommandRouter(
        capabilities=capabilities,
        devices=DeviceCapabilityRouter(
            DeviceResolver(devices)
        ),
    )

    request = CommandRequest(
        command_id="command-3",
        capability_name="test.failure",
        device_type=DeviceType.DESKTOP,
        arguments={},
    )

    result = router.execute(request)

    assert result.success is False
    assert "execution failed" in (
        result.message.lower()
    )

from app.brain.intent_models import IntentType, ParsedIntent
from app.brain.intent_parser import RivaIntentParser


def test_intent_parser_empty_input():
    parser = RivaIntentParser()

    result = parser.parse("")

    assert result.intent_type == (
        IntentType.UNKNOWN
    )
    assert result.capability_name is None


def test_intent_parser_greeting():
    parser = RivaIntentParser()

    result = parser.parse("Hello")

    assert result.intent_type == (
        IntentType.CONVERSATION
    )
    assert result.confidence > 0.9


def test_intent_parser_calculator():
    parser = RivaIntentParser()

    result = parser.parse(
        "calculate 25 * 6"
    )

    assert result.intent_type == (
        IntentType.COMMAND
    )
    assert result.capability_name == (
        "calculator"
    )
    assert result.arguments[
        "expression"
    ] == "25 * 6"


def test_intent_parser_time_query():
    parser = RivaIntentParser()

    result = parser.parse(
        "what time is it"
    )

    assert result.intent_type == (
        IntentType.QUERY
    )
    assert result.capability_name == "time"


def test_intent_parser_unknown():
    parser = RivaIntentParser()

    result = parser.parse(
        "do something completely unknown"
    )

    assert result.intent_type == (
        IntentType.UNKNOWN
    )
    assert result.confidence == 0.0


def test_intent_parser_preserves_original_text():
    parser = RivaIntentParser()

    text = "Calculate 100 / 4"

    result = parser.parse(text)

    assert result.original_text == text

from app.brain.command_compiler import (
    RivaCommandCompiler,
)


def test_command_compiler_builds_request():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.COMMAND,
        capability_name="calculator",
        device_type=None,
        arguments={
            "expression": "25 * 6",
        },
        confidence=0.99,
        original_text="calculate 25 * 6",
    )

    request = compiler.compile(intent)

    assert request.command_id
    assert request.capability_name == (
        "calculator"
    )
    assert request.device_type == (
        DeviceType.DESKTOP
    )
    assert request.arguments[
        "expression"
    ] == "25 * 6"


def test_command_compiler_preserves_arguments():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.COMMAND,
        capability_name="test.command",
        device_type="phone",
        arguments={
            "message": "hello",
            "priority": "high",
        },
        confidence=1.0,
        original_text="test",
    )

    request = compiler.compile(intent)

    assert request.arguments == {
        "message": "hello",
        "priority": "high",
    }


def test_command_compiler_rejects_non_command():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.CONVERSATION,
        capability_name=None,
        device_type=None,
        arguments={},
        confidence=1.0,
        original_text="hello",
    )

    try:
        compiler.compile(intent)

        assert False, (
            "Non-command intent should fail"
        )

    except ValueError as exc:
        assert "command" in str(exc).lower()


def test_command_compiler_requires_capability():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.COMMAND,
        capability_name=None,
        device_type=None,
        arguments={},
        confidence=1.0,
        original_text="do something",
    )

    try:
        compiler.compile(intent)

        assert False, (
            "Missing capability should fail"
        )

    except ValueError as exc:
        assert "capability" in str(exc).lower()


def test_command_compiler_rejects_unknown_device():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.COMMAND,
        capability_name="test.command",
        device_type="spaceship",
        arguments={},
        confidence=1.0,
        original_text="test",
    )

    try:
        compiler.compile(intent)

        assert False, (
            "Unknown device should fail"
        )

    except ValueError as exc:
        assert "device type" in str(exc).lower()


def test_command_compiler_generates_unique_ids():
    compiler = RivaCommandCompiler()

    intent = ParsedIntent(
        intent_type=IntentType.COMMAND,
        capability_name="test.command",
        device_type=None,
        arguments={},
        confidence=1.0,
        original_text="test",
    )

    first = compiler.compile(intent)
    second = compiler.compile(intent)

    assert first.command_id != (
        second.command_id
    )




from app.brain.command_pipeline import (
    RivaCommandPipeline,
)


def test_command_pipeline_rejects_non_command():
    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=None,
    )

    result = pipeline.process("hello")

    assert result["success"] is False
    assert result["stage"] == "intent"
    assert result["intent_type"] == "conversation"


def test_command_pipeline_rejects_unknown_input():
    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=None,
    )

    result = pipeline.process(
        "do something completely unknown"
    )

    assert result["success"] is False
    assert result["stage"] == "intent"
    assert result["intent_type"] == "unknown"


def test_command_pipeline_executes_compiled_command():
    capabilities = CapabilityRegistry()

    capabilities.register(
        Capability(
            name="calculator",
            description="Calculate an expression.",
            permission=PermissionLevel.NONE,
            execute=lambda expression: (
                str(
                    eval(
                        expression,
                        {
                            "__builtins__": {}
                        },
                        {},
                    )
                )
            ),
        )
    )

    devices = DeviceRegistry()

    devices.register(
        Device(
            device_id="desktop-main",
            name="Desktop",
            device_type=DeviceType.DESKTOP,
            online=True,
        )
    )

    router = UnifiedCommandRouter(
        capabilities=capabilities,
        devices=DeviceCapabilityRouter(
            DeviceResolver(devices)
        ),
    )

    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=router,
    )

    result = pipeline.process(
        "calculate 25 * 6"
    )

    assert result["success"] is True
    assert result["stage"] == "execute"
    assert result["device_id"] == "desktop-main"

from app.brain.response_builder import (
    RivaResponseBuilder,
)
from app.brain.response_models import (
    ResponseType,
)


def test_response_builder_success():
    builder = RivaResponseBuilder()

    result = builder.from_pipeline_result(
        {
            "success": True,
            "intent_type": "command",
            "message": "150",
            "command_id": "cmd-1",
            "result": "150",
        }
    )

    assert result.success is True
    assert result.response_type == (
        ResponseType.SUCCESS
    )
    assert result.message == "150"
    assert result.command_id == "cmd-1"


def test_response_builder_failure():
    builder = RivaResponseBuilder()

    result = builder.from_pipeline_result(
        {
            "success": False,
            "intent_type": "command",
            "message": "Permission denied.",
            "command_id": "cmd-2",
        }
    )

    assert result.success is False
    assert result.response_type == (
        ResponseType.FAILURE
    )
    assert result.message == "Permission denied."


def test_response_builder_conversation():
    builder = RivaResponseBuilder()

    result = builder.from_pipeline_result(
        {
            "success": False,
            "intent_type": "conversation",
        }
    )

    assert result.success is True
    assert result.response_type == (
        ResponseType.CONVERSATION
    )
    assert "Hello" in result.message


def test_response_builder_unknown():
    builder = RivaResponseBuilder()

    result = builder.from_pipeline_result(
        {
            "success": False,
            "intent_type": "unknown",
        }
    )

    assert result.success is False
    assert result.response_type == (
        ResponseType.UNKNOWN
    )


def test_response_builder_preserves_command_id():
    builder = RivaResponseBuilder()

    result = builder.from_pipeline_result(
        {
            "success": False,
            "intent_type": "command",
            "message": "Failed.",
            "command_id": "abc-123",
        }
    )

    assert result.command_id == "abc-123"

from app.runtime.session import (
    RivaRuntime,
    RivaSession,
)


def test_riva_session_starts():
    session = RivaRuntime.create_session(
        "session-1"
    )

    assert session.session_id == "session-1"
    assert session.command_count == 0
    assert session.started_at is not None


def test_riva_runtime_processes_conversation():
    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=None,
    )

    runtime = RivaRuntime(
        pipeline=pipeline,
        session=RivaRuntime.create_session(
            "session-2"
        ),
    )

    response = runtime.process("hello")

    assert response.success is True
    assert response.response_type == (
        ResponseType.CONVERSATION
    )
    assert runtime.session.command_count == 1


def test_riva_runtime_counts_commands():
    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=None,
    )

    runtime = RivaRuntime(
        pipeline=pipeline,
        session=RivaRuntime.create_session(
            "session-3"
        ),
    )

    runtime.process("hello")
    runtime.process("hello")
    runtime.process("unknown request")

    assert runtime.session.command_count == 3


def test_riva_runtime_preserves_session():
    session = RivaSession(
        session_id="persistent-session",
        started_at=datetime.now(timezone.utc),
    )

    pipeline = RivaCommandPipeline(
        parser=RivaIntentParser(),
        compiler=RivaCommandCompiler(),
        router=None,
    )

    runtime = RivaRuntime(
        pipeline=pipeline,
        session=session,
    )

    runtime.process("hello")

    assert runtime.session is session
    assert runtime.session.session_id == (
        "persistent-session"
    )

def test_runtime_public_handle_returns_response():
    database = MemoryStore(":memory:")

    memory = MemoryManager(database)

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="public-handle"
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.success is True
    assert result.session_id == "public-handle"
    assert result.user_input == "Calculate 25 * 6"
    assert "150" in result.response


def test_runtime_public_handle_rejects_empty_input():
    database = MemoryStore(":memory:")

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(database),
    )

    session = RivaSession(
        session_id="public-empty"
    )

    try:
        runtime.handle(
            session=session,
            user_input="   ",
        )
        assert False, "Empty input should fail"
    except ValueError as exc:
        assert "input" in str(exc).lower()


def test_runtime_public_handle_preserves_session():
    database = MemoryStore(":memory:")

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(database),
    )

    session = RivaSession(
        session_id="public-session"
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 10 + 5",
    )

    assert result.session_id == session.session_id
    assert result.user_input == "Calculate 10 + 5"

def test_agent_loop_responds_to_greeting():
    database = MemoryStore(":memory:")

    # SQLite in-memory databases need initialization on the same
    # connection, so use the existing test pattern with a temp file.
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-greeting",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.response != ""
    assert "Hello" in result.response


def test_agent_loop_calculates():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-calculator",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response != ""
    assert "150" in result.response


def test_agent_loop_rejects_empty_input():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-empty",
    )

    try:
        loop.run(
            session=session,
            user_input="   ",
        )
        assert False, "Empty input should fail"
    except ValueError as exc:
        assert "input" in str(exc).lower()



def test_agent_loop_calculation_is_verified():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-verified",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response != ""
    assert "150" in result.response
    assert result.executions


def test_agent_loop_records_user_message():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-history",
    )

    loop.run(
        session=session,
        user_input="hello",
    )

    history = session.history()

    assert len(history) == 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"


def test_agent_loop_handles_unknown_request_without_crashing():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-unknown",
    )

    result = loop.run(
        session=session,
        user_input="do something completely unsupported",
    )

    assert result.response != ""
    assert result.session_id == "agent-unknown"


def test_agent_loop_preserves_context():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-context",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.context is not None
    assert result.session_id == session.session_id
    assert result.user_input == "hello"


def test_agent_loop_tool_execution_records_execution_result():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-execution",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 10 + 5",
    )

    assert len(result.executions) >= 1
    assert result.executions[-1].status.value == "success"
    assert "15" in result.response


def test_runtime_handle_uses_agent_loop_contract_for_greeting():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="runtime-agent-greeting",
    )

    result = runtime.handle(
        session=session,
        user_input="hello",
    )

    assert result.success is True
    assert result.session_id == session.session_id
    assert result.user_input == "hello"
    assert result.response != ""


def test_runtime_handle_calculation_returns_verified_output():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="runtime-agent-calculation",
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.success is True
    assert "150" in result.response
    assert len(result.tool_outputs) >= 1


def test_runtime_handle_preserves_conversation_history():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    memory = MemoryManager(
        MemoryStore(database_path)
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="runtime-history",
    )

    runtime.handle(
        session=session,
        user_input="hello",
    )

    history = session.history()

    assert len(history) >= 1
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "hello"


def test_runtime_contains_agent_loop():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    assert hasattr(runtime, "_agent_loop")
    assert isinstance(
        runtime._agent_loop,
        RivaAgentLoop,
    )


def test_agent_loop_rejects_empty_input():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-empty",
    )

    try:
        loop.run(
            session=session,
            user_input="   ",
        )
        assert False, "Empty input should fail"
    except ValueError as exc:
        assert "input" in str(exc).lower()


def test_agent_loop_preserves_session_identity():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-session-contract",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.session_id == session.session_id
    assert result.user_input == "hello"
    assert result.response != ""


def test_agent_loop_calculator_contract():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-calculator-contract",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.session_id == session.session_id
    assert result.user_input == "Calculate 25 * 6"
    assert result.response == "150"
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"


def test_agent_loop_rejects_empty_input():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-empty",
    )

    try:
        loop.run(
            session=session,
            user_input="   ",
        )
        assert False, "Empty input should fail"
    except ValueError as exc:
        assert "input" in str(exc).lower()


def test_agent_loop_preserves_session_identity():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-session-contract",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.session_id == session.session_id
    assert result.user_input == "hello"
    assert result.response != ""


def test_agent_loop_calculator_contract():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="agent-calculator-contract",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.session_id == session.session_id
    assert result.user_input == "Calculate 25 * 6"
    assert result.response == "150"
    assert len(result.executions) == 1
    assert result.executions[0].status.value == "success"


def test_runtime_delegates_handle_to_agent_loop():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    session = RivaSession(
        session_id="runtime-agent-delegation",
    )

    result = runtime.handle(
        session=session,
        user_input="hello",
    )

    assert result.success is True
    assert result.session_id == session.session_id
    assert result.user_input == "hello"
    assert result.response != ""


def test_runtime_calculator_uses_agent_loop_contract():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    session = RivaSession(
        session_id="runtime-agent-calculator",
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.success is True
    assert result.session_id == session.session_id
    assert result.response == "Verified: 150"
    assert result.tool_outputs == ["150"]


def test_runtime_preserves_conversation_history_through_agent_loop():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    session = RivaSession(
        session_id="runtime-history-agent",
    )

    first = runtime.handle(
        session=session,
        user_input="hello",
    )

    second = runtime.handle(
        session=session,
        user_input="hello again",
    )

    assert first.success is True
    assert second.success is True
    assert len(session.messages) >= 2
    assert session.messages[-1]["content"] == "hello again"



def test_agent_loop_rejects_empty_input():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path)
            ),
        )
    )

    session = RivaSession(
        session_id="agent-error-empty",
    )

    try:
        loop.run(
            session=session,
            user_input="   ",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "input" in str(exc).lower()


def test_agent_loop_rejects_missing_tool_name():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    class MissingToolDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name=None,
                tool_arguments={},
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=MissingToolDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-error-tool",
    )

    try:
        loop.run(
            session=session,
            user_input="do something",
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "tool name" in str(exc).lower()




def test_agent_loop_returns_failure_when_tool_execution_fails():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    class FailingDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "this is not valid math",
                },
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=FailingDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-tool-failure",
    )

    result = loop.run(
        session=session,
        user_input="calculate something invalid",
    )

    assert result.response != ""
    assert "invalid arithmetic expression" in result.response.lower()
    assert len(result.executions) == 1
    assert result.executions[-1].status.value == "failed"





def test_agent_loop_normalizes_empty_response():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    class EmptyResponseDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="   ",
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=EmptyResponseDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-empty-response",
    )

    result = loop.run(
        session=session,
        user_input="test response",
    )

    assert result.response == ""


def test_agent_loop_normalizes_none_response():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    class NoneResponseDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response=None,
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=NoneResponseDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-none-response",
    )

    result = loop.run(
        session=session,
        user_input="test response",
    )

    assert result.response == ""



def test_agent_loop_preserves_session_identity():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-session-identity-174",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.session_id == "agent-session-identity-174"
    assert result.session_id == session.session_id
    assert result.user_input == "hello"



def test_agent_loop_calculator_preserves_execution_result():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-execution-integrity-174",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response == "150"
    assert len(result.executions) == 1

    execution = result.executions[0]

    assert execution.tool_name == "calculator"
    assert execution.status.value == "success"
    assert str(execution.result) == "150"



def test_agent_loop_forwards_tool_arguments():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class ArgumentDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "25 * 6",
                },
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=ArgumentDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-tool-arguments-175",
    )

    result = loop.run(
        session=session,
        user_input="calculate this",
    )

    assert result.response == "150"
    assert len(result.executions) == 1
    assert result.executions[0].tool_name == "calculator"
    assert str(result.executions[0].result) == "150"



def test_execution_engine_marks_unknown_tool_as_failed():
    engine = ExecutionEngine(
        create_default_registry(),
    )

    result = engine.execute(
        "tool_that_does_not_exist",
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.result is None
    assert result.error is not None
    assert result.completed_at is not None



def test_execution_engine_failure_preserves_error_and_completion():
    engine = ExecutionEngine(
        create_default_registry(),
    )

    result = engine.execute(
        "tool_that_does_not_exist",
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.error
    assert "tool" in result.error.lower()
    assert result.completed_at is not None
    assert result.started_at is not None
    assert result.completed_at >= result.started_at



def test_execution_engine_success_completes_lifecycle():
    engine = ExecutionEngine(
        create_default_registry(),
    )

    result = engine.execute(
        "calculator",
        expression="25 * 6",
    )

    assert result.status == ExecutionStatus.SUCCESS
    assert str(result.result) == "150"
    assert result.error is None
    assert result.completed_at is not None
    assert result.started_at is not None
    assert result.completed_at >= result.started_at



def test_execution_engine_generates_unique_execution_ids():
    engine = ExecutionEngine(
        create_default_registry(),
    )

    first = engine.execute(
        "calculator",
        expression="25 * 6",
    )

    second = engine.execute(
        "calculator",
        expression="10 + 5",
    )

    assert first.execution_id
    assert second.execution_id
    assert first.execution_id != second.execution_id



def test_execution_engine_preserves_calculator_tool_identity():
    engine = ExecutionEngine(
        create_default_registry(),
    )

    result = engine.execute(
        "calculator",
        expression="25 * 6",
    )

    assert result.tool_name == "calculator"
    assert result.status == ExecutionStatus.SUCCESS
    assert str(result.result) == "150"



def test_execution_engine_marks_invalid_calculator_result_as_failed():
    engine = ExecutionEngine(
        create_default_registry()
    )

    result = engine.execute(
        "calculator",
        expression="this is not valid math",
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.tool_name == "calculator"
    assert result.error == "Invalid arithmetic expression."


def test_execution_engine_preserves_valid_calculator_success():
    engine = ExecutionEngine(
        create_default_registry()
    )

    result = engine.execute(
        "calculator",
        expression="25 * 6",
    )

    assert result.status == ExecutionStatus.SUCCESS
    assert result.tool_name == "calculator"
    assert result.result == "150"
    assert result.error is None


def test_execution_engine_unknown_tool_fails_cleanly():
    engine = ExecutionEngine(
        create_default_registry()
    )

    result = engine.execute(
        "does_not_exist",
    )

    assert result.status == ExecutionStatus.FAILED
    assert result.tool_name == "does_not_exist"
    assert result.error is not None



def test_agent_loop_propagates_failed_execution_status():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path)
        ),
    )

    class InvalidCalculatorDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "invalid arithmetic",
                },
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=InvalidCalculatorDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-failure-propagation",
    )

    result = loop.run(
        session=session,
        user_input="calculate invalid",
    )

    assert len(result.executions) == 1

    execution = result.executions[0]

    assert execution.tool_name == "calculator"
    assert execution.status == ExecutionStatus.FAILED
    assert execution.error == "Invalid arithmetic expression."
    assert execution.result is None
    assert result.response != ""


def test_agent_loop_preserves_successful_execution_result():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
    )

    session = RivaSession(
        session_id="agent-success-preservation",
    )

    result = loop.run(
        session=session,
        user_input="Calculate 12 + 8",
    )

    assert len(result.executions) == 1

    execution = result.executions[0]

    assert execution.tool_name == "calculator"
    assert execution.status == ExecutionStatus.SUCCESS
    assert execution.result == "20"
    assert execution.error is None
    assert result.response == "20"



def test_runtime_propagates_agent_tool_failure():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class InvalidDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "invalid arithmetic",
                },
            )

    runtime._agent_loop = RivaAgentLoop(
        orchestrator=runtime._orchestrator,
        decision_maker=InvalidDecisionMaker(),
    )

    session = RivaSession(
        session_id="runtime-failure-contract",
    )

    result = runtime.handle(
        session=session,
        user_input="calculate invalid",
    )

    assert result.success is False
    assert result.session_id == session.session_id
    assert result.user_input == "calculate invalid"
    assert result.error == "Invalid arithmetic expression."
    assert result.response != ""
    assert result.tool_outputs == []


def test_runtime_preserves_success_contract():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    session = RivaSession(
        session_id="runtime-success-contract",
    )

    result = runtime.handle(
        session=session,
        user_input="Calculate 30 + 12",
    )

    assert result.success is True
    assert result.session_id == session.session_id
    assert result.user_input == "Calculate 30 + 12"
    assert result.response == "Verified: 42"
    assert result.tool_outputs == ["42"]
    assert result.error is None


def test_runtime_agent_loop_uses_runtime_orchestrator():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    assert isinstance(
        runtime._agent_loop,
        RivaAgentLoop,
    )

    assert runtime._agent_loop._orchestrator is runtime._orchestrator


def test_runtime_agent_loop_is_reused_between_requests():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    agent_loop = runtime._agent_loop

    session = RivaSession(
        session_id="runtime-loop-reuse",
    )

    first = runtime.handle(
        session=session,
        user_input="hello",
    )

    second = runtime.handle(
        session=session,
        user_input="Calculate 5 + 5",
    )

    assert first.success is True
    assert second.success is True
    assert runtime._agent_loop is agent_loop
    assert runtime._agent_loop._orchestrator is runtime._orchestrator
    assert second.response == "Verified: 10"


def test_agent_loop_respond_decision_does_not_execute_tool():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class RespondDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Hello from Riva.",
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=RespondDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-respond-contract",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert result.response == "Hello from Riva."
    assert result.executions == []


def test_agent_loop_tool_decision_executes_selected_tool():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class CalculatorDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "7 * 8",
                },
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=CalculatorDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-tool-contract",
    )

    result = loop.run(
        session=session,
        user_input="calculate 7 * 8",
    )

    assert len(result.executions) == 1
    assert result.executions[0].tool_name == "calculator"
    assert result.executions[0].status == ExecutionStatus.SUCCESS
    assert result.executions[0].result == "56"
    assert result.response == "56"


def test_agent_loop_rejects_unknown_decision_type():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class UnknownDecisionMaker:
        def decide(self, user_input):
            return AgentDecision(
                decision_type="unknown",
            )

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=UnknownDecisionMaker(),
    )

    session = RivaSession(
        session_id="agent-unknown-decision",
    )

    try:
        loop.run(
            session=session,
            user_input="something",
        )
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "decision" in str(exc).lower()



def test_agent_loop_supports_multiple_tool_steps():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class MultiStepDecisionMaker:
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
                        "expression": "10 + 5",
                    },
                )

            if self.calls == 2:
                return AgentDecision(
                    decision_type=DecisionType.USE_TOOL,
                    tool_name="calculator",
                    tool_arguments={
                        "expression": "15 * 2",
                    },
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="Multi-step complete.",
            )

    decision_maker = MultiStepDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="agent-multi-step",
    )

    result = loop.run(
        session=session,
        user_input="do two calculations",
    )

    assert len(result.executions) == 2

    assert result.executions[0].tool_name == "calculator"
    assert result.executions[0].result == "15"
    assert result.executions[0].status == ExecutionStatus.SUCCESS

    assert result.executions[1].tool_name == "calculator"
    assert result.executions[1].result == "30"
    assert result.executions[1].status == ExecutionStatus.SUCCESS

    assert result.response == "Multi-step complete."
    assert decision_maker.calls == 3


def test_agent_loop_stops_after_failed_tool_execution():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class FailingMultiStepDecisionMaker:
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
                response="This should not execute.",
            )

    decision_maker = FailingMultiStepDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="agent-multi-step-failure",
    )

    result = loop.run(
        session=session,
        user_input="perform failing action",
    )

    assert len(result.executions) == 1
    assert result.executions[0].status == ExecutionStatus.FAILED
    assert result.executions[0].error == "Invalid arithmetic expression."
    assert decision_maker.calls == 1
    assert result.response != ""


def test_agent_loop_has_bounded_step_limit():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class InfiniteDecisionMaker:
        def __init__(self):
            self.calls = 0

        def decide(self, user_input):
            self.calls += 1

            return AgentDecision(
                decision_type=DecisionType.USE_TOOL,
                tool_name="calculator",
                tool_arguments={
                    "expression": "1 + 1",
                },
            )

    decision_maker = InfiniteDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="agent-step-limit",
    )

    result = loop.run(
        session=session,
        user_input="keep going",
    )

    assert len(result.executions) <= 10
    assert decision_maker.calls <= 10
    assert result.response != ""




def test_agent_loop_passes_context_to_context_aware_decision_maker():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class ContextAwareDecisionMaker:
        supports_context = True

        def __init__(self):
            self.context = None

        def decide(self, user_input, context):
            self.context = context

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response=f"Context session: {context.session_id}",
            )

    decision_maker = ContextAwareDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="context-aware-agent",
    )

    result = loop.run(
        session=session,
        user_input="hello",
    )

    assert decision_maker.context is not None
    assert decision_maker.context.session_id == "context-aware-agent"
    assert result.response == "Context session: context-aware-agent"

def test_agent_loop_context_contains_previous_conversation():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    class ContextAwareDecisionMaker:
        supports_context = True

        def decide(self, user_input, context):
            self.context = context
            previous = context.recent_messages

            if previous:
                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=previous[0]["content"],
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="No previous context.",
            )

    decision_maker = ContextAwareDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="conversation-context-test",
    )

    session.add_message(
        "user",
        "My favorite language is Python.",
    )

    result = loop.run(
        session=session,
        user_input="What did I just tell you?",
    )

    assert len(decision_maker.context.recent_messages) == 2
    assert (
        decision_maker.context.recent_messages[0]["content"]
        == "My favorite language is Python."
    )
    assert (
        decision_maker.context.recent_messages[1]["content"]
        == "What did I just tell you?"
    )
    assert result.response == "My favorite language is Python."


def test_agent_loop_context_contains_relevant_memory():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    memory_manager = MemoryManager(
        MemoryStore(database_path),
    )

    memory_manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory_manager,
    )

    class MemoryAwareDecisionMaker:
        supports_context = True

        def decide(self, user_input, context):
            self.context = context

            if context.memories:
                memory = context.memories[0]

                return AgentDecision(
                    decision_type=DecisionType.RESPOND,
                    response=(
                        f"Your favorite language is "
                        f"{memory.value}."
                    ),
                )

            return AgentDecision(
                decision_type=DecisionType.RESPOND,
                response="I don't remember.",
            )

    decision_maker = MemoryAwareDecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="memory-context-test",
    )

    result = loop.run(
        session=session,
        user_input="What is my favorite programming language?",
    )

    assert len(decision_maker.context.memories) == 1
    assert (
        decision_maker.context.memories[0].key
        == "favorite_language"
    )
    assert (
        decision_maker.context.memories[0].value
        == "Python"
    )
    assert result.response == "Your favorite language is Python."

def test_default_decision_maker_uses_memory_context():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    memory_manager = MemoryManager(
        MemoryStore(database_path),
    )

    memory_manager.remember(
        key="favorite_language",
        value="Python",
        category="preference",
    )

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=memory_manager,
    )

    decision_maker = DecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="default-memory-decision",
    )

    result = loop.run(
        session=session,
        user_input="What is my favorite language?",
    )

    assert result.response == "Python"

def test_default_decision_maker_handles_conversation_follow_up():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    decision_maker = DecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="conversation-follow-up",
    )

    first = loop.run(
        session=session,
        user_input="My favorite language is Python.",
    )

    assert first.response != ""

    second = loop.run(
        session=session,
        user_input="What did I just tell you?",
    )

    assert (
        "Python" in second.response
    )

def test_default_decision_maker_uses_previous_user_message_for_follow_up():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    decision_maker = DecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="conversation-follow-up-user-message",
    )

    session.add_message(
        "user",
        "My favorite programming language is Python.",
    )

    session.add_message(
        "assistant",
        "That's useful to know.",
    )

    result = loop.run(
        session=session,
        user_input="What did I just tell you?",
    )

    assert (
        result.response
        == "My favorite programming language is Python."
    )

def test_default_decision_maker_resolves_previous_calculation_result():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    decision_maker = DecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="reference-calculation",
    )

    first = loop.run(
        session=session,
        user_input="calculate 25 * 6",
    )

    assert first.response == "150"

    second = loop.run(
        session=session,
        user_input="What was the result?",
    )

    assert second.response == "150"

def test_default_decision_maker_resolves_it_to_previous_calculation_result():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database_path),
        ),
    )

    decision_maker = DecisionMaker()

    loop = RivaAgentLoop(
        orchestrator=orchestrator,
        decision_maker=decision_maker,
    )

    session = RivaSession(
        session_id="entity-reference-calculation",
    )

    first = loop.run(
        session=session,
        user_input="calculate 25 * 6",
    )

    assert first.response == "150"

    second = loop.run(
        session=session,
        user_input="Now add 50 to it",
    )

    assert second.response == "200"

def test_default_decision_maker_resolves_it_for_subtraction():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        orchestrator=RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path),
            ),
        ),
        decision_maker=DecisionMaker(),
    )

    session = RivaSession(
        session_id="entity-reference-subtraction",
    )

    first = loop.run(
        session=session,
        user_input="calculate 100 - 25",
    )

    assert first.response == "75"

    second = loop.run(
        session=session,
        user_input="subtract 15 from it",
    )

    assert second.response == "60"


def test_default_decision_maker_resolves_it_for_multiplication():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        orchestrator=RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path),
            ),
        ),
        decision_maker=DecisionMaker(),
    )

    session = RivaSession(
        session_id="entity-reference-multiplication",
    )

    first = loop.run(
        session=session,
        user_input="calculate 10 + 5",
    )

    assert first.response == "15"

    second = loop.run(
        session=session,
        user_input="multiply it by 4",
    )

    assert second.response == "60"


def test_default_decision_maker_resolves_it_for_division():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        orchestrator=RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path),
            ),
        ),
        decision_maker=DecisionMaker(),
    )

    session = RivaSession(
        session_id="entity-reference-division",
    )

    first = loop.run(
        session=session,
        user_input="calculate 100 / 4",
    )

    assert first.response == "25.0"

    second = loop.run(
        session=session,
        user_input="divide it by 5",
    )

    assert second.response == "5.0"

def test_default_decision_maker_resolves_previous_statement_reference():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        orchestrator=RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path),
            ),
        ),
        decision_maker=DecisionMaker(),
    )

    session = RivaSession(
        session_id="general-reference-statement",
    )

    first = loop.run(
        session=session,
        user_input="My favorite color is blue",
    )

    assert first.response == (
        "I understand your request, "
        "but I don't have a capability for it yet."
    )

    second = loop.run(
        session=session,
        user_input="What did I just tell you?",
    )

    assert second.response == "My favorite color is blue"


def test_default_decision_maker_resolves_previous_statement_with_that():
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False,
    ) as tmp:
        database_path = tmp.name

    loop = RivaAgentLoop(
        orchestrator=RivaOrchestrator(
            registry=create_default_registry(),
            memory_manager=MemoryManager(
                MemoryStore(database_path),
            ),
        ),
        decision_maker=DecisionMaker(),
    )

    session = RivaSession(
        session_id="general-reference-that",
    )

    first = loop.run(
        session=session,
        user_input="The project deadline is Friday",
    )

    assert first.response == (
        "I understand your request, "
        "but I don't have a capability for it yet."
    )

    second = loop.run(
        session=session,
        user_input="What was that?",
    )

    assert second.response == "The project deadline is Friday"
