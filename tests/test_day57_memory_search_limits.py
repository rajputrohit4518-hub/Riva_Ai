from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_negative_limit_returns_empty():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("Rust",limit=-1)==[]

def test_zero_limit_returns_empty():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("Rust",limit=0)==[]

def test_limit_one_returns_one_result():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    m.remember("Rust tools","Cargo","programming")
    assert len(m.search("Rust",limit=1))==1
