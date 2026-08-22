import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.security.manager import ProductionSecurityManager

def test_token_generation_and_verification():
    sec = ProductionSecurityManager(secret_key="test-secret")
    payload = "user_session_123"
    
    token = sec.generate_token(payload)
    assert sec.verify_token(payload, token) is True
    assert sec.verify_token("tampered_payload", token) is False

def test_input_sanitization():
    raw = "Hello\x00World\nClean"
    sanitized = ProductionSecurityManager.sanitize_input(raw)
    assert "\x00" not in sanitized
    assert "Hello" in sanitized
    assert "Clean" in sanitized
