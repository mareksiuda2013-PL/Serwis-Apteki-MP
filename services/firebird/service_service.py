from __future__ import annotations

import subprocess
import time


class ServiceService:
    """
    Zarządza usługami Windows Firebird.
    """

    def exists(self, service_name: str) -> bool:

        result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        return result.returncode == 0

    def status(self, service_name: str) -> str:

        if not self.exists(service_name):
            return "Not Installed"

        result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        output = result.stdout.upper()

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

    def find_firebird_service(self) -> str | None:

        result = subprocess.run(
            [
                "sc",
                "query",
                "state=",
                "all",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():

            line = line.strip()

            if not line.startswith("SERVICE_NAME:"):
                continue

            service_name = line.split(
                "SERVICE_NAME:",
                1,
            )[1].strip()

            if "FIREBIRD" in service_name.upper():
                return service_name

        return None

    def start(
        self,
        service_name: str,
        timeout: int = 30,
    ) -> bool:

        if self.status(service_name) == "Running":
            return True

        result = subprocess.run(
            ["sc", "start", service_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            return False

        end_time = time.time() + timeout

        while time.time() < end_time:

            if self.status(service_name) == "Running":
                return True

            time.sleep(0.5)

        return False

    def stop(
        self,
        service_name: str,
        timeout: int = 30,
    ) -> bool:

        if self.status(service_name) == "Stopped":
            return True

        result = subprocess.run(
            ["sc", "stop", service_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            return False

        end_time = time.time() + timeout

        while time.time() < end_time:

            if self.status(service_name) == "Stopped":
                return True

            time.sleep(0.5)

        return False

    def restart(
        self,
        service_name: str,
    ) -> bool:

        if not self.stop(service_name):
            return False

        return self.start(service_name)