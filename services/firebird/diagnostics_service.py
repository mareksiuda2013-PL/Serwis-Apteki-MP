from __future__ import annotations

from dataclasses import dataclass

from models import DatabaseStatistics
from models.database_health import (
    DatabaseHealth,
    HealthCheck,
)


@dataclass(slots=True)
class DiagnosticResult:
    """
    Wynik automatycznej diagnostyki bazy Firebird.
    """

    status: str = "success"
    message: str = "Baza działa prawidłowo."

    transaction_gap: int = 0
    active_gap: int = 0
    snapshot_gap: int = 0

    no_reserve_warning: bool = False


class DiagnosticsService:

    def analyze(
        self,
        stats: DatabaseStatistics,
    ) -> DiagnosticResult:
        """
        Analizuje statystyki Firebird.
        """

        result = DiagnosticResult()

        # ==================================================
        # TRANSAKCJE
        # ==================================================

        result.transaction_gap = (
            stats.next_transaction
            - stats.oldest_transaction
        )

        result.active_gap = (
            stats.oldest_active
            - stats.oldest_transaction
        )

        result.snapshot_gap = (
            stats.oldest_snapshot
            - stats.oldest_transaction
        )

        # ==================================================
        # NO RESERVE
        # ==================================================

        result.no_reserve_warning = (
            stats.no_reserve
        )

        warnings: list[str] = []
        information: list[str] = []

        # ==================================================
        # TRANSACTION GAP
        # ==================================================

        if result.transaction_gap >= 1_000_000:

            result.status = "error"

            warnings.append(
                "Bardzo duży dystans transakcji."
            )

        elif result.transaction_gap >= 100_000:

            result.status = "warning"

            warnings.append(
                "Duży dystans transakcji."
            )

        # ==================================================
        # ACTIVE GAP
        # ==================================================

        if result.active_gap >= 100_000:

            if result.status != "error":
                result.status = "warning"

            warnings.append(
                "Duży dystans aktywnej transakcji."
            )

        # ==================================================
        # SNAPSHOT GAP
        # ==================================================

        if result.snapshot_gap >= 100_000:

            if result.status != "error":
                result.status = "warning"

            warnings.append(
                "Duży dystans snapshot."
            )

        # ==================================================
        # NO RESERVE
        # ==================================================

        if result.no_reserve_warning:

            information.append(
                "Informacja: No Reserve jest włączone."
            )

        # ==================================================
        # KOMUNIKAT
        # ==================================================

        if warnings:

            result.message = " ".join(
                warnings
            )

            if information:

                result.message += " " + " ".join(
                    information
                )

        elif information:

            result.status = "success"

            result.message = (
                "Baza działa prawidłowo. "
                + " ".join(information)
            )

        else:

            result.status = "success"

            result.message = (
                "Baza działa prawidłowo."
            )

        return result

    # ======================================================
    # HEALTH
    # ======================================================

    def health(
        self,
        stats: DatabaseStatistics,
    ) -> DatabaseHealth:
        """
        Buduje wynik Health Check na podstawie
        aktualnych statystyk Firebird.
        """

        health = DatabaseHealth()

        # ==================================================
        # TRANSAKCJE
        # ==================================================

        transaction_gap = (
            stats.next_transaction
            - stats.oldest_transaction
        )

        if transaction_gap >= 1_000_000:

            health.checks.append(
                HealthCheck(
                    name="Transakcje",
                    status="ERROR",
                    value=str(transaction_gap),
                    message=(
                        "Bardzo duży dystans "
                        "pomiędzy transakcjami."
                    ),
                )
            )

        elif transaction_gap >= 100_000:

            health.checks.append(
                HealthCheck(
                    name="Transakcje",
                    status="WARNING",
                    value=str(transaction_gap),
                    message=(
                        "Duży dystans pomiędzy "
                        "transakcjami."
                    ),
                )
            )

        else:

            health.checks.append(
                HealthCheck(
                    name="Transakcje",
                    status="OK",
                    value=str(transaction_gap),
                    message=(
                        "Dystans transakcji "
                        "wygląda prawidłowo."
                    ),
                )
            )

        # ==================================================
        # FORCE WRITE
        # ==================================================

        health.checks.append(
            HealthCheck(
                name="Force Write",
                status="OK"
                if stats.forced_writes
                else "WARNING",
                value="ON"
                if stats.forced_writes
                else "OFF",
                message=(
                    "Forced Writes jest włączone."
                    if stats.forced_writes
                    else
                    "Forced Writes jest wyłączone."
                ),
            )
        )

        # ==================================================
        # NO RESERVE
        # ==================================================

        health.checks.append(
            HealthCheck(
                name="No Reserve",
                status="OK"
                if stats.no_reserve
                else "WARNING",
                value="ON"
                if stats.no_reserve
                else "OFF",
                message=(
                    "NO RESERVE jest ustawione."
                    if stats.no_reserve
                    else
                    "NO RESERVE nie jest ustawione."
                ),
            )
        )

        # ==================================================
        # STATUS KOŃCOWY
        # ==================================================

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

        if errors:

            health.status = "ERROR"

            health.summary = (
                f"Wykryto {errors} problemów."
            )

        elif warnings:

            health.status = "WARNING"

            health.summary = (
                f"Wykryto {warnings} ostrzeżeń."
            )

        else:

            health.status = "OK"

            health.summary = (
                "Baza wygląda prawidłowo."
            )

        return health