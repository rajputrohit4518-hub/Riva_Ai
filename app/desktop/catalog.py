import shutil

from app.desktop.models import DesktopApplication


class DesktopApplicationCatalog:
    def __init__(self) -> None:
        self._applications = {
            "notepad": DesktopApplication(
                name="notepad",
                executable="notepad.exe",
            ),
            "calculator": DesktopApplication(
                name="calculator",
                executable="calc.exe",
            ),
        }

    def find(
        self,
        name: str,
    ) -> DesktopApplication | None:

        key = name.strip().lower()

        application = self._applications.get(key)

        if application is None:
            return None

        if shutil.which(application.executable) is None:
            return None

        return application

    def names(self) -> list[str]:
        return sorted(self._applications)
