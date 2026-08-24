from __future__ import annotations

from unittest.mock import MagicMock

from models import DatabaseStatistics
from services.firebird.health_service import HealthService


def create_stats(
    *,
    ods: str = "13.0",
    page_size: int = 8192,
    sweep_interval: int = 20000,
    oldest_transaction: int = 100,
    oldest_active: int = 200,
    next_transaction: int = 500,
    forced_writes: bool = True,
    no_reserve: bool = True,
) -> DatabaseStatistics:

    return DatabaseStatistics(
        ods=ods,
        page_size=page_size,
        page_buffers=2048,
        sweep_interval=sweep_interval,
        oldest_transaction=oldest_transaction,
        oldest_active=oldest_active,
        oldest_snapshot=300,
        next_transaction=next_transaction,
        database_dialect=3,
        generation=10,
        forced_writes=forced_writes,
        no_reserve=no_reserve,
    )


def create_service() -> HealthService:

    service = HealthService()

    service.statistics_service = MagicMock()

    return service


# ==========================================================
# HEALTHY DATABASE
# ==========================================================


def test_health_check_healthy_database():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    assert result.status == "OK"

    assert (
        result.summary
        == "Baza wygląda prawidłowo."
    )

    assert len(result.checks) == 7

    statuses = [
        check.status
        for check in result.checks
    ]

    assert all(
        status == "OK"
        for status in statuses
    )


# ==========================================================
# ODS
# ==========================================================


def test_health_ods_missing():

    service = create_service()

    stats = create_stats(
        ods=""
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "ODS"
    )

    assert check.status == "WARNING"
    assert check.value == "-"
    assert (
        check.message
        == "Brak informacji o ODS."
    )

    assert result.status == "WARNING"


# ==========================================================
# PAGE SIZE
# ==========================================================


def test_health_page_size_valid():

    service = create_service()

    valid_sizes = {
        1024,
        2048,
        4096,
        8192,
        16384,
        32768,
    }

    for page_size in valid_sizes:

        result = service.check(
            create_stats(
                page_size=page_size
            )
        )

        check = next(
            check
            for check in result.checks
            if check.name == "Page Size"
        )

        assert check.status == "OK"
        assert check.value == str(page_size)


def test_health_page_size_invalid():

    service = create_service()

    result = service.check(
        create_stats(
            page_size=12345
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Page Size"
    )

    assert check.status == "WARNING"
    assert check.value == "12345"

    assert (
        check.message
        == "Nietypowy rozmiar strony."
    )

    assert result.status == "WARNING"


# ==========================================================
# SWEEP
# ==========================================================


def test_health_sweep_enabled():

    service = create_service()

    result = service.check(
        create_stats(
            sweep_interval=20000
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "OK"
    assert check.value == "20000"

    assert (
        check.message
        == "Sweep jest skonfigurowany."
    )


def test_health_sweep_disabled():

    service = create_service()

    result = service.check(
        create_stats(
            sweep_interval=0
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "WARNING"
    assert check.value == "0"

    assert (
        check.message
        == "Sweep jest wyłączony."
    )

    assert result.status == "WARNING"


def test_health_sweep_negative():

    service = create_service()

    result = service.check(
        create_stats(
            sweep_interval=-1
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "WARNING"


# ==========================================================
# TRANSACTIONS
# ==========================================================


def test_health_transactions_normal():

    service = create_service()

    result = service.check(
        create_stats(
            oldest_transaction=100,
            next_transaction=500,
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "OK"
    assert check.value == "400"

    assert (
        check.message
        == "Transakcje wyglądają prawidłowo."
    )


def test_health_transactions_large_difference():

    service = create_service()

    result = service.check(
        create_stats(
            oldest_transaction=100,
            next_transaction=1_000_100,
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "WARNING"
    assert check.value == "1000000"

    assert (
        "Duża różnica"
        in check.message
    )

    assert result.status == "WARNING"


def test_health_transactions_missing():

    service = create_service()

    result = service.check(
        create_stats(
            oldest_transaction=100,
            next_transaction=0,
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "WARNING"
    assert check.value == "-"

    assert (
        check.message
        == "Brak poprawnych danych transakcyjnych."
    )


# ==========================================================
# OLDEST ACTIVE
# ==========================================================


def test_health_oldest_active_valid():

    service = create_service()

    result = service.check(
        create_stats(
            oldest_transaction=100,
            oldest_active=200,
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Oldest Active"
    )

    assert check.status == "OK"
    assert check.value == "200"

    assert (
        "mieści się w zakresie"
        in check.message
    )


def test_health_oldest_active_invalid():

    service = create_service()

    result = service.check(
        create_stats(
            oldest_transaction=200,
            oldest_active=100,
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Oldest Active"
    )

    assert check.status == "WARNING"
    assert check.value == "100"

    assert (
        "wymaga sprawdzenia"
        in check.message
    )

    assert result.status == "WARNING"


# ==========================================================
# FORCE WRITE
# ==========================================================


def test_health_force_write_enabled():

    service = create_service()

    result = service.check(
        create_stats(
            forced_writes=True
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Force Write"
    )

    assert check.status == "OK"
    assert check.value == "ON"

    assert (
        "włączone"
        in check.message
    )


def test_health_force_write_disabled():

    service = create_service()

    result = service.check(
        create_stats(
            forced_writes=False
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "Force Write"
    )

    assert check.status == "WARNING"
    assert check.value == "OFF"

    assert (
        "wyłączone"
        in check.message
    )

    assert result.status == "WARNING"


# ==========================================================
# NO RESERVE
# ==========================================================


def test_health_no_reserve_enabled():

    service = create_service()

    result = service.check(
        create_stats(
            no_reserve=True
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "No Reserve"
    )

    assert check.status == "OK"
    assert check.value == "ON"

    assert (
        "ustawione"
        in check.message
    )


def test_health_no_reserve_disabled():

    service = create_service()

    result = service.check(
        create_stats(
            no_reserve=False
        )
    )

    check = next(
        check
        for check in result.checks
        if check.name == "No Reserve"
    )

    assert check.status == "WARNING"
    assert check.value == "OFF"

    assert (
        "nie jest ustawione"
        in check.message
    )

    assert result.status == "WARNING"


# ==========================================================
# STATISTICS SERVICE
# ==========================================================


def test_health_loads_statistics_when_not_provided():

    service = create_service()

    stats = create_stats()

    service.statistics_service.statistics.return_value = (
        stats
    )

    result = service.check()

    service.statistics_service.statistics.assert_called_once()

    assert result.status == "OK"


def test_health_does_not_load_statistics_when_provided():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    service.statistics_service.statistics.assert_not_called()

    assert result.status == "OK"


# ==========================================================
# STATISTICS ERROR
# ==========================================================


def test_health_returns_error_when_statistics_fail():

    service = create_service()

    service.statistics_service.statistics.side_effect = (
        RuntimeError("GSTAT ERROR")
    )

    result = service.check()

    assert result.status == "ERROR"

    assert (
        result.summary
        == "Nie udało się pobrać statystyk bazy."
    )

    assert len(result.checks) == 1

    check = result.checks[0]

    assert check.name == "Połączenie"
    assert check.status == "ERROR"
    assert check.value == "-"
    assert check.message == "GSTAT ERROR"


# ==========================================================
# FINAL STATUS PRIORITY
# ==========================================================


def test_health_error_has_priority():

    service = create_service()

    stats = create_stats(
        ods="",
        page_size=12345,
        sweep_interval=0,
        forced_writes=False,
        no_reserve=False,
    )

    result = service.check(stats)

    assert result.status == "WARNING"

    assert (
        result.summary
        == "Wykryto 5 ostrzeżeń."
    )


def test_health_all_checks_ok():

    service = create_service()

    stats = create_stats(
        ods="13.0",
        page_size=8192,
        sweep_interval=20000,
        oldest_transaction=100,
        oldest_active=200,
        next_transaction=500,
        forced_writes=True,
        no_reserve=True,
    )

    result = service.check(stats)

    assert result.status == "OK"

    assert (
        result.summary
        == "Baza wygląda prawidłowo."
    )

    assert all(
        check.status == "OK"
        for check in result.checks
    )