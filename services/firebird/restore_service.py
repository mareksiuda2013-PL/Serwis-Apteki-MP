from __future__ import annotations

from pathlib import Path

from core.process_runner import ProcessRunner
from services.firebird.base_firebird_service import BaseFirebirdService


class RestoreService(BaseFirebirdService):

    def __init__(self):
        super().__init__()

        if self.installation.gbak is None:
            raise RuntimeError("Nie znaleziono gbak.exe.")

        self.gbak = self.installation.gbak

    def restore(
        self,
        backup_file: str | Path,
        database_file: str | Path,
        replace: bool = True,
    ):

        backup_file = Path(backup_file)
        database_file = Path(database_file)

        if not backup_file.exists():
            return False, f"Nie znaleziono backupu:\n{backup_file}"

        if database_file.exists() and not replace:
            return False, f"Baza już istnieje:\n{database_file}"

        command = [
            str(self.gbak),
            "-c",
            "-v",
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
            str(backup_file),
            str(database_file),
        ]

        if replace:
            command.insert(2, "-rep")

        result = self.runner.run(
        command,
        timeout=1800,
        operation="RESTORE",
)

        if result.success:
            return True, result.stdout

        return False, result.stderr or result.stdout