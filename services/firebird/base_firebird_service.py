from __future__ import annotations

from pathlib import Path

from config import Config
from core.process_runner import ProcessRunner

from .discovery.installation_service import InstallationService


class BaseFirebirdService:

    def __init__(
        self,
        database: str | Path | None = None,
    ):

        self.cfg = Config()

        self.installation = (
            InstallationService()
            .first_installation()
        )

        if self.installation is None:

            raise RuntimeError(
                "Nie znaleziono instalacji Firebird."
            )

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