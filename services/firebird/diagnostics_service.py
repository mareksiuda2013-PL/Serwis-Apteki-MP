from __future__ import annotations

from dataclasses import dataclass

from models import DatabaseStatistics


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
        Analizuje statystyki Firebird i określa stan bazy.

        Poziomy diagnostyki:

            success
                Baza działa prawidłowo.

            warning
                Wykryto parametr wymagający uwagi.

            error
                Wykryto poważny problem wymagający reakcji.

        NO RESERVE jest traktowane jako informacja
        konfiguracyjna, a nie jako błąd bazy.
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

        # ==================================================
        # OCENA
        # ==================================================

        warnings: list[str] = []
        information: list[str] = []

        # --------------------------------------------------
        # WIEK TRANSAKCJI
        # --------------------------------------------------

        if result.transaction_gap >= 1_000_000:

            result.status = "error"

            warnings.append(
                "Bardzo duży dystans transakcji."
            )

        elif result.transaction_gap >= 100_000:

            if result.status != "error":
                result.status = "warning"

            warnings.append(
                "Duży dystans transakcji."
            )

        # --------------------------------------------------
        # AKTYWNE TRANSAKCJE
        # --------------------------------------------------

        if result.active_gap >= 100_000:

            if result.status != "error":
                result.status = "warning"

            warnings.append(
                "Duży dystans aktywnej transakcji."
            )

        # --------------------------------------------------
        # SNAPSHOT
        # --------------------------------------------------

        if result.snapshot_gap >= 100_000:

            if result.status != "error":
                result.status = "warning"

            warnings.append(
                "Duży dystans snapshot."
            )

        # --------------------------------------------------
        # NO RESERVE
        # --------------------------------------------------

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