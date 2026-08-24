from __future__ import annotations

from pathlib import Path

from models import DatabaseStatistics

from services.firebird.base_firebird_service import (
    BaseFirebirdService,
)
from services.firebird.statistics_parser import (
    StatisticsParser,
)


class StatisticsService(BaseFirebirdService):

    def __init__(
        self,
        database: str | Path | None = None,
    ):

        super().__init__(
            database=database
        )

        if self.installation.gstat is None:

            raise RuntimeError(
                "Nie znaleziono gstat.exe."
            )

        self.gstat = self.installation.gstat

        self.parser = StatisticsParser()

    # ==================================================
    # GSTAT HEADER
    # ==================================================

    def header(self):

        command = [
            str(self.gstat),
            "-h",
            str(self.database),
            "-user",
            self.cfg.user,
            "-password",
            self.cfg.password,
        ]

        return self.runner.run(
            command,
            operation="GSTAT",
        )

    # ==================================================
    # STATISTICS
    # ==================================================

    def statistics(
        self,
    ) -> DatabaseStatistics:

        result = self.header()

        if not result.success:

            raise RuntimeError(
                result.stderr
                or result.stdout
                or "GSTAT zakończył się błędem."
            )

        return self.parser.parse(
            result.stdout
        )