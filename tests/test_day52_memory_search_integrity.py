from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))


def test_search_returns_independent_memory_objects():
    memory = build_memory()
    memory.remember("favorite language", "Rust", "preference")

    result = memory.search("Rust")[0]
    assert result.value == memory.recall("favorite language").value


def test_search_does_not_change_metadata():
    memory = build_memory()
    memory.remember("favorite language", "Rust", "preference")

    before = memory.recall("favorite language")
    memory.search("Rust")
    after = memory.recall("favorite language")

    assert before.created_at == after.created_at
    assert before.updated_at == after.updated_at


def test_search_results_are_stable():
    memory = build_memory()
    memory.remember("alpha", "Rust", "programming")
    memory.remember("beta", "Rust", "programming")

    assert memory.search("Rust") == memory.search("Rust")
