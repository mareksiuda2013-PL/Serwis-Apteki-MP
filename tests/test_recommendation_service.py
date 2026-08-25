from __future__ import annotations

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
    RecommendationService,
)


def create_service():
    return RecommendationService()


def create_diagnostic(
    *,
    transaction_gap=0,
    active_gap=0,
    snapshot_gap=0,
    status="success",
    no_reserve_warning=False,
):
    return DiagnosticResult(
        status=status,
        transaction_gap=transaction_gap,
        active_gap=active_gap,
        snapshot_gap=snapshot_gap,
        no_reserve_warning=no_reserve_warning,
    )


# ==========================================================
# BASIC
# ==========================================================


def test_recommend_returns_recommendation_result():

    service = create_service()

    result = service.recommend(
        create_diagnostic()
    )

    assert isinstance(
        result,
        RecommendationResult,
    )


# ==========================================================
# NO PROBLEMS
# ==========================================================


def test_no_problems_returns_default_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic()
    )

    assert result.recommendations == [
        (
            "Brak dodatkowych rekomendacji. "
            "Baza działa prawidłowo."
        )
    ]


def test_no_problems_has_recommendations():

    service = create_service()

    result = service.recommend(
        create_diagnostic()
    )

    assert result.has_recommendations is True


# ==========================================================
# TRANSACTION GAP — WARNING
# ==========================================================


def test_transaction_gap_100000_recommends_sweep():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=100_000
        )
    )

    assert result.recommendations == [
        "Zalecane wykonanie Sweep bazy danych."
    ]


def test_transaction_gap_below_100000_has_no_sweep_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=99_999
        )
    )

    assert result.recommendations == [
        (
            "Brak dodatkowych rekomendacji. "
            "Baza działa prawidłowo."
        )
    ]


# ==========================================================
# TRANSACTION GAP — ERROR
# ==========================================================


def test_transaction_gap_1000000_recommends_diagnostics():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=1_000_000
        )
    )

    assert (
        "Zalecane wykonanie diagnostyki transakcji "
        "oraz sprawdzenie możliwości wykonania Sweep."
        in result.recommendations
    )


def test_transaction_gap_1000000_does_not_recommend_simple_sweep():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=1_000_000
        )
    )

    assert (
        "Zalecane wykonanie Sweep bazy danych."
        not in result.recommendations
    )


def test_transaction_gap_999999_recommends_sweep():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=999_999
        )
    )

    assert (
        "Zalecane wykonanie Sweep bazy danych."
        in result.recommendations
    )


# ==========================================================
# ACTIVE TRANSACTIONS
# ==========================================================


def test_active_gap_100000_recommends_check():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            active_gap=100_000
        )
    )

    assert result.recommendations == [
        (
            "Zalecane sprawdzenie długo trwających "
            "aktywnych transakcji."
        )
    ]


def test_active_gap_below_threshold_has_no_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            active_gap=99_999
        )
    )

    assert result.recommendations == [
        (
            "Brak dodatkowych rekomendacji. "
            "Baza działa prawidłowo."
        )
    ]


# ==========================================================
# SNAPSHOT
# ==========================================================


def test_snapshot_gap_100000_recommends_check():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            snapshot_gap=100_000
        )
    )

    assert result.recommendations == [
        (
            "Zalecane sprawdzenie długotrwałych "
            "snapshotów transakcyjnych."
        )
    ]


def test_snapshot_gap_below_threshold_has_no_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            snapshot_gap=99_999
        )
    )

    assert result.recommendations == [
        (
            "Brak dodatkowych rekomendacji. "
            "Baza działa prawidłowo."
        )
    ]


# ==========================================================
# ERROR STATUS
# ==========================================================


def test_error_status_adds_diagnostic_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            status="error"
        )
    )

    assert result.recommendations == [
        (
            "Baza wymaga szczegółowej diagnostyki "
            "przed wykonaniem operacji naprawczych."
        )
    ]


def test_warning_status_does_not_add_error_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            status="warning"
        )
    )

    assert result.recommendations == [
        (
            "Brak dodatkowych rekomendacji. "
            "Baza działa prawidłowo."
        )
    ]


# ==========================================================
# NO RESERVE
# ==========================================================


def test_no_reserve_adds_information():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            no_reserve_warning=True
        )
    )

    assert result.recommendations == [
        (
            "No Reserve jest włączone. "
            "Jest to informacja konfiguracyjna "
            "i nie oznacza uszkodzenia bazy."
        )
    ]


def test_no_reserve_is_not_error_recommendation():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            no_reserve_warning=True
        )
    )

    assert not any(
        "uszkodzenia" not in recommendation
        and "No Reserve" not in recommendation
        for recommendation in result.recommendations
    )


# ==========================================================
# MULTIPLE RECOMMENDATIONS
# ==========================================================


def test_multiple_recommendations_are_combined():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=100_000,
            active_gap=100_000,
            snapshot_gap=100_000,
            no_reserve_warning=True,
        )
    )

    assert len(
        result.recommendations
    ) == 4

    assert (
        "Zalecane wykonanie Sweep bazy danych."
        in result.recommendations
    )

    assert (
        "Zalecane sprawdzenie długo trwających "
        "aktywnych transakcji."
        in result.recommendations
    )

    assert (
        "Zalecane sprawdzenie długotrwałych "
        "snapshotów transakcyjnych."
        in result.recommendations
    )

    assert (
        "No Reserve jest włączone. "
        "Jest to informacja konfiguracyjna "
        "i nie oznacza uszkodzenia bazy."
        in result.recommendations
    )


# ==========================================================
# ERROR + ALL OTHER CONDITIONS
# ==========================================================


def test_error_with_all_conditions_combines_all_recommendations():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=1_000_000,
            active_gap=100_000,
            snapshot_gap=100_000,
            status="error",
            no_reserve_warning=True,
        )
    )

    assert len(
        result.recommendations
    ) == 5

    assert (
        "Zalecane wykonanie diagnostyki transakcji "
        "oraz sprawdzenie możliwości wykonania Sweep."
        in result.recommendations
    )

    assert (
        "Zalecane sprawdzenie długo trwających "
        "aktywnych transakcji."
        in result.recommendations
    )

    assert (
        "Zalecane sprawdzenie długotrwałych "
        "snapshotów transakcyjnych."
        in result.recommendations
    )

    assert (
        "Baza wymaga szczegółowej diagnostyki "
        "przed wykonaniem operacji naprawczych."
        in result.recommendations
    )

    assert (
        "No Reserve jest włączone. "
        "Jest to informacja konfiguracyjna "
        "i nie oznacza uszkodzenia bazy."
        in result.recommendations
    )


# ==========================================================
# RESULT PROPERTY
# ==========================================================


def test_has_recommendations_returns_true_when_list_not_empty():

    result = RecommendationResult(
        recommendations=[
            "Testowa rekomendacja"
        ]
    )

    assert result.has_recommendations is True


def test_has_recommendations_returns_false_when_list_empty():

    result = RecommendationResult(
        recommendations=[]
    )

    assert result.has_recommendations is False


# ==========================================================
# RECOMMENDATION ORDER
# ==========================================================


def test_recommendations_keep_expected_order():

    service = create_service()

    result = service.recommend(
        create_diagnostic(
            transaction_gap=100_000,
            active_gap=100_000,
            snapshot_gap=100_000,
            status="error",
            no_reserve_warning=True,
        )
    )

    assert result.recommendations[0] == (
        "Zalecane wykonanie Sweep bazy danych."
    )

    assert result.recommendations[1] == (
        "Zalecane sprawdzenie długo trwających "
        "aktywnych transakcji."
    )

    assert result.recommendations[2] == (
        "Zalecane sprawdzenie długotrwałych "
        "snapshotów transakcyjnych."
    )

    assert result.recommendations[3] == (
        "Baza wymaga szczegółowej diagnostyki "
        "przed wykonaniem operacji naprawczych."
    )

    assert result.recommendations[4] == (
        "No Reserve jest włączone. "
        "Jest to informacja konfiguracyjna "
        "i nie oznacza uszkodzenia bazy."
    )