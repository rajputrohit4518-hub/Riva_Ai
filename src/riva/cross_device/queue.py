import uuid
import time
from typing import Dict, Any, Optional

class DistributedTaskQueue:
    """Manages asynchronous background task offloading and status tracking across distributed Riva nodes."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def enqueue_task(self, task_name: str, payload: Dict[str, Any], target_node: Optional[str] = None) -> str:
        """Enqueues a background task for execution either locally or on a remote node."""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "task_id": task_id,
            "task_name": task_name,
            "payload": payload,
            "target_node": target_node or self.node_id,
            "status": "pending",
            "result": None,
            "created_at": time.time()
        }
        return task_id

    def update_task_status(self, task_id: str, status: str, result: Any = None) -> bool:
        """Updates the execution status and result of an enqueued task."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            self.tasks[task_id]["result"] = result
            return True
        return False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves task details and current status by ID."""
        return self.tasks.get(task_id)
