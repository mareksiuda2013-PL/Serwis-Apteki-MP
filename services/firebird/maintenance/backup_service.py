from __future__ import annotations

from pathlib import Path

from services.firebird.base_firebird_service import (
    BaseFirebirdService,
)


class BackupService(BaseFirebirdService):

    def __init__(
        self,
        database: str | Path | None = None,
    ):

        super().__init__(
            database=database
        )

        if self.installation.gbak is None:

            raise RuntimeError(
                "Nie znaleziono gbak.exe."
            )

        self.gbak = self.installation.gbak

    def backup(
        self,
        destination: str | Path,
    ) -> tuple[bool, str]:

        destination = Path(
            destination
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        command = [
            str(self.gbak),
            "-b",
            "-g",
            "-v",
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
            str(self.database),
            str(destination),
        ]

        result = self.runner.run(
            command,
            timeout=1800,
            operation="BACKUP",
        )

        if result.success:

            return True, result.stdout

        return (
            False,
            result.stderr
            or result.stdout,
        )