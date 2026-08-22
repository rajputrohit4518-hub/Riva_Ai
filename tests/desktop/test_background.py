import sys
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.desktop.background.service import BackgroundOperationService

def test_background_service_lifecycle():
    service = BackgroundOperationService(interval=0.05)
    assert not service.is_running
    
    service.start()
    assert service.is_running
    
    time.sleep(0.2)
    service.stop()
    assert not service.is_running
    assert service.execution_count > 0

def test_background_service_callback():
    counter = {"val": 0}
    def dummy_task():
        counter["val"] += 1

    service = BackgroundOperationService(task_callback=dummy_task, interval=0.02)
    service.start()
    time.sleep(0.1)
    service.stop()
    
    assert counter["val"] > 0
