from __future__ import annotations

from pathlib import Path

from config import Config
from core.process_runner import ProcessRunner
from services.firebird.installation_service import (
    InstallationService,
)


class ValidateService:

    def __init__(
        self,
        database: str | Path | None = None,
    ):

        self.cfg = Config()

        installation = (
            InstallationService()
            .first_installation()
        )

        if installation is None:

            raise RuntimeError(
                "Nie znaleziono Firebird."
            )

        if installation.gfix is None:

            raise RuntimeError(
                "Nie znaleziono gfix.exe."
            )

        self.gfix = installation.gfix
        self.runner = ProcessRunner()

        if database:

            self.database = Path(
                database
            )

        else:

            self.database = Path(
                self.cfg.database
            )

    def validate(self):

        cmd = [
            str(self.gfix),
            "-v",
            "-full",
            str(self.database),
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
        ]

        return self.runner.run(
            cmd,
            operation="VALIDATE",
        )