import pytest
from app.desktop.app import RivaDesktopApp

def test_day64_conversation_history():
    app = RivaDesktopApp()
    app.add_message('user', 'Test message')
    assert len(app.history) == 1
    app.clear_history()
    assert len(app.history) == 0

