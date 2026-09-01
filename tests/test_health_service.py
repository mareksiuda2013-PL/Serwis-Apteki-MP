from __future__ import annotations

from unittest.mock import MagicMock, patch

from models.database_health import (
    DatabaseHealth,
    HealthCheck,
)
from services.firebird.health_service import (
    HealthService,
)


def create_service():

    service = HealthService.__new__(
        HealthService
    )

    service.statistics_service = MagicMock()

    return service


def create_stats(
    *,
    ods="13.0",
    page_size=4096,
    sweep_interval=20000,
    oldest_transaction=100,
    oldest_active=150,
    oldest_snapshot=120,
    next_transaction=200,
    forced_writes=True,
    no_reserve=True,
):

    stats = MagicMock()

    stats.ods = ods
    stats.page_size = page_size
    stats.sweep_interval = sweep_interval

    stats.oldest_transaction = (
        oldest_transaction
    )

    stats.oldest_active = (
        oldest_active
    )

    stats.oldest_snapshot = (
        oldest_snapshot
    )

    stats.next_transaction = (
        next_transaction
    )

    stats.forced_writes = forced_writes
    stats.no_reserve = no_reserve

    return stats


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_init_creates_statistics_service():

    with patch(
        "services.firebird.health_service.StatisticsService"
    ) as statistics_cls:

        service = HealthService()

    statistics_cls.assert_called_once_with()

    assert service.statistics_service is (
        statistics_cls.return_value
    )


# ==========================================================
# CHECK — PROVIDED STATISTICS
# ==========================================================


def test_check_uses_provided_statistics():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    assert isinstance(
        result,
        DatabaseHealth,
    )

    service.statistics_service.statistics.assert_not_called()


# ==========================================================
# CHECK — LOADS STATISTICS AUTOMATICALLY
# ==========================================================


def test_check_loads_statistics_when_not_provided():

    service = create_service()

    stats = create_stats()

    service.statistics_service.statistics.return_value = (
        stats
    )

    result = service.check()

    assert isinstance(
        result,
        DatabaseHealth,
    )

    service.statistics_service.statistics.assert_called_once_with()


# ==========================================================
# STATISTICS ERROR
# ==========================================================


def test_check_returns_error_when_statistics_fail():

    service = create_service()

    service.statistics_service.statistics.side_effect = (
        RuntimeError(
            "GSTAT ERROR"
        )
    )

    result = service.check()

    assert result.status == "ERROR"

    assert result.summary == (
        "Nie udało się pobrać "
        "statystyk bazy."
    )

    assert len(result.checks) == 1

    check = result.checks[0]

    assert isinstance(
        check,
        HealthCheck,
    )

    assert check.name == "Połączenie"
    assert check.status == "ERROR"
    assert check.value == "-"
    assert check.message == "GSTAT ERROR"


# ==========================================================
# ODS
# ==========================================================


def test_ods_valid():

    service = create_service()

    stats = create_stats(
        ods="13.0"
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "ODS"
    )

    assert check.status == "OK"
    assert check.value == "13.0"
    assert check.message == (
        "ODS odczytany poprawnie."
    )


def test_ods_missing():

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
    assert check.message == (
        "Brak informacji o ODS."
    )


def test_ods_none_is_treated_as_missing():

    service = create_service()

    stats = create_stats(
        ods=None
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "ODS"
    )

    assert check.status == "WARNING"
    assert check.value == "-"
    assert check.message == (
        "Brak informacji o ODS."
    )


# ==========================================================
# PAGE SIZE
# ==========================================================


def test_page_size_valid():

    service = create_service()

    valid_sizes = (
        1024,
        2048,
        4096,
        8192,
        16384,
        32768,
    )

    for page_size in valid_sizes:

        stats = create_stats(
            page_size=page_size
        )

        result = service.check(stats)

        check = next(
            check
            for check in result.checks
            if check.name == "Page Size"
        )

        assert check.status == "OK"
        assert check.value == str(
            page_size
        )
        assert check.message == (
            "Prawidłowy rozmiar strony."
        )


def test_page_size_invalid():

    service = create_service()

    stats = create_stats(
        page_size=9999
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Page Size"
    )

    assert check.status == "WARNING"
    assert check.value == "9999"
    assert check.message == (
        "Nietypowy rozmiar strony."
    )


def test_page_size_zero_is_warning():

    service = create_service()

    stats = create_stats(
        page_size=0
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Page Size"
    )

    assert check.status == "WARNING"
    assert check.value == "0"


# ==========================================================
# SWEEP
# ==========================================================


def test_sweep_enabled():

    service = create_service()

    stats = create_stats(
        sweep_interval=20000
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "OK"
    assert check.value == "20000"
    assert check.message == (
        "Sweep jest skonfigurowany."
    )


def test_sweep_disabled():

    service = create_service()

    stats = create_stats(
        sweep_interval=0
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "WARNING"
    assert check.value == "0"
    assert check.message == (
        "Sweep jest wyłączony."
    )


def test_sweep_negative_value():

    service = create_service()

    stats = create_stats(
        sweep_interval=-1
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Sweep Interval"
    )

    assert check.status == "WARNING"


# ==========================================================
# TRANSACTIONS
# ==========================================================


def test_transactions_normal():

    service = create_service()

    stats = create_stats(
        oldest_transaction=100,
        oldest_active=150,
        next_transaction=200,
    )

    result = service.check(stats)

    transaction_check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert transaction_check.status == "OK"
    assert transaction_check.value == "100"
    assert transaction_check.message == (
        "Transakcje wyglądają prawidłowo."
    )

    active_check = next(
        check
        for check in result.checks
        if check.name == "Oldest Active"
    )

    assert active_check.status == "OK"
    assert active_check.value == "150"
    assert active_check.message == (
        "Aktywna transakcja mieści się w zakresie."
    )


def test_transactions_large_difference():

    service = create_service()

    stats = create_stats(
        oldest_transaction=100,
        oldest_active=150,
        next_transaction=1_000_100,
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "WARNING"
    assert check.value == "1000000"
    assert check.message == (
        "Duża różnica pomiędzy "
        "Next Transaction i Oldest Transaction."
    )


def test_transactions_below_warning_threshold():

    service = create_service()

    stats = create_stats(
        oldest_transaction=100,
        oldest_active=150,
        next_transaction=1_000_099,
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "OK"
    assert check.value == "999999"


def test_transactions_missing():

    service = create_service()

    stats = create_stats(
        next_transaction=0
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "WARNING"
    assert check.value == "-"
    assert check.message == (
        "Brak poprawnych danych transakcyjnych."
    )

    assert not any(
        check.name == "Oldest Active"
        for check in result.checks
    )


def test_transactions_negative_next_transaction():

    service = create_service()

    stats = create_stats(
        next_transaction=-1
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Transakcje"
    )

    assert check.status == "WARNING"
    assert check.value == "-"


def test_oldest_active_warning():

    service = create_service()

    stats = create_stats(
        oldest_transaction=100,
        oldest_active=50,
        next_transaction=200,
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Oldest Active"
    )

    assert check.status == "WARNING"
    assert check.value == "50"
    assert check.message == (
        "Oldest Active wymaga sprawdzenia."
    )


def test_oldest_active_equal_to_oldest_is_warning():

    service = create_service()

    stats = create_stats(
        oldest_transaction=100,
        oldest_active=100,
        next_transaction=200,
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Oldest Active"
    )

    assert check.status == "WARNING"


# ==========================================================
# FORCE WRITE
# ==========================================================


def test_force_write_enabled():

    service = create_service()

    stats = create_stats(
        forced_writes=True
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Force Write"
    )

    assert check.status == "OK"
    assert check.value == "ON"
    assert check.message == (
        "Forced Writes jest włączone."
    )


def test_force_write_disabled():

    service = create_service()

    stats = create_stats(
        forced_writes=False
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "Force Write"
    )

    assert check.status == "WARNING"
    assert check.value == "OFF"
    assert check.message == (
        "Forced Writes jest wyłączone."
    )


# ==========================================================
# NO RESERVE
# ==========================================================


def test_no_reserve_enabled():

    service = create_service()

    stats = create_stats(
        no_reserve=True
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "No Reserve"
    )

    assert check.status == "OK"
    assert check.value == "ON"
    assert check.message == (
        "NO RESERVE jest ustawione."
    )


def test_no_reserve_disabled():

    service = create_service()

    stats = create_stats(
        no_reserve=False
    )

    result = service.check(stats)

    check = next(
        check
        for check in result.checks
        if check.name == "No Reserve"
    )

    assert check.status == "WARNING"
    assert check.value == "OFF"
    assert check.message == (
        "NO RESERVE nie jest ustawione."
    )


# ==========================================================
# FINAL STATUS
# ==========================================================


def test_final_status_ok():

    service = create_service()

    stats = create_stats(
        ods="13.0",
        page_size=4096,
        sweep_interval=20000,
        oldest_transaction=100,
        oldest_active=150,
        next_transaction=200,
        forced_writes=True,
        no_reserve=True,
    )

    result = service.check(stats)

    assert result.status == "OK"

    assert result.summary == (
        "Baza wygląda prawidłowo."
    )


def test_final_status_warning():

    service = create_service()

    stats = create_stats(
        page_size=12345,
        sweep_interval=0,
        forced_writes=False,
        no_reserve=False,
    )

    result = service.check(stats)

    assert result.status == "WARNING"

    assert result.summary.startswith(
        "Wykryto "
    )

    assert result.summary.endswith(
        " ostrzeżeń."
    )


def test_final_status_error():

    service = create_service()

    health = DatabaseHealth()

    health.checks.append(
        HealthCheck(
            name="TEST",
            status="ERROR",
            value="-",
            message="ERROR",
        )
    )

    service._calculate_status(health)

    assert health.status == "ERROR"
    assert health.summary == (
        "Wykryto 1 problemów."
    )


# ==========================================================
# CHECK COUNT
# ==========================================================


def test_check_produces_expected_number_of_checks():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    # ODS
    # Page Size
    # Sweep Interval
    # Transakcje
    # Oldest Active
    # Force Write
    # No Reserve

    assert len(result.checks) == 7


# ==========================================================
# CHECK OBJECTS
# ==========================================================


def test_all_checks_are_health_checks():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    assert all(
        isinstance(
            check,
            HealthCheck,
        )
        for check in result.checks
    )


# ==========================================================
# CHECK NAMES
# ==========================================================


def test_check_contains_expected_names():

    service = create_service()

    stats = create_stats()

    result = service.check(stats)

    names = [
        check.name
        for check in result.checks
    ]

    assert names == [
        "ODS",
        "Page Size",
        "Sweep Interval",
        "Transakcje",
        "Oldest Active",
        "Force Write",
        "No Reserve",
    ]