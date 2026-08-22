from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_empty_query_returns_empty():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("")==[]

def test_whitespace_query_returns_empty():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("   \t\n ")==[]

def test_empty_query_does_not_mutate_memory():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    before=m.recall("Rust")
    m.search("   ")
    after=m.recall("Rust")
    assert before==after
