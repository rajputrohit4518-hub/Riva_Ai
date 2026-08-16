from app.capabilities.models import (
    Capability,
    PermissionLevel,
)
from app.desktop.catalog import DesktopApplicationCatalog
from app.desktop.launcher import DesktopLauncher
from app.desktop.models import DesktopActionResult
from app.desktop.verifier import DesktopVerifier


class DesktopCapability:
    def __init__(
        self,
        catalog: DesktopApplicationCatalog | None = None,
        launcher: DesktopLauncher | None = None,
        verifier: DesktopVerifier | None = None,
    ) -> None:
        self._catalog = (
            catalog or DesktopApplicationCatalog()
        )
        self._launcher = (
            launcher or DesktopLauncher(self._catalog)
        )
        self._verifier = (
            verifier or DesktopVerifier()
        )

    def launch(
        self,
        application: str,
    ) -> DesktopActionResult:

        result = self._launcher.launch(
            application
        )

        return self._verifier.verify(result)

    def capability(
        self,
        permission: PermissionLevel = (
            PermissionLevel.CONFIRM
        ),
    ) -> Capability:

        return Capability(
            name="desktop.launch",
            description=(
                "Launch an allowed Windows application "
                "and verify that it started."
            ),
            permission=permission,
            execute=self.launch,
        )
