import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.desktop.recovery.manager import DesktopCrashRecoveryManager

def test_crash_detection_and_recovery():
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "crash_state.json"
        manager = DesktopCrashRecoveryManager(str(state_file))
        
        # Initially no state/crash
        assert not manager.did_crash_occur()
        assert manager.recover_state() is None
        
        # Simulate active state without clean exit (i.e. a crash)
        manager.save_state({"active_tab": "chat", "draft": "hello"})
        assert manager.did_crash_occur() is True
        
        recovered = manager.recover_state()
        assert recovered is not None
        assert recovered["draft"] == "hello"
        
        # Simulate clean exit resolution
        manager.mark_clean_exit()
        assert manager.did_crash_occur() is False
