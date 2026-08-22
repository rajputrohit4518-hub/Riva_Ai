import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.backup.manager import ProductionBackupManager

def test_backup_creation_and_restoration():
    with tempfile.TemporaryDirectory() as tmpdir:
        source_dir = Path(tmpdir) / "data"
        source_dir.mkdir()
        
        # Create a mock data file
        test_file = source_dir / "test.db"
        test_file.write_text("critical_app_state", encoding="utf-8")
        
        backup_dir = Path(tmpdir) / "backups"
        manager = ProductionBackupManager(str(backup_dir))
        
        # Create backup
        archive_path = manager.create_backup(str(test_file), "test_backup.zip")
        assert archive_path is not None
        assert Path(archive_path).exists()
        
        # Restore backup
        restore_dir = Path(tmpdir) / "restored"
        success = manager.restore_backup(archive_path, str(restore_dir))
        assert success is True
        
        restored_file = restore_dir / "test.db"
        assert restored_file.exists()
        assert restored_file.read_text(encoding="utf-8") == "critical_app_state"
