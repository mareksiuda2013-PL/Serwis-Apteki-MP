from __future__ import annotations

from services.firebird import FirebirdService
from services.firebird.health_service import HealthService
from services.firebird.statistics_service import StatisticsService


class FirebirdController:

    def __init__(self) -> None:

        self.firebird = FirebirdService()

        self.statistics_service = (
            StatisticsService()
        )

        self.health_service = (
            HealthService()
        )

    # ==================================================
    # DATABASE
    # ==================================================

    def database(self) -> str:

        return self.firebird.cfg.database

    # ==================================================
    # INFORMACJE
    # ==================================================

    def info(
        self,
        database: str | None = None,
    ):

        return self.firebird.get_info(
            database=database
        )

    # ==================================================
    # INSPEKCJA BAZY
    # ==================================================

    def inspect_database(
        self,
        path: str,
    ):

        return self.firebird.inspect_database(
            path
        )

    # ==================================================
    # STATYSTYKI
    # ==================================================

    def statistics(self):

        return (
            self.statistics_service.statistics()
        )

    # ==================================================
    # HEALTH CHECK
    # ==================================================

    def health(self):

        return self.health_service.check()