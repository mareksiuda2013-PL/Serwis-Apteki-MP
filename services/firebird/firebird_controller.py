from __future__ import annotations

from services.firebird import FirebirdService
from services.firebird.diagnostics_service import (
    DiagnosticsService,
)
from services.firebird.health_service import HealthService
from services.firebird.recommendation_service import (
    RecommendationService,
)
from services.firebird.statistics_service import StatisticsService


class FirebirdController:
    """
    Główny kontroler usług Firebird.

    Odpowiada za połączenie warstwy GUI / workflow
    z usługami odpowiedzialnymi za:
        - informacje o bazie,
        - statystyki,
        - diagnostykę,
        - rekomendacje,
        - health check.
    """

    def __init__(self) -> None:

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.firebird = FirebirdService()

        # ==================================================
        # SERVICES
        # ==================================================

        self.statistics_service = (
            StatisticsService()
        )

        self.health_service = (
            HealthService()
        )

        self.diagnostics_service = (
            DiagnosticsService()
        )

        self.recommendation_service = (
            RecommendationService()
        )

    # ======================================================
    # DATABASE
    # ======================================================

    def database(self) -> str:
        """
        Zwraca aktualnie skonfigurowaną bazę danych.
        """

        return self.firebird.cfg.database

    # ======================================================
    # INFORMACJE
    # ======================================================

    def info(
        self,
        database: str | None = None,
    ):
        """
        Pobiera podstawowe informacje o bazie Firebird.
        """

        return self.firebird.get_info(
            database=database
        )

    # ======================================================
    # INSPEKCJA BAZY
    # ======================================================

    def inspect_database(
        self,
        path: str,
    ):
        """
        Wykonuje inspekcję wskazanego pliku bazy.
        """

        return self.firebird.inspect_database(
            path
        )

    # ======================================================
    # STATYSTYKI
    # ======================================================

    def statistics(self):
        """
        Pobiera statystyki bazy Firebird.
        """

        return (
            self.statistics_service.statistics()
        )

    # ======================================================
    # DIAGNOSTYKA
    # ======================================================

    def diagnostics(self):
        """
        Analizuje aktualne statystyki bazy.
        """

        stats = self.statistics()

        return self.diagnostics_service.analyze(
            stats
        )

    # ======================================================
    # REKOMENDACJE
    # ======================================================

    def recommendations(
        self,
        diagnostic=None,
    ):
        """
        Generuje rekomendacje na podstawie diagnostyki.

        Jeżeli wynik diagnostyki nie został przekazany,
        zostanie pobrany automatycznie.
        """

        if diagnostic is None:

            diagnostic = self.diagnostics()

        return self.recommendation_service.recommend(
            diagnostic
        )

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health(self):
        """
        Wykonuje pełny health check bazy.
        """

        return self.health_service.check()