import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from riva.production.database.migrations import ProductionMigrationManager

def test_migration_execution_and_tracking():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = str(Path(tmpdir) / "test_prod.db")
        manager = ProductionMigrationManager(db_file)
        
        assert manager.get_applied_versions() == []
        
        # Apply migration 1
        success = manager.apply_migration(
            version=1,
            name="create_users_table",
            sql_statements=["CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT)"]
        )
        assert success is True
        assert manager.get_applied_versions() == [1]
        
        # Attempting to re-apply same version should safely return False
        success_repeat = manager.apply_migration(
            version=1,
            name="create_users_table",
            sql_statements=[]
        )
        assert success_repeat is False
