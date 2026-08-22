from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_remember_command_foundation():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert manager.recall("name").value == "Rohit"


def test_search_memory_command_foundation():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    results = manager.search("Rohit")

    assert len(results) == 1
    assert results[0].value == "Rohit"


def test_forget_command_foundation():
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
