from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_memory_category_is_preserved():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    memory = manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.category == "identity"


def test_multiple_memory_categories():
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

    name = manager.recall("name")
    language = manager.recall("favorite language")

    assert name is not None
    assert name.category == "identity"

    assert language is not None
    assert language.category == "preference"


def test_category_persists_across_manager_instances(tmp_path):
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
