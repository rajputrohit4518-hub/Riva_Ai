from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.tools.defaults import create_default_registry
from app.core.session import RivaSession
from app.runtime.runtime import RivaRuntime


def test_memory_recall_through_runtime():
    memory = MemoryManager(
        store=MemoryStore(":memory:")
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="day42"
    )

    runtime.handle(
        session,
        "remember my favorite language is Python",
    )

    result = runtime.handle(
        session,
        "what is my favorite language",
    )

    assert result.success is True
    assert result.response == "Python"


def test_memory_forget_through_runtime():
    memory = MemoryManager(
        store=MemoryStore(":memory:")
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="day42-forget"
    )

    runtime.handle(
        session,
        "remember my favorite language is Python",
    )

    runtime.handle(
        session,
        "forget my favorite language",
    )

    assert memory.recall(
        "favorite language"
    ) is None


def test_memory_update_through_runtime():
    memory = MemoryManager(
        store=MemoryStore(":memory:")
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="day42-update"
    )

    runtime.handle(
        session,
        "remember my favorite language is Python",
    )

    runtime.handle(
        session,
        "remember my favorite language is Rust",
    )

    result = runtime.handle(
        session,
        "what is my favorite language",
    )

    assert result.success is True
    assert result.response == "Rust"
