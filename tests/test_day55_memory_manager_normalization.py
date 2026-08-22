from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_manager_normalizes_case_and_whitespace():
    m=build_memory()
    m.remember("Favorite Language","Rust","preference")
    r=m.search("  FAVORITE   LANGUAGE  ")
    assert len(r)==1
    assert r[0].key=="Favorite Language"

def test_manager_normalization_preserves_empty_query():
    assert build_memory().search("   \t\n  ")==[]

def test_manager_normalization_preserves_limit():
    m=build_memory()
    m.remember("a","Rust","programming")
    m.remember("b","Rust","programming")
    assert len(m.search("  RUST  ",limit=1))==1
