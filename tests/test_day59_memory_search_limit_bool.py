from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_true_limit_is_safe():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("Rust",limit=True)==[]

def test_false_limit_is_safe():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("Rust",limit=False)==[]

def test_integer_limit_still_works():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert len(m.search("Rust",limit=1))==1
