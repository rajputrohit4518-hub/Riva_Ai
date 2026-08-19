from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_day29_memory_lifecycle():
    manager = MemoryManager(store=MemoryStore(":memory:"))

    manager.remember("name", "Rohit", "identity")
    manager.remember("language", "Python", "preference")

    assert manager.recall("name").value == "Rohit"
    assert manager.search("Python")[0].value == "Python"

    manager.remember("language", "Python 3.11", "preference")
    assert manager.recall("language").value == "Python 3.11"

    assert manager.forget("name") is True
    assert manager.recall("name") is None


def test_day29_multiple_memories_remain_isolated():
    manager = MemoryManager(store=MemoryStore(":memory:"))

    for index in range(20):
        manager.remember(
            f"memory_{index}",
            f"value_{index}",
        )

    assert len(manager.list_memories()) == 20
    assert manager.recall("memory_7").value == "value_7"
