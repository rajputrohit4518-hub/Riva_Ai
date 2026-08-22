import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.delegation import CrossDeviceToolDelegation

def test_tool_delegation_and_execution():
    # Setup remote worker node
    worker_node = CrossDeviceToolDelegation(node_id="worker_tablet")
    
    # Register a sample tool on the worker node
    def sample_calculator(a: int, b: int):
        return a + b
        
    worker_node.register_tool("calculator", sample_calculator)
    
    # Primary node creates delegation payload
    primary_node = CrossDeviceToolDelegation(node_id="primary_desktop")
    payload = primary_node.delegate_execution("worker_tablet", "calculator", {"a": 10, "b": 20})
    
    # Worker node handles incoming payload
    response_raw = worker_node.handle_incoming_delegation(payload)
    
    assert response_raw["success"] is True
    assert response_raw["result"] == 30

def test_delegation_tool_not_found():
    node = CrossDeviceToolDelegation(node_id="isolated_node")
    payload = node.delegate_execution("isolated_node", "nonexistent_tool", {})
    response = node.handle_incoming_delegation(payload)
    
    assert response["success"] is False
    assert "not found" in response["error"]
