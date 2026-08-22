import time
from typing import Dict, Any, Optional

class CrossDeviceClipboardManager:
    """Manages synchronized clipboard history and context sharing across connected Riva devices."""

    def __init__(self, node_id: str, max_history: int = 50):
        self.node_id = node_id
        self.max_history = max_history
        self.clipboard_history: list = []

    def push_clipboard(self, content: str, content_type: str = "text", source_device: Optional[str] = None) -> Dict[str, Any]:
        """Pushes new clipboard content into the shared history ring buffer."""
        entry = {
            "source_device": source_device or self.node_id,
            "content_type": content_type,
            "content": content,
            "timestamp": time.time()
        }
        
        # Avoid duplicate consecutive entries
        if self.clipboard_history and self.clipboard_history[0]["content"] == content:
            return self.clipboard_history[0]

        self.clipboard_history.insert(0, entry)
        if len(self.clipboard_history) > self.max_history:
            self.clipboard_history.pop()

        return entry

    def get_latest_clipboard(self) -> Optional[Dict[str, Any]]:
        """Retrieves the most recent clipboard entry."""
        if self.clipboard_history:
            return self.clipboard_history[0]
        return None

    def search_clipboard(self, query: str) -> list:
        """Searches shared clipboard history for specific keywords."""
        query_lower = query.lower()
        return [
            entry for entry in self.clipboard_history
            if query_lower in entry["content"].lower()
        ]
