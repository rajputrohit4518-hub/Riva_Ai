import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.pairing import CrossDevicePairingManager

def test_pairing_code_workflow():
    manager = CrossDevicePairingManager(master_secret="test-master-secret")
    device_id = "phone_client_1"
    
    code = manager.generate_pairing_code(device_id)
    assert len(code) == 6
    
    # Verify with incorrect code
    assert manager.verify_pairing_code(device_id, "000000") is False
    
    # Re-generate code for verification test
    code = manager.generate_pairing_code(device_id)
    assert manager.verify_pairing_code(device_id, code) is True
    
    # Code should be consumed (single use)
    assert manager.verify_pairing_code(device_id, code) is False

def test_device_token_authentication():
    manager = CrossDevicePairingManager(master_secret="test-master-secret")
    device_id = "tablet_client_2"
    
    token = manager.generate_device_token(device_id)
    assert manager.verify_device_token(device_id, token) is True
    assert manager.verify_device_token(device_id, "invalid_token") is False
