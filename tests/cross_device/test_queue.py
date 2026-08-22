import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.cross_device.queue import DistributedTaskQueue

def test_task_queue_lifecycle():
    queue = DistributedTaskQueue(node_id="desktop_primary")
    
    # Enqueue a background indexing task
    task_id = queue.enqueue_task("index_documents", {"path": "/docs"}, target_node="worker_node_1")
    assert task_id is not None
    
    task_info = queue.get_task(task_id)
    assert task_info["status"] == "pending"
    assert task_info["target_node"] == "worker_node_1"
    
    # Update task status to completed with result
    success = queue.update_task_status(task_id, "completed", {"indexed_count": 42})
    assert success is True
    
    updated_info = queue.get_task(task_id)
    assert updated_info["status"] == "completed"
    assert updated_info["result"]["indexed_count"] == 42
