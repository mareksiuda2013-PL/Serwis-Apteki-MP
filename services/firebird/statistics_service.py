from __future__ import annotations

from pathlib import Path

from models import DatabaseStatistics

from services.firebird.base_firebird_service import (
    BaseFirebirdService,
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

    def statistics(
        self,
    ) -> DatabaseStatistics:

        result = self.header()

        if not result.success:

            raise RuntimeError(
                result.stderr
                or result.stdout
            )

        stats = DatabaseStatistics()

        for raw_line in result.stdout.splitlines():

            line = raw_line.strip()

            if line.startswith("Page size"):

                stats.page_size = int(
                    line.split()[-1]
                )

            elif line.startswith("ODS version"):

                stats.ods = line.split()[-1]

            elif line.startswith("Sweep interval"):

                stats.sweep_interval = int(
                    line.split()[-1]
                )

            elif line.startswith("Page buffers"):

                stats.page_buffers = int(
                    line.split()[-1]
                )

            elif line.startswith("Next transaction"):

                stats.next_transaction = int(
                    line.split()[-1]
                )

            elif line.startswith("Oldest transaction"):

                stats.oldest_transaction = int(
                    line.split()[-1]
                )

            elif line.startswith("Oldest active"):

                stats.oldest_active = int(
                    line.split()[-1]
                )

            elif line.startswith("Oldest snapshot"):

                stats.oldest_snapshot = int(
                    line.split()[-1]
                )

            elif line.startswith("Database dialect"):

                stats.database_dialect = int(
                    line.split()[-1]
                )

            elif line.startswith("Generation"):

                stats.generation = int(
                    line.split()[-1]
                )

            elif line.startswith("Creation date"):

                stats.creation_date = (
                    line
                    .split(
                        "Creation date",
                        1,
                    )[1]
                    .strip()
                )

            elif line.startswith("Attributes"):

                attributes = line.upper()

                stats.forced_writes = (
                    "FORCE WRITE"
                    in attributes
                )

                stats.no_reserve = (
                    "NO RESERVE"
                    in attributes
                )

        return stats