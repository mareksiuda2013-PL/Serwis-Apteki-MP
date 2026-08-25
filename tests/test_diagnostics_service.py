from __future__ import annotations

from models import DatabaseStatistics
from services.firebird.diagnostics_service import (
    DiagnosticResult,
    DiagnosticsService,
)


def create_stats(
    *,
    oldest_transaction=100,
    oldest_active=150,
    oldest_snapshot=120,
    next_transaction=200,
    no_reserve=False,
):
    return DatabaseStatistics(
        oldest_transaction=oldest_transaction,
        oldest_active=oldest_active,
        oldest_snapshot=oldest_snapshot,
        next_transaction=next_transaction,
        no_reserve=no_reserve,
    )


def create_service():
    return DiagnosticsService()


# ==========================================================
# BASIC
# ==========================================================


def test_analyze_returns_diagnostic_result():

    service = create_service()

    result = service.analyze(
        create_stats()
    )

    assert isinstance(
        result,
        DiagnosticResult,
    )


# ==========================================================
# GAPS
# ==========================================================


def test_analyze_calculates_transaction_gap():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            next_transaction=500,
        )
    )

    assert result.transaction_gap == 400


def test_analyze_calculates_active_gap():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_active=350,
        )
    )

    assert result.active_gap == 250


def test_analyze_calculates_snapshot_gap():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_snapshot=450,
        )
    )

    assert result.snapshot_gap == 350


# ==========================================================
# SUCCESS
# ==========================================================


def test_normal_database_is_success():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_active=150,
            oldest_snapshot=120,
            next_transaction=200,
        )
    )

    assert result.status == "success"

    assert result.message == (
        "Baza działa prawidłowo."
    )


# ==========================================================
# TRANSACTION WARNING
# ==========================================================


def test_transaction_gap_100000_is_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            next_transaction=100100,
        )
    )

    assert result.transaction_gap == 100000
    assert result.status == "warning"

    assert (
        "Duży dystans transakcji."
        in result.message
    )


def test_transaction_gap_below_100000_is_success():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            next_transaction=100099,
        )
    )

    assert result.status == "success"


# ==========================================================
# TRANSACTION ERROR
# ==========================================================


def test_transaction_gap_1000000_is_error():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            next_transaction=1_000_100,
        )
    )

    assert result.transaction_gap == 1_000_000
    assert result.status == "error"

    assert (
        "Bardzo duży dystans transakcji."
        in result.message
    )


# ==========================================================
# ERROR HAS PRIORITY OVER WARNING
# ==========================================================


def test_error_has_priority_over_active_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_active=100_100,
            next_transaction=1_000_100,
        )
    )

    assert result.status == "error"

    assert (
        "Bardzo duży dystans transakcji."
        in result.message
    )

    assert (
        "Duży dystans aktywnej transakcji."
        in result.message
    )


# ==========================================================
# ACTIVE TRANSACTION WARNING
# ==========================================================


def test_active_gap_100000_is_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_active=100_100,
            next_transaction=200,
        )
    )

    assert result.active_gap == 100000
    assert result.status == "warning"

    assert (
        "Duży dystans aktywnej transakcji."
        in result.message
    )


# ==========================================================
# SNAPSHOT WARNING
# ==========================================================


def test_snapshot_gap_100000_is_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_snapshot=100_100,
            next_transaction=200,
        )
    )

    assert result.snapshot_gap == 100000
    assert result.status == "warning"

    assert (
        "Duży dystans snapshot."
        in result.message
    )


# ==========================================================
# NO RESERVE
# ==========================================================


def test_no_reserve_is_reported_as_information():

    service = create_service()

    result = service.analyze(
        create_stats(
            no_reserve=True
        )
    )

    assert result.no_reserve_warning is True

    assert result.status == "success"

    assert result.message == (
        "Baza działa prawidłowo. "
        "Informacja: No Reserve jest włączone."
    )


def test_no_reserve_does_not_create_warning_status():

    service = create_service()

    result = service.analyze(
        create_stats(
            no_reserve=True
        )
    )

    assert result.status == "success"


# ==========================================================
# COMBINED WARNINGS
# ==========================================================


def test_multiple_warnings_are_combined():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            oldest_active=100_100,
            oldest_snapshot=100_200,
            next_transaction=100_200,
        )
    )

    assert result.status == "warning"

    assert (
        "Duży dystans aktywnej transakcji."
        in result.message
    )

    assert (
        "Duży dystans snapshot."
        in result.message
    )


# ==========================================================
# WARNING + NO RESERVE
# ==========================================================


def test_warning_and_no_reserve_information_are_combined():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=100,
            next_transaction=100_100,
            no_reserve=True,
        )
    )

    assert result.status == "warning"

    assert (
        "Duży dystans transakcji."
        in result.message
    )

    assert (
        "Informacja: No Reserve jest włączone."
        in result.message
    )


# ==========================================================
# ZERO VALUES
# ==========================================================


def test_zero_transaction_values_are_allowed():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=0,
            oldest_active=0,
            oldest_snapshot=0,
            next_transaction=0,
        )
    )

    assert result.transaction_gap == 0
    assert result.active_gap == 0
    assert result.snapshot_gap == 0

    assert result.status == "success"


# ==========================================================
# NEGATIVE GAPS
# ==========================================================


def test_negative_gaps_do_not_create_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=500,
            oldest_active=100,
            oldest_snapshot=200,
            next_transaction=300,
        )
    )

    assert result.transaction_gap == -200
    assert result.active_gap == -400
    assert result.snapshot_gap == -300

    assert result.status == "success"


# ==========================================================
# EXACT ERROR THRESHOLD
# ==========================================================


def test_transaction_error_threshold_is_exact():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=0,
            next_transaction=1_000_000,
        )
    )

    assert result.status == "error"


# ==========================================================
# JUST BELOW ERROR THRESHOLD
# ==========================================================


def test_transaction_just_below_error_threshold_is_warning():

    service = create_service()

    result = service.analyze(
        create_stats(
            oldest_transaction=0,
            next_transaction=999_999,
        )
    )

    assert result.status == "warning"

    assert (
        "Duży dystans transakcji."
        in result.message
    )


# ==========================================================
# DEFAULT RESULT VALUES
# ==========================================================


def test_default_diagnostic_result():

    result = DiagnosticResult()

    assert result.status == "success"

    assert result.message == (
        "Baza działa prawidłowo."
    )

    assert result.transaction_gap == 0
    assert result.active_gap == 0
    assert result.snapshot_gap == 0

    assert result.no_reserve_warning is False