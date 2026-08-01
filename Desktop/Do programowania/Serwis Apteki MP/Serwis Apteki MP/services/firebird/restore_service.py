from __future__ import annotations

import subprocess
from pathlib import Path

from config import Config
from .installation_service import InstallationService


class RestoreService:

    def __init__(self):

        self.cfg = Config()

        installation = InstallationService().first_installation()

        if installation is None:
            raise RuntimeError("Nie znaleziono instalacji Firebird.")

        if installation.gbak is None:
            raise RuntimeError("Nie znaleziono gbak.exe.")

        self.gbak = installation.gbak

    def restore(
        self,
        backup_file: str | Path,
        database_file: str | Path,
        replace: bool = True,
    ) -> tuple[bool, str]:

        backup_file = Path(backup_file)
        database_file = Path(database_file)

        cmd = [
            str(self.gbak),
            "-c",
        ]

        if replace:
            cmd.append("-rep")

        cmd = [
    str(self.gbak),
    "-rep",
    "-v",
    "-user",
    self.cfg.user,
    "-password",
    self.cfg.password,
    str(backup_file),
    str(database_file),
]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )