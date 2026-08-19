from __future__ import annotations

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.recommendation_service import (
    RecommendationService,
)


def test_recommendation_for_healthy_database():

    diagnostic = DiagnosticResult(
        status="success",
        transaction_gap=10_000,
        active_gap=100,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert result.has_recommendations
    assert len(result.recommendations) == 1
    assert (
        "Brak dodatkowych rekomendacji"
        in result.recommendations[0]
    )


def test_recommendation_for_large_transaction_gap():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=150_000,
        active_gap=100,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "Sweep" in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_for_very_large_transaction_gap():

    diagnostic = DiagnosticResult(
        status="error",
        transaction_gap=1_500_000,
        active_gap=100,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "diagnostyki" in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_for_active_transaction():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=10_000,
        active_gap=150_000,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "aktywnych transakcji" in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_for_snapshot():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=10_000,
        active_gap=100,
        snapshot_gap=150_000,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "snapshot" in recommendation.lower()
        for recommendation in result.recommendations
    )


def test_recommendation_for_no_reserve():

    diagnostic = DiagnosticResult(
        status="success",
        transaction_gap=10_000,
        active_gap=100,
        snapshot_gap=100,
        no_reserve_warning=True,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "No Reserve" in recommendation
        for recommendation in result.recommendations
    )