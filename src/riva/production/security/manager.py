import hmac
import hashlib
from typing import Optional

class ProductionSecurityManager:
    """Manages authentication tokens, input sanitization, and security boundaries for Riva Production."""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = (secret_key or "riva-secure-default-key").encode("utf-8")

    def generate_token(self, payload: str) -> str:
        """Generates an HMAC-SHA256 authentication token for a given payload."""
        return hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_token(self, payload: str, token: str) -> bool:
        """Verifies an HMAC-SHA256 authentication token safely against timing attacks."""
        expected_token = self.generate_token(payload)
        return hmac.compare_digest(expected_token, token)

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """Sanitizes raw user string input to prevent injection or malicious control characters."""
        if not isinstance(user_input, str):
            return ""
        # Strip dangerous control characters and normalize whitespace
        sanitized = "".join(ch for ch in user_input if ord(ch) >= 32 or ch in "\n\r\t")
        return sanitized.strip()
