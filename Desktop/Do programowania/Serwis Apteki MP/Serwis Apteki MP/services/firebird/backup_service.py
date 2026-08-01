from __future__ import annotations

import subprocess
from pathlib import Path

from config import Config
from .installation_service import InstallationService


class BackupService:

    def __init__(self):

        self.cfg = Config()

        installation = InstallationService().first_installation()

        if installation is None:
            raise RuntimeError("Nie znaleziono instalacji Firebird.")

        if installation.gbak is None:
            raise RuntimeError("Nie znaleziono programu gbak.exe.")

        self.gbak = installation.gbak

    def backup(
        self,
        destination: str | Path,
    ) -> tuple[bool, str]:

        destination = Path(destination)

        cmd = [
            str(self.gbak),
            "-b",
            "-g",
            "-v",
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
            self.cfg.database,
            str(destination),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            return False, result.stderr

        return True, result.stdout