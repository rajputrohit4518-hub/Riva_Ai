import threading
import time
from typing import Callable, Optional

class BackgroundOperationService:
    """Manages background task loops, tray service status, and daemon tasks for Riva Desktop."""

    def __init__(self, task_callback: Optional[Callable[[], None]] = None, interval: float = 0.1):
        self.task_callback = task_callback
        self.interval = interval
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self.execution_count = 0

    def _run_loop(self):
        while self._is_running:
            if self.task_callback:
                try:
                    self.task_callback()
                except Exception:
                    pass
            self.execution_count += 1
            time.sleep(self.interval)

    def start(self) -> None:
        """Starts the background worker thread."""
        if not self._is_running:
            self._is_running = True
            self.execution_count = 0
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stops the background worker thread."""
        if self._is_running:
            self._is_running = False
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1.0)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._is_running
