from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore


def test_memory_persists_across_manager_instances(tmp_path):
    database = tmp_path / "riva_memory.db"

    first = MemoryManager(
        store=MemoryStore(str(database))
    )

    first.remember(
        "favorite language",
        "Rust",
    )

    second = MemoryManager(
        store=MemoryStore(str(database))
    )

    memory = second.recall("favorite language")

    assert memory is not None
    assert memory.value == "Rust"


def test_memory_update_persists(tmp_path):
    database = tmp_path / "riva_memory.db"

    first = MemoryManager(
        store=MemoryStore(str(database))
    )

    first.remember(
        "favorite language",
        "Python",
    )

    first.remember(
        "favorite language",
        "Rust",
    )

    second = MemoryManager(
        store=MemoryStore(str(database))
    )

    memory = second.recall("favorite language")

    assert memory is not None
    assert memory.value == "Rust"


def test_forgot_memory_stays_deleted(tmp_path):
    database = tmp_path / "riva_memory.db"

    first = MemoryManager(
        store=MemoryStore(str(database))
    )

    first.remember(
        "name",
        "Rohit",
        "identity",
    )

    assert first.forget("name") is True

    second = MemoryManager(
        store=MemoryStore(str(database))
    )

    assert second.recall("name") is None
