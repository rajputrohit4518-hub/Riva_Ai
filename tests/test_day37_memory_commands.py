from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_remember_and_recall():
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


def test_forget_memory():
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


def test_unknown_memory_returns_none():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    assert manager.recall("unknown") is None
