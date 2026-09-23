from __future__ import annotations

from models.database_health import (
    DatabaseHealth,
    HealthCheck,
)

from .statistics_service import StatisticsService


class HealthService:

    def __init__(self):

        self.statistics_service = StatisticsService()

    # ==================================================
    # PUBLIC
    # ==================================================

    def check(
        self,
        stats=None,
    ) -> DatabaseHealth:

        health = DatabaseHealth()

        try:

            if stats is None:
                stats = (
                    self.statistics_service.statistics()
                )

        except Exception as exc:

            health.status = "ERROR"

            health.summary = (
                "Nie udało się pobrać "
                "statystyk bazy."
            )

            health.checks.append(
                HealthCheck(
                    name="Połączenie",
                    status="ERROR",
                    value="-",
                    message=str(exc),
                )
            )

            return health

        # ==================================================
        # ODS
        # ==================================================

        self._check_ods(
            health,
            stats.ods,
        )

        # ==================================================
        # PAGE SIZE
        # ==================================================

        self._check_page_size(
            health,
            stats.page_size,
        )

        # ==================================================
        # SWEEP
        # ==================================================

        self._check_sweep(
            health,
            stats.sweep_interval,
        )

        # ==================================================
        # TRANSAKCJE
        # ==================================================

        self._check_transactions(
            health,
            stats.oldest_transaction,
            stats.oldest_active,
            stats.next_transaction,
        )

        # ==================================================
        # FORCE WRITE
        # ==================================================

        self._check_force_write(
            health,
            stats.forced_writes,
        )

        # ==================================================
        # NO RESERVE
        # ==================================================

        self._check_no_reserve(
            health,
            stats.no_reserve,
        )

        # ==================================================
        # STATUS KOŃCOWY
        # ==================================================

        self._calculate_status(
            health
        )

        return health

    # ==================================================
    # ODS
    # ==================================================

    def _check_ods(
        self,
        health: DatabaseHealth,
        ods: str,
    ) -> None:

        if not ods:

            health.checks.append(
                HealthCheck(
                    name="ODS",
                    status="WARNING",
                    value="-",
                    message="Brak informacji o ODS.",
                )
            )

            return

        health.checks.append(
            HealthCheck(
                name="ODS",
                status="OK",
                value=ods,
                message="ODS odczytany poprawnie.",
            )
        )

    # ==================================================
    # PAGE SIZE
    # ==================================================

    def _check_page_size(
        self,
        health: DatabaseHealth,
        page_size: int,
    ) -> None:

        valid_sizes = {
            1024,
            2048,
            4096,
            8192,
            16384,
            32768,
        }

        if page_size in valid_sizes:

            health.checks.append(
                HealthCheck(
                    name="Page Size",
                    status="OK",
                    value=str(page_size),
                    message="Prawidłowy rozmiar strony.",
                )
            )

        else:

            health.checks.append(
                HealthCheck(
                    name="Page Size",
                    status="WARNING",
                    value=str(page_size),
                    message="Nietypowy rozmiar strony.",
                )
            )

    # ==================================================
    # SWEEP
    # ==================================================

    def _check_sweep(
        self,
        health: DatabaseHealth,
        sweep_interval: int,
    ) -> None:

        if sweep_interval <= 0:

            health.checks.append(
                HealthCheck(
                    name="Sweep Interval",
                    status="WARNING",
                    value=str(sweep_interval),
                    message="Sweep jest wyłączony.",
                )
            )

            return

        health.checks.append(
            HealthCheck(
                name="Sweep Interval",
                status="OK",
                value=str(sweep_interval),
                message="Sweep jest skonfigurowany.",
            )
        )

    # ==================================================
    # TRANSACTIONS
    # ==================================================

    def _check_transactions(
        self,
        health: DatabaseHealth,
        oldest: int,
        oldest_active: int,
        next_transaction: int,
    ) -> None:

        if next_transaction <= 0:

            health.checks.append(
                HealthCheck(
                    name="Transakcje",
                    status="WARNING",
                    value="-",
                    message="Brak poprawnych danych transakcyjnych.",
                )
            )

            return

        difference = (
            next_transaction - oldest
        )

        # --------------------------------------------------
        # Orientacyjne poziomy ostrzegawcze.
        # Nie są to wartości uszkodzenia bazy.
        # --------------------------------------------------

        if difference >= 1_000_000:

            status = "WARNING"

            message = (
                "Duża różnica pomiędzy "
                "Next Transaction i Oldest Transaction."
            )

        else:

            status = "OK"

            message = (
                "Transakcje wyglądają prawidłowo."
            )

        health.checks.append(
            HealthCheck(
                name="Transakcje",
                status=status,
                value=str(difference),
                message=message,
            )
        )

        # --------------------------------------------------
        # Oldest Active
        # --------------------------------------------------

        if oldest_active > oldest:

            health.checks.append(
                HealthCheck(
                    name="Oldest Active",
                    status="OK",
                    value=str(oldest_active),
                    message="Aktywna transakcja mieści się w zakresie.",
                )
            )

        else:

            health.checks.append(
                HealthCheck(
                    name="Oldest Active",
                    status="WARNING",
                    value=str(oldest_active),
                    message="Oldest Active wymaga sprawdzenia.",
                )
            )

    # ==================================================
    # FORCE WRITE
    # ==================================================

    def _check_force_write(
        self,
        health: DatabaseHealth,
        forced_writes: bool,
    ) -> None:

        health.checks.append(
            HealthCheck(
                name="Force Write",
                status="OK"
                if forced_writes
                else "WARNING",
                value="ON"
                if forced_writes
                else "OFF",
                message=(
                    "Forced Writes jest włączone."
                    if forced_writes
                    else
                    "Forced Writes jest wyłączone."
                ),
            )
        )

    # ==================================================
    # NO RESERVE
    # ==================================================

    def _check_no_reserve(
        self,
        health: DatabaseHealth,
        no_reserve: bool,
    ) -> None:

        health.checks.append(
            HealthCheck(
                name="No Reserve",
                status="OK"
                if no_reserve
                else "WARNING",
                value="ON"
                if no_reserve
                else "OFF",
                message=(
                    "NO RESERVE jest ustawione."
                    if no_reserve
                    else
                    "NO RESERVE nie jest ustawione."
                ),
            )
        )

    # ==================================================
    # FINAL STATUS
    # ==================================================

    def _calculate_status(
        self,
        health: DatabaseHealth,
    ) -> None:

        errors = sum(
            1
            for check in health.checks
            if check.status == "ERROR"
        )

        warnings = sum(
            1
            for check in health.checks
            if check.status == "WARNING"
        )

        if errors > 0:

            health.status = "ERROR"

            health.summary = (
                f"Wykryto {errors} problemów."
            )

            return

        if warnings > 0:

            health.status = "WARNING"

            health.summary = (
                f"Wykryto {warnings} ostrzeżeń."
            )

            return

        health.status = "OK"

        health.summary = (
            "Baza wygląda prawidłowo."
        )