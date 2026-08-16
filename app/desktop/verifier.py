import subprocess

from app.desktop.models import DesktopActionResult


class DesktopVerifier:
    def verify(
        self,
        result: DesktopActionResult,
    ) -> DesktopActionResult:

        if not result.success:
            return result

        if result.pid is None:
            return DesktopActionResult(
                success=False,
                application=result.application,
                message=(
                    "Launch reported success "
                    "but no process ID was returned."
                ),
            )

        try:
            process = subprocess.run(
                [
                    "tasklist",
                    "/FI",
                    f"PID eq {result.pid}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False,
            )

            if str(result.pid) in process.stdout:
                return result

        except (
            subprocess.SubprocessError,
            OSError,
        ):
            pass

        return DesktopActionResult(
            success=False,
            application=result.application,
            message=(
                f"Could not verify process "
                f"{result.pid}."
            ),
            pid=result.pid,
        )
