from __future__ import annotations

from dataclasses import dataclass, field

from services.firebird.backup_service import BackupService
from services.firebird.diagnostics_service import (
    DiagnosticResult,
    DiagnosticsService,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
    RecommendationService,
)
from services.firebird.statistics_service import (
    StatisticsService,
)


@dataclass(slots=True)
class WorkflowStep:
    """
    Pojedynczy krok workflow.
    """

    name: str
    status: str = "PENDING"
    message: str = ""


@dataclass(slots=True)
class WorkflowResult:
    """
    Wynik kompletnego workflow Firebird.
    """

    success: bool = False

    initial_diagnostic: DiagnosticResult | None = None
    final_diagnostic: DiagnosticResult | None = None

    recommendations: RecommendationResult | None = None

    steps: list[WorkflowStep] = field(
        default_factory=list
    )

    backup_file: str = ""

    error: str = ""

    @property
    def has_error(self) -> bool:
        return bool(self.error)

    @property
    def has_recommendations(self) -> bool:
        if self.recommendations is None:
            return False

        return self.recommendations.has_recommendations


class WorkflowService:
    """
    Główny workflow serwisowy Firebird.

    Aktualny przebieg:

        1. Diagnostyka początkowa
        2. Backup
        3. Ponowna diagnostyka
        4. Rekomendacje

    Operacje ingerujące w bazę, takie jak MEND
    lub Restore, nie są wykonywane automatycznie.
    """

    def __init__(
        self,
        statistics_service: StatisticsService | None = None,
        diagnostics_service: DiagnosticsService | None = None,
        recommendation_service: RecommendationService | None = None,
        backup_service: BackupService | None = None,
    ) -> None:

        self.statistics_service = (
            statistics_service
            or StatisticsService()
        )

        self.diagnostics_service = (
            diagnostics_service
            or DiagnosticsService()
        )

        self.recommendation_service = (
            recommendation_service
            or RecommendationService()
        )

        self.backup_service = (
            backup_service
            or BackupService()
        )

    # ======================================================
    # PUBLIC
    # ======================================================

    def run(
        self,
        backup_file: str,
    ) -> WorkflowResult:
        """
        Wykonuje pełny bezpieczny workflow.

        Parametr:

            backup_file
                Docelowa ścieżka pliku FBK.
        """

        result = WorkflowResult()

        # ==================================================
        # DIAGNOSTYKA POCZĄTKOWA
        # ==================================================

        initial_step = WorkflowStep(
            name="Diagnostyka początkowa"
        )

        result.steps.append(
            initial_step
        )

        try:

            initial_stats = (
                self.statistics_service.statistics()
            )

            initial_diagnostic = (
                self.diagnostics_service.analyze(
                    initial_stats
                )
            )

            result.initial_diagnostic = (
                initial_diagnostic
            )

            initial_step.status = "SUCCESS"

            initial_step.message = (
                initial_diagnostic.message
            )

        except Exception as exc:

            initial_step.status = "ERROR"

            initial_step.message = str(exc)

            result.error = (
                f"Błąd diagnostyki początkowej: {exc}"
            )

            return result

        # ==================================================
        # BACKUP
        # ==================================================

        backup_step = WorkflowStep(
            name="Backup"
        )

        result.steps.append(
            backup_step
        )

        try:

            ok, log = self.backup_service.backup(
                backup_file
            )

            if not ok:

                backup_step.status = "ERROR"

                backup_step.message = (
                    log
                    or "Backup nie powiódł się."
                )

                result.error = (
                    backup_step.message
                )

                return result

            result.backup_file = str(
                backup_file
            )

            backup_step.status = "SUCCESS"

            backup_step.message = (
                log
                or "Backup wykonany pomyślnie."
            )

        except Exception as exc:

            backup_step.status = "ERROR"

            backup_step.message = str(exc)

            result.error = (
                f"Błąd backupu: {exc}"
            )

            return result

        # ==================================================
        # PONOWNA DIAGNOSTYKA
        # ==================================================

        final_step = WorkflowStep(
            name="Ponowna diagnostyka"
        )

        result.steps.append(
            final_step
        )

        try:

            final_stats = (
                self.statistics_service.statistics()
            )

            final_diagnostic = (
                self.diagnostics_service.analyze(
                    final_stats
                )
            )

            result.final_diagnostic = (
                final_diagnostic
            )

            final_step.status = "SUCCESS"

            final_step.message = (
                final_diagnostic.message
            )

        except Exception as exc:

            final_step.status = "ERROR"

            final_step.message = str(exc)

            result.error = (
                f"Błąd ponownej diagnostyki: {exc}"
            )

            return result

        # ==================================================
        # REKOMENDACJE
        # ==================================================

        recommendation_step = WorkflowStep(
            name="Rekomendacje"
        )

        result.steps.append(
            recommendation_step
        )

        try:

            recommendations = (
                self.recommendation_service.recommend(
                    result.final_diagnostic
                )
            )

            result.recommendations = (
                recommendations
            )

            recommendation_step.status = "SUCCESS"

            recommendation_step.message = (
                "Rekomendacje zostały wygenerowane."
            )

        except Exception as exc:

            recommendation_step.status = "ERROR"

            recommendation_step.message = str(exc)

            result.error = (
                f"Błąd generowania rekomendacji: {exc}"
            )

            return result

        # ==================================================
        # KONIEC
        # ==================================================

        result.success = True

        return result