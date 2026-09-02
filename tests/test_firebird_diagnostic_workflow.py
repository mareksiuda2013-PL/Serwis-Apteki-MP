from __future__ import annotations

from unittest.mock import MagicMock

from services.firebird.diagnostics_service import DiagnosticResult
from services.firebird.health_service import DatabaseHealth
from services.firebird.recommendation_service import RecommendationResult
from services.firebird.statistics_service import DatabaseStatistics
from workflows.firebird_diagnostic_workflow import (
    DiagnosticWorkflow,
    DiagnosticWorkflowResult,
)


def create_workflow():
    controller = MagicMock()

    statistics = MagicMock(spec=DatabaseStatistics)
    diagnostic = DiagnosticResult()
    health = MagicMock(spec=DatabaseHealth)
    recommendations = RecommendationResult(
        recommendations=[
            "Testowa rekomendacja.",
        ]
    )

    controller.statistics.return_value = statistics
    controller.diagnostics.return_value = diagnostic
    controller.health.return_value = health
    controller.recommendations.return_value = recommendations

    return (
        DiagnosticWorkflow(controller),
        controller,
        statistics,
        diagnostic,
        health,
        recommendations,
    )


def test_workflow_returns_result():
    (
        workflow,
        _,
        _,
        _,
        _,
        _,
    ) = create_workflow()

    result = workflow.run()

    assert isinstance(
        result,
        DiagnosticWorkflowResult,
    )


def test_workflow_gets_statistics_once():
    (
        workflow,
        controller,
        statistics,
        _,
        _,
        _,
    ) = create_workflow()

    result = workflow.run()

    controller.statistics.assert_called_once_with()

    assert result.statistics is statistics


def test_workflow_passes_statistics_to_diagnostics_and_health():
    (
        workflow,
        controller,
        statistics,
        _,
        health,
        _,
    ) = create_workflow()

    result = workflow.run()

    controller.diagnostics.assert_called_once_with(
        statistics
    )

    controller.health.assert_called_once_with(
        statistics
    )

    assert result.health is health


def test_workflow_passes_diagnostic_to_recommendations():
    (
        workflow,
        controller,
        _,
        diagnostic,
        _,
        recommendations,
    ) = create_workflow()

    result = workflow.run()

    controller.recommendations.assert_called_once_with(
        diagnostic
    )

    assert result.diagnostic is diagnostic
    assert result.recommendations is recommendations