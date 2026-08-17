from app.agent_loop.loop import RivaAgentLoop
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def test_agent_loop_calculation_uses_existing_runtime():
    database = "day7_agent_loop.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(database)
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="day7-calculation"
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response
    assert "150" in result.response
