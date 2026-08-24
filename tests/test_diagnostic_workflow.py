from __future__ import annotations

from models import DatabaseStatistics
from services.firebird.diagnostics_service import (
    DiagnosticsService,
)


def make_stats(
    *,
    oldest_transaction: int = 100,
    oldest_active: int = 100,
    oldest_snapshot: int = 100,
    next_transaction: int = 100,
    no_reserve: bool = False,
) -> DatabaseStatistics:

    return DatabaseStatistics(
        oldest_transaction=oldest_transaction,
        oldest_active=oldest_active,
        oldest_snapshot=oldest_snapshot,
        next_transaction=next_transaction,
        no_reserve=no_reserve,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_diagnostics_ok():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        oldest_active=120,
        oldest_snapshot=130,
        next_transaction=500,
    )

    result = service.analyze(stats)

    assert result.status == "success"

    assert result.transaction_gap == 400
    assert result.active_gap == 20
    assert result.snapshot_gap == 30

    assert result.no_reserve_warning is False

    assert (
        result.message
        == "Baza działa prawidłowo."
    )


# ============================================================
# TRANSACTION WARNING
# ============================================================


def test_transaction_gap_warning():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        next_transaction=100_100,
    )

    result = service.analyze(stats)

    assert result.status == "warning"

    assert result.transaction_gap == 100_000

    assert (
        "Duży dystans transakcji."
        in result.message
    )


# ============================================================
# TRANSACTION ERROR
# ============================================================


def test_transaction_gap_error():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        next_transaction=1_000_100,
    )

    result = service.analyze(stats)

    assert result.status == "error"

    assert result.transaction_gap == 1_000_000

    assert (
        "Bardzo duży dystans transakcji."
        in result.message
    )


# ============================================================
# ACTIVE TRANSACTION WARNING
# ============================================================


def test_active_transaction_gap_warning():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        oldest_active=100_100,
        next_transaction=500,
    )

    result = service.analyze(stats)

    assert result.status == "warning"

    assert result.active_gap == 100_000

    assert (
        "Duży dystans aktywnej transakcji."
        in result.message
    )


# ============================================================
# SNAPSHOT WARNING
# ============================================================


def test_snapshot_gap_warning():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        oldest_snapshot=100_100,
        next_transaction=500,
    )

    result = service.analyze(stats)

    assert result.status == "warning"

    assert result.snapshot_gap == 100_000

    assert (
        "Duży dystans snapshot."
        in result.message
    )


# ============================================================
# NO RESERVE
# ============================================================


def test_no_reserve_is_information_only():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        oldest_active=120,
        oldest_snapshot=130,
        next_transaction=500,
        no_reserve=True,
    )

    result = service.analyze(stats)

    assert result.status == "success"

    assert result.no_reserve_warning is True

    assert (
        "No Reserve jest włączone."
        in result.message
    )


# ============================================================
# NO RESERVE + WARNING
# ============================================================


def test_no_reserve_does_not_override_warning():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        next_transaction=100_100,
        no_reserve=True,
    )

    result = service.analyze(stats)

    assert result.status == "warning"

    assert (
        "Duży dystans transakcji."
        in result.message
    )

    assert (
        "No Reserve jest włączone."
        in result.message
    )


# ============================================================
# ERROR HAS PRIORITY
# ============================================================


def test_error_has_priority_over_warnings():

    service = DiagnosticsService()

    stats = make_stats(
        oldest_transaction=100,
        oldest_active=100_100,
        oldest_snapshot=100_100,
        next_transaction=1_000_100,
    )

    result = service.analyze(stats)

    assert result.status == "error"

    assert result.transaction_gap == 1_000_000
    assert result.active_gap == 100_000
    assert result.snapshot_gap == 100_000

    assert (
        "Bardzo duży dystans transakcji."
        in result.message
    )

    assert (
        "Duży dystans aktywnej transakcji."
        in result.message
    )

    assert (
        "Duży dystans snapshot."
        in result.message
    )