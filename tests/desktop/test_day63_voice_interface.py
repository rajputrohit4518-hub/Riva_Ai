import pytest
from app.desktop.app import RivaDesktopApp

def test_day63_voice_interface():
    app = RivaDesktopApp()
    assert not app.voice_active
    assert app.toggle_voice() is True
    assert app.voice_active
    assert app.toggle_voice() is False

