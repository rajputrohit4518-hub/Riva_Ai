import subprocess

from app.desktop.catalog import DesktopApplicationCatalog
from app.desktop.models import DesktopActionResult


class DesktopLauncher:
    def __init__(
        self,
        catalog: DesktopApplicationCatalog | None = None,
    ) -> None:
        self._catalog = (
            catalog
            or DesktopApplicationCatalog()
        )

    def launch(
        self,
        application_name: str,
    ) -> DesktopActionResult:

        application = self._catalog.find(
            application_name
        )

        if application is None:
            return DesktopActionResult(
                success=False,
                application=application_name,
                message=(
                    f"Application not allowed or "
                    f"not installed: "
                    f"{application_name}"
                ),
            )

        process = subprocess.Popen(
            [application.executable],
            shell=False,
        )

        return DesktopActionResult(
            success=True,
            application=application.name,
            message=(
                f"Application launched: "
                f"{application.name}"
            ),
            pid=process.pid,
        )
