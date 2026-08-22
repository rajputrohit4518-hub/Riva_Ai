from app.memory.manager import MemoryManager
from app.orchestration.models import OrchestrationResult


def test_orchestrator_memory_access():
    memory = MemoryManager(
        store=__import__("app.memory.store", fromlist=["MemoryStore"]).MemoryStore(":memory:")
    )

    memory.remember("name", "Rohit", "identity")

    assert memory.recall("name").value == "Rohit"

    assert memory.forget("name") is True
    assert memory.recall("name") is None
