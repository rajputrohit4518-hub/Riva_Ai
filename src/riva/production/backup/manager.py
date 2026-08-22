import shutil
import zipfile
from pathlib import Path
from typing import Optional

class ProductionBackupManager:
    """Manages automated database and state backups for Riva Production."""

    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = Path(backup_dir) if backup_dir else Path.home() / ".riva" / "backups"

    def create_backup(self, source_path: str, backup_name: str = "riva_backup.zip") -> Optional[str]:
        """Creates a compressed ZIP backup of the specified file or directory."""
        source = Path(source_path)
        if not source.exists():
            return None

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        archive_path = self.backup_dir / backup_name

        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if source.is_file():
                    zipf.write(source, source.name)
                elif source.is_dir():
                    for file_path in source.rglob('*'):
                        if file_path.is_file():
                            zipf.write(file_path, file_path.relative_to(source.parent))
            return str(archive_path)
        except Exception:
            return None

    def restore_backup(self, archive_path: str, destination_path: str) -> bool:
        """Restores a backup archive to the target destination path."""
        archive = Path(archive_path)
        destination = Path(destination_path)
        if not archive.exists():
            return False

        try:
            destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(archive, 'r') as zipf:
                zipf.extractall(destination)
            return True
        except Exception:
            return False
