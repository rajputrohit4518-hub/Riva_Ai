import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.clipboard import CrossDeviceClipboardManager

def test_clipboard_push_and_retrieval():
    manager = CrossDeviceClipboardManager(node_id="desktop_primary")
    
    manager.push_clipboard("First copied snippet", source_device="phone_1")
    latest = manager.push_clipboard("Important reference URL: https://riva.ai", source_device="desktop_primary")
    
    assert latest["content"] == "Important reference URL: https://riva.ai"
    assert latest["source_device"] == "desktop_primary"
    
    # Verify latest retrieval
    current = manager.get_latest_clipboard()
    assert current["content"] == "Important reference URL: https://riva.ai"

def test_clipboard_search():
    manager = CrossDeviceClipboardManager(node_id="desktop_primary")
    manager.push_clipboard("Alpha python script snippet")
    manager.push_clipboard("Beta rust memory management")
    manager.push_clipboard("Alpha machine learning model architecture")
    
    results = manager.search_clipboard("alpha")
    assert len(results) == 2
