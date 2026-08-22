from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_day41_remember_memory():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    memory = manager.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert memory.key == "name"
    assert memory.value == "Rohit"


def test_day41_recall_memory():
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


def test_day41_forget_memory():
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
