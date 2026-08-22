from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_large_limit_is_safe():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert len(m.search("Rust",limit=999999))==1

def test_empty_query_with_large_limit_is_empty():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("   ",limit=999999)==[]

def test_normal_search_still_works():
    m=build_memory()
    m.remember("Rust","systems language","programming")
    assert m.search("Rust",limit=1)[0].key=="Rust"
