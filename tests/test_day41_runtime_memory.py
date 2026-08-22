from app.memory.manager import MemoryManager
from app.tools.defaults import create_default_registry
from app.core.session import RivaSession
from app.runtime.runtime import RivaRuntime


def test_runtime_memory_commands():
    memory = MemoryManager(
        store=__import__("app.memory.store", fromlist=["MemoryStore"]).MemoryStore(":memory:")
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(session_id="test-memory")

    result = runtime.handle(session, "remember my name is Rohit")

    assert result.success is True
    assert memory.recall("name") is not None
    assert memory.recall("name").value == "Rohit"

    result = runtime.handle(session, "what is my name")

    assert result.success is True
    assert result.response == "Rohit"

    result = runtime.handle(session, "forget my name")

    assert result.success is True
    assert memory.recall("name") is None
