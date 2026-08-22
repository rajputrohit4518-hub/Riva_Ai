from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_day36_remember_name():
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
    assert memory.category == "identity"


def test_day36_recall_name():
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


def test_day36_memory_persists():
    manager = MemoryManager(
        store=MemoryStore(":memory:")
    )

    manager.remember(
        "language",
        "Python",
        "preference",
    )

    memories = manager.list_memories()

    assert len(memories) == 1
    assert memories[0].key == "language"
    assert memories[0].value == "Python"
