import hmac
import hashlib
import secrets
from typing import Dict, Any, Optional

class CrossDevicePairingManager:
    """Manages cryptographic pairing codes and device authentication tokens for secure cross-device handshakes."""

    def __init__(self, master_secret: Optional[str] = None):
        self.master_secret = (master_secret or secrets.token_hex(32)).encode("utf-8")
        self.active_pairing_codes: Dict[str, str] = {}

    def generate_pairing_code(self, device_id: str) -> str:
        """Generates a secure 6-digit temporary pairing code for a connecting device."""
        code = "".join(secrets.choice("0123456789") for _ in range(6))
        self.active_pairing_codes[device_id] = code
        return code

    def verify_pairing_code(self, device_id: str, code: str) -> bool:
        """Verifies a submitted pairing code against active challenges."""
        expected_code = self.active_pairing_codes.get(device_id)
        if expected_code and hmac.compare_digest(expected_code, code):
            # Consume pairing code upon successful verification
            self.active_pairing_codes.pop(device_id, None)
            return True
        return False

    def generate_device_token(self, device_id: str) -> str:
        """Issues a persistent HMAC authentication token for a paired device."""
        return hmac.new(self.master_secret, device_id.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_device_token(self, device_id: str, token: str) -> bool:
        """Verifies a device authentication token securely."""
        expected_token = self.generate_device_token(device_id)
        return hmac.compare_digest(expected_token, token)
