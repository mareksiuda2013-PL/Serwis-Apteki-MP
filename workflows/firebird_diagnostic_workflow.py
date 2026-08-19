from __future__ import annotations

from dataclasses import dataclass

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
)
from services.firebird.statistics_service import (
    DatabaseStatistics,
)


@dataclass(slots=True)
class DiagnosticWorkflowResult:

    statistics: DatabaseStatistics
    diagnostic: DiagnosticResult
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
            self.controller.diagnostics()
        )

        recommendations = (
            self.controller.recommendations(
                diagnostic
            )
        )

        return DiagnosticWorkflowResult(
            statistics=statistics,
            diagnostic=diagnostic,
            recommendations=recommendations,
        )