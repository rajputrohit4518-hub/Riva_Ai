from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_search_returns_matching_memory_with_category():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = manager.search("favorite language")

    assert len(results) == 1
    assert results[0].key == "favorite language"
    assert results[0].value == "Rust"
    assert results[0].category == "preference"


def test_search_can_return_multiple_categories():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    manager.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    results = manager.list_memories()

    assert len(results) == 2

    categories = {
        memory.category
        for memory in results
    }

    assert "identity" in categories
    assert "preference" in categories


def test_memory_update_keeps_latest_category():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "favorite language",
        "Python",
        "preference",
    )

    manager.remember(
        "favorite language",
        "Rust",
        "programming",
    )

    memory = manager.recall("favorite language")

    assert memory is not None
    assert memory.value == "Rust"
    assert memory.category == "programming"


def test_category_and_value_persist():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    memory = manager.recall("name")

    assert memory is not None
    assert memory.value == "Rohit"
    assert memory.category == "identity"


def test_unknown_memory_returns_none():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    assert manager.recall("does not exist") is None


def test_forget_removes_memory_completely():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert manager.forget("name") is True
    assert manager.recall("name") is None
    assert manager.search("name") == []


def test_category_persists_across_database_instances(tmp_path):
    database = tmp_path / "riva_memory.db"

    first = MemoryManager(
        store=MemoryStore(str(database))
    )

    first.remember(
        "favorite language",
        "Rust",
        "preference",
    )

    second = MemoryManager(
        store=MemoryStore(str(database))
    )

    memory = second.recall("favorite language")

    assert memory is not None
    assert memory.value == "Rust"
    assert memory.category == "preference"

