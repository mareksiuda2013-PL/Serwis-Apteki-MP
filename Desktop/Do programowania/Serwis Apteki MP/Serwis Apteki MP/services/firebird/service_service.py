from __future__ import annotations

import subprocess


class ServiceService:
    """
    Zarządza usługami Windows Firebird.
    """

    def exists(self, service_name: str) -> bool:

        result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    def status(self, service_name: str) -> str:

        if not self.exists(service_name):
            return "Not Installed"

        result = subprocess.run(
            ["sc", "query", service_name],
            capture_output=True,
            text=True,
        )

        output = result.stdout.upper()

        if "RUNNING" in output:
            return "Running"

        if "STOPPED" in output:
            return "Stopped"

        if "PAUSED" in output:
            return "Paused"

        return "Unknown"

    def start(self, service_name: str) -> bool:

        result = subprocess.run(
            ["sc", "start", service_name],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    def stop(self, service_name: str) -> bool:

        result = subprocess.run(
            ["sc", "stop", service_name],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0

    def restart(self, service_name: str) -> bool:

        self.stop(service_name)

        return self.start(service_name)