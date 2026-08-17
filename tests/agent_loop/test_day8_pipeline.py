from app.agent_loop.loop import RivaAgentLoop
from app.core.session import RivaSession
from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.orchestration.orchestrator import RivaOrchestrator
from app.tools.defaults import create_default_registry


def test_day8_calculation_pipeline_returns_verified_result(tmp_path):
    database = tmp_path / "day8.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="day8-calculation"
    )

    result = loop.run(
        session=session,
        user_input="Calculate 25 * 6",
    )

    assert result.response
    assert "150" in result.response


def test_day8_greeting_still_works(tmp_path):
    database = tmp_path / "day8-greeting.db"

    orchestrator = RivaOrchestrator(
        registry=create_default_registry(),
        memory_manager=MemoryManager(
            MemoryStore(str(database))
        ),
    )

    loop = RivaAgentLoop(orchestrator)

    session = RivaSession(
        session_id="day8-greeting"
    )

    result = loop.run(
        session=session,
        user_input="Hello Riva",
    )

    assert result.response
    assert "Hello" in result.response
