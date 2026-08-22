from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore
from app.core.session import RivaSession
from app.runtime.runtime import RivaRuntime
from app.tools.defaults import create_default_registry


def build_runtime():
    memory = MemoryManager(
        store=MemoryStore(":memory:")
    )

    runtime = RivaRuntime(
        registry=create_default_registry(),
        memory_manager=memory,
    )

    session = RivaSession(
        session_id="day46-memory-category"
    )

    return runtime, memory, session


def test_runtime_name_memory_gets_identity_category():
    runtime, memory, session = build_runtime()

    result = runtime.handle(
        session,
        "remember my name is Rohit",
    )

    assert result.success is True

    stored = memory.recall("name")

    assert stored is not None
    assert stored.value == "Rohit"
    assert stored.category == "identity"


def test_runtime_favorite_memory_gets_preference_category():
    runtime, memory, session = build_runtime()

    result = runtime.handle(
        session,
        "remember my favorite language is Rust",
    )

    assert result.success is True

    stored = memory.recall("favorite language")

    assert stored is not None
    assert stored.value == "Rust"
    assert stored.category == "preference"


def test_runtime_memory_update_preserves_category():
    runtime, memory, session = build_runtime()

    runtime.handle(
        session,
        "remember my favorite language is Python",
    )

    runtime.handle(
        session,
        "remember my favorite language is Rust",
    )

    stored = memory.recall("favorite language")

    assert stored is not None
    assert stored.value == "Rust"
    assert stored.category == "preference"


def test_runtime_memory_retrieval_returns_latest_value():
    runtime, memory, session = build_runtime()

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


def test_runtime_forget_removes_categorized_memory():
    runtime, memory, session = build_runtime()

    runtime.handle(
        session,
        "remember my name is Rohit",
    )

    stored = memory.recall("name")

    assert stored is not None
    assert stored.category == "identity"

    result = runtime.handle(
        session,
        "forget my name",
    )

    assert result.success is True
    assert memory.recall("name") is None


def test_runtime_multiple_categories_are_independent():
    runtime, memory, session = build_runtime()

    runtime.handle(
        session,
        "remember my name is Rohit",
    )

    runtime.handle(
        session,
        "remember my favorite language is Rust",
    )

    name = memory.recall("name")
    language = memory.recall("favorite language")

    assert name is not None
    assert language is not None

    assert name.value == "Rohit"
    assert name.category == "identity"

    assert language.value == "Rust"
    assert language.category == "preference"


def test_runtime_category_data_persists_in_memory_store():
    runtime, memory, session = build_runtime()

    runtime.handle(
        session,
        "remember my name is Rohit",
    )

    runtime.handle(
        session,
        "remember my favorite language is Rust",
    )

    memories = memory.list_memories()

    assert len(memories) == 2

    categories = {
        memory.category
        for memory in memories
    }

    assert "identity" in categories
    assert "preference" in categories
