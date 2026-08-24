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

    assert result.has_recommendations is True
    assert len(result.recommendations) == 1

    assert (
        "Brak dodatkowych rekomendacji"
        in result.recommendations[0]
    )


def test_recommendation_for_transaction_warning():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=100_000,
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


def test_recommendation_for_transaction_error():

    diagnostic = DiagnosticResult(
        status="error",
        transaction_gap=1_000_000,
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
        active_gap=100_000,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "aktywnych transakcji"
        in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_for_snapshot():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=10_000,
        active_gap=100,
        snapshot_gap=100_000,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert any(
        "snapshot"
        in recommendation.lower()
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

    assert result.has_recommendations is True

    assert any(
        "No Reserve"
        in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_combines_transaction_and_active_warning():

    diagnostic = DiagnosticResult(
        status="warning",
        transaction_gap=150_000,
        active_gap=150_000,
        snapshot_gap=100,
        no_reserve_warning=False,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert len(result.recommendations) == 2

    assert any(
        "Sweep"
        in recommendation
        for recommendation in result.recommendations
    )

    assert any(
        "aktywnych transakcji"
        in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_combines_error_and_all_warnings():

    diagnostic = DiagnosticResult(
        status="error",
        transaction_gap=1_500_000,
        active_gap=150_000,
        snapshot_gap=150_000,
        no_reserve_warning=True,
    )

    result = RecommendationService().recommend(
        diagnostic
    )

    assert len(result.recommendations) == 5

    assert any(
        "diagnostyki"
        in recommendation
        for recommendation in result.recommendations
    )

    assert any(
        "aktywnych transakcji"
        in recommendation
        for recommendation in result.recommendations
    )

    assert any(
        "snapshot"
        in recommendation.lower()
        for recommendation in result.recommendations
    )

    assert any(
        "No Reserve"
        in recommendation
        for recommendation in result.recommendations
    )


def test_recommendation_result_has_recommendations_property():

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

    assert result.has_recommendations is True
    assert isinstance(
        result.recommendations,
        list,
    )