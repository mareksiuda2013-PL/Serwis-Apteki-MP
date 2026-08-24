from __future__ import annotations

import subprocess
import time


class ServiceService:
    """
    Zarządza usługami Windows Firebird.
    """

    # ==================================================
    # SC
    # ==================================================

    def _run_sc(
        self,
        command: str,
        service_name: str,
    ) -> tuple[bool, str]:

        try:

            result = subprocess.run(
                [
                    "sc",
                    command,
                    service_name,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

        except Exception as exc:

            return (
                False,
                str(exc),
            )

        output = (
            result.stdout
            or result.stderr
            or ""
        )

        return (
            result.returncode == 0,
            output.strip(),
        )

    # ==================================================
    # EXISTS
    # ==================================================

    def exists(
        self,
        service_name: str,
    ) -> bool:

        success, _ = self._run_sc(
            "query",
            service_name,
        )

        return success

    # ==================================================
    # STATUS
    # ==================================================

    def status(
        self,
        service_name: str,
    ) -> str:

        success, output = self._run_sc(
            "query",
            service_name,
        )

        if not success:
            return "Not Installed"

        output = output.upper()

        if "RUNNING" in output:
            return "Running"

        if "STOPPED" in output:
            return "Stopped"

        if "PAUSED" in output:
            return "Paused"

        if "STOP_PENDING" in output:
            return "Stop Pending"

        if "START_PENDING" in output:
            return "Start Pending"

        return "Unknown"

    # ==================================================
    # FIND FIREBIRD SERVICE
    # ==================================================

    def find_firebird_service(
        self,
    ) -> str | None:

        success, output = self._run_sc(
            "query",
            "state=",
        )

        if not success:
            return None

        if not output:
            return None

        for line in output.splitlines():

            line = line.strip()

            if not line.startswith(
                "SERVICE_NAME:"
            ):
                continue

            service_name = (
                line.split(
                    "SERVICE_NAME:",
                    1,
                )[1]
                .strip()
            )

            if (
                service_name
                and "FIREBIRD"
                in service_name.upper()
            ):
                return service_name

        return None

    # ==================================================
    # START
    # ==================================================

    def start(
        self,
        service_name: str,
        timeout: int = 30,
    ) -> bool:

        current_status = self.status(
            service_name
        )

        if current_status == "Running":
            return True

        success, _ = self._run_sc(
            "start",
            service_name,
        )

        if not success:
            return False

        if self.status(
            service_name
        ) in (
            "Running",
            "Start Pending",
        ):
            return True

        end_time = (
            time.time() + timeout
        )

        while time.time() < end_time:

            status = self.status(
                service_name
            )

            if status == "Running":
                return True

            if status != "Start Pending":
                return False

            time.sleep(0.5)

        return False

    # ==================================================
    # STOP
    # ==================================================

    def stop(
        self,
        service_name: str,
        timeout: int = 30,
    ) -> bool:

        current_status = self.status(
            service_name
        )

        if current_status == "Stopped":
            return True

        success, _ = self._run_sc(
            "stop",
            service_name,
        )

        if not success:
            return False

        if self.status(
            service_name
        ) in (
            "Stopped",
            "Stop Pending",
        ):
            return True

        end_time = (
            time.time() + timeout
        )

        while time.time() < end_time:

            status = self.status(
                service_name
            )

            if status == "Stopped":
                return True

            if status != "Stop Pending":
                return False

            time.sleep(0.5)

        return False

    # ==================================================
    # RESTART
    # ==================================================

    def restart(
        self,
        service_name: str,
    ) -> bool:

        if not self.stop(
            service_name
        ):
            return False

        return self.start(
            service_name
        )