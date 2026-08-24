from __future__ import annotations

from services.firebird import FirebirdService
from services.firebird.diagnostics_service import (
    DiagnosticsService,
)
from services.firebird.health_service import HealthService
from services.firebird.recommendation_service import (
    RecommendationService,
)
from services.firebird.report_service import (
    ReportService,
)
from services.firebird.statistics_service import (
    StatisticsService,
)
from services.firebird.workflow_service import (
    WorkflowResult,
    WorkflowService,
)


class FirebirdController:
    """
    Główny kontroler usług Firebird.

    Łączy warstwę GUI / workflow
    z usługami Firebird.
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

        self.report_service = (
            ReportService()
        )

        self.workflow_service = (
            WorkflowService()
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

        return self.firebird.inspect_database(
            path
        )

    # ======================================================
    # STATYSTYKI
    # ======================================================

    def statistics(self):

        return (
            self.statistics_service.statistics()
        )

    # ======================================================
    # DIAGNOSTYKA
    # ======================================================

    def diagnostics(
        self,
        stats=None,
    ):

        if stats is None:

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
        Generuje rekomendacje na podstawie
        aktualnej diagnostyki.
        """

        if diagnostic is None:

            diagnostic = self.diagnostics()

        return self.recommendation_service.recommend(
            diagnostic
        )

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def health(
        self,
        stats=None,
    ):

        if stats is None:

            stats = self.statistics()

        return self.health_service.check(
            stats
        )

    # ======================================================
    # RAPORT
    # ======================================================

    def report(
        self,
        diagnostic=None,
        health=None,
        recommendations=None,
    ):
        """
        Generuje kompletny raport aktualnej bazy.

        Jeżeli dane nie zostały przekazane,
        kontroler pobiera je automatycznie.
        """

        database = self.database()

        statistics = self.statistics()

        if health is None:

            health = self.health(
                statistics
            )

        if diagnostic is None:

            diagnostic = self.diagnostics(
                statistics
            )

        if recommendations is None:

            recommendations = (
                self.recommendations(
                    diagnostic
                )
            )

        return self.report_service.generate(
            database=database,
            statistics=statistics,
            health=health,
            recommendations=recommendations,
        )

    # ======================================================
    # WORKFLOW
    # ======================================================

    def workflow(
        self,
        backup_file: str,
    ) -> WorkflowResult:
        """
        Uruchamia kompletny bezpieczny workflow Firebird.

        Aktualny przebieg:

            diagnostyka
                ↓
            backup
                ↓
            ponowna diagnostyka
                ↓
            rekomendacje

        Operacje naprawcze nie są wykonywane
        automatycznie.
        """

        return self.workflow_service.run(
            backup_file=backup_file
        )

    # ======================================================
    # RAPORT WORKFLOW
    # ======================================================

    def workflow_report(
        self,
        workflow: WorkflowResult,
    ):
        """
        Generuje raport na podstawie wyniku workflow.
        """

        return (
            self.report_service
            .generate_workflow_report(
                database=self.database(),
                workflow=workflow,
            )
        )