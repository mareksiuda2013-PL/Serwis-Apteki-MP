from __future__ import annotations

from pathlib import Path

from config import Config
from core.process_runner import ProcessRunner

from .discovery.installation_service import InstallationService
from .service_service import ServiceService


class ValidateService:

    def __init__(
        self,
        database: str | Path | None = None,
    ) -> None:

        self.cfg = Config()

        self.service = ServiceService()
        self.runner = ProcessRunner()

        # ==================================================
        # AKTYWNA BAZA
        # ==================================================

        if database:

            self.database = Path(
                database
            )

        else:

            self.database = Path(
                self.cfg.database
            )

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.installation = (
            self.service_installation()
        )

        if self.installation is None:

            raise RuntimeError(
                "Nie znaleziono instalacji Firebird."
            )

        if self.installation.gfix is None:

            raise RuntimeError(
                "Nie znaleziono gfix.exe."
            )

        self.gfix = self.installation.gfix

    # ======================================================
    # INSTALACJA FIREBIRD
    # ======================================================

    def service_installation(self):

        return (
            InstallationService()
            .first_installation()
        )

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self):

        command = [
            str(self.gfix),
            "-validate",
            "-full",
            str(self.database),
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
        ]

        return self.runner.run(
            command,
            timeout=1800,
            operation="VALIDATE",
        )