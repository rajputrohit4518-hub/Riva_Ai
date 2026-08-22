from app.memory.manager import MemoryManager
from app.memory.store import MemoryStore

def build_memory():
    return MemoryManager(store=MemoryStore(":memory:"))

def test_search_integer_is_safe():
    assert build_memory().search(123)==[]

def test_search_list_is_safe():
    assert build_memory().search([])==[]

def test_search_dict_is_safe():
    assert build_memory().search({})==[]

def test_search_bytes_is_safe():
    assert build_memory().search(b"Rust")==[]
