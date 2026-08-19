from __future__ import annotations

from dataclasses import dataclass

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)


@dataclass(slots=True)
class RecommendationResult:
    """
    Wynik rekomendacji dla bazy Firebird.
    """

    recommendations: list[str]

    @property
    def has_recommendations(self) -> bool:
        return bool(self.recommendations)


class RecommendationService:

    def recommend(
        self,
        diagnostic: DiagnosticResult,
    ) -> RecommendationResult:

        recommendations: list[str] = []

        # ==================================================
        # TRANSAKCJE
        # ==================================================

        if diagnostic.transaction_gap >= 1_000_000:

            recommendations.append(
                "Zalecane wykonanie diagnostyki transakcji "
                "oraz sprawdzenie możliwości wykonania Sweep."
            )

        elif diagnostic.transaction_gap >= 100_000:

            recommendations.append(
                "Zalecane wykonanie Sweep bazy danych."
            )

        # ==================================================
        # AKTYWNE TRANSAKCJE
        # ==================================================

        if diagnostic.active_gap >= 100_000:

            recommendations.append(
                "Zalecane sprawdzenie długo trwających "
                "aktywnych transakcji."
            )

        # ==================================================
        # SNAPSHOT
        # ==================================================

        if diagnostic.snapshot_gap >= 100_000:

            recommendations.append(
                "Zalecane sprawdzenie długotrwałych "
                "snapshotów transakcyjnych."
            )

        # ==================================================
        # ERROR
        # ==================================================

        if diagnostic.status == "error":

            recommendations.append(
                "Baza wymaga szczegółowej diagnostyki "
                "przed wykonaniem operacji naprawczych."
            )

        # ==================================================
        # NO RESERVE
        # ==================================================

        if diagnostic.no_reserve_warning:

            recommendations.append(
                "No Reserve jest włączone. "
                "Jest to informacja konfiguracyjna "
                "i nie oznacza uszkodzenia bazy."
            )

        # ==================================================
        # BRAK PROBLEMÓW
        # ==================================================

        if not recommendations:

            recommendations.append(
                "Brak dodatkowych rekomendacji. "
                "Baza działa prawidłowo."
            )

        return RecommendationResult(
            recommendations=recommendations
        )