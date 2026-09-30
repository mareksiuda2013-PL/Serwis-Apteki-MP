from __future__ import annotations

from dataclasses import dataclass

from services.firebird.database.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.database.health_service import (
    DatabaseHealth,
)
from services.firebird.reporting.recommendation_service import (
    RecommendationResult,
)
from services.firebird.database.statistics_service import (
    DatabaseStatistics,
)


@dataclass(slots=True)
class DiagnosticWorkflowResult:

    statistics: DatabaseStatistics
    diagnostic: DiagnosticResult
    health: DatabaseHealth
    recommendations: RecommendationResult


class DiagnosticWorkflow:

    def __init__(
        self,
        controller,
    ) -> None:

        self.controller = controller

    def run(
        self,
    ) -> DiagnosticWorkflowResult:

        statistics = (
            self.controller.statistics()
        )

        diagnostic = (
            self.controller.diagnostics(
                statistics
            )
        )

        health = (
            self.controller.health(
                statistics
            )
        )

        recommendations = (
            self.controller.recommendations(
                diagnostic
            )
        )

        return DiagnosticWorkflowResult(
            statistics=statistics,
            diagnostic=diagnostic,
            health=health,
            recommendations=recommendations,
        )

