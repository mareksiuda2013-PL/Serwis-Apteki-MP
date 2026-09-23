from __future__ import annotations

from models import DatabaseStatistics


class StatisticsParser:
    """
    Parser wyjścia programu gstat.

    Odpowiada wyłącznie za zamianę tekstu
    zwróconego przez gstat na DatabaseStatistics.
    """

    def parse(
        self,
        output: str,
    ) -> DatabaseStatistics:

        stats = DatabaseStatistics()

        for raw_line in output.splitlines():

            line = raw_line.strip()

            if not line:
                continue

            self._parse_line(
                line,
                stats,
            )

        return stats

    # ==================================================
    # LINE PARSER
    # ==================================================

    def _parse_line(
        self,
        line: str,
        stats: DatabaseStatistics,
    ) -> None:

        if line.startswith("Page size"):

            stats.page_size = self._parse_int(
                line
            )

        elif line.startswith("ODS version"):

            stats.ods = self._parse_last_value(
                line
            )

        elif line.startswith("Sweep interval"):

            stats.sweep_interval = self._parse_int(
                line
            )

        elif line.startswith("Page buffers"):

            stats.page_buffers = self._parse_int(
                line
            )

        elif line.startswith("Next transaction"):

            stats.next_transaction = self._parse_int(
                line
            )

        elif line.startswith("Oldest transaction"):

            stats.oldest_transaction = self._parse_int(
                line
            )

        elif line.startswith("Oldest active"):

            stats.oldest_active = self._parse_int(
                line
            )

        elif line.startswith("Oldest snapshot"):

            stats.oldest_snapshot = self._parse_int(
                line
            )

        elif line.startswith("Database dialect"):

            stats.database_dialect = self._parse_int(
                line
            )

        elif line.startswith("Generation"):

            stats.generation = self._parse_int(
                line
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

            self._parse_attributes(
                line,
                stats,
            )

    # ==================================================
    # INTEGER
    # ==================================================

    @staticmethod
    def _parse_int(
        line: str,
    ) -> int:

        return int(
            line.split()[-1]
        )

    # ==================================================
    # LAST VALUE
    # ==================================================

    @staticmethod
    def _parse_last_value(
        line: str,
    ) -> str:

        return line.split()[-1]

    # ==================================================
    # ATTRIBUTES
    # ==================================================

    @staticmethod
    def _parse_attributes(
        line: str,
        stats: DatabaseStatistics,
    ) -> None:

        attributes = line.upper()

        stats.forced_writes = (
            "FORCE WRITE"
            in attributes
        )

        stats.no_reserve = (
            "NO RESERVE"
            in attributes
        )