from __future__ import annotations

from dataclasses import dataclass

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
)
from services.firebird.workflow_service import (
    WorkflowService,
)


# ==========================================================
# MOCK STATISTICS
# ==========================================================


@dataclass
class FakeStatistics:
    pass


# ==========================================================
# MOCK SERVICES
# ==========================================================


class FakeStatisticsService:
    def __init__(
        self,
        fail: bool = False,
    ):
        self.fail = fail
        self.calls = 0

    def statistics(self):

        self.calls += 1

        if self.fail:
            raise RuntimeError(
                "Błąd statystyk"
            )

        return FakeStatistics()


class FakeDiagnosticsService:
    def __init__(
        self,
        fail: bool = False,
    ):
        self.fail = fail
        self.calls = 0

    def analyze(
        self,
        stats,
    ):

        self.calls += 1

        if self.fail:
            raise RuntimeError(
                "Błąd diagnostyki"
            )

        return DiagnosticResult(
            status="success",
            message="Baza działa prawidłowo.",
            transaction_gap=0,
            active_gap=0,
            snapshot_gap=0,
            no_reserve_warning=False,
        )


class FakeRecommendationService:
    def __init__(
        self,
        fail: bool = False,
    ):
        self.fail = fail
        self.calls = 0

    def recommend(
        self,
        diagnostic,
    ):

        self.calls += 1

        if self.fail:
            raise RuntimeError(
                "Błąd rekomendacji"
            )

        return RecommendationResult(
            recommendations=[
                "Brak dodatkowych rekomendacji."
            ]
        )


class FakeBackupService:
    def __init__(
        self,
        success: bool = True,
    ):
        self.success = success
        self.calls = 0

    def backup(
        self,
        destination,
    ):

        self.calls += 1

        if self.success:

            return (
                True,
                "Backup wykonany pomyślnie.",
            )

        return (
            False,
            "Backup nie powiódł się.",
        )


# ==========================================================
# TEST 1 — PEŁNY SUKCES
# ==========================================================


def test_workflow_success():

    statistics_service = (
        FakeStatisticsService()
    )

    diagnostics_service = (
        FakeDiagnosticsService()
    )

    recommendation_service = (
        FakeRecommendationService()
    )

    backup_service = (
        FakeBackupService(
            success=True
        )
    )

    workflow = WorkflowService(
        statistics_service=statistics_service,
        diagnostics_service=diagnostics_service,
        recommendation_service=recommendation_service,
        backup_service=backup_service,
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True
    assert result.error == ""

    assert (
        result.initial_diagnostic
        is not None
    )

    assert (
        result.final_diagnostic
        is not None
    )

    assert (
        result.recommendations
        is not None
    )

    assert (
        result.backup_file
        == "C:/backup/test.fbk"
    )

    assert len(result.steps) == 4

    assert all(
        step.status == "SUCCESS"
        for step in result.steps
    )

    assert (
        statistics_service.calls
        == 2
    )

    assert (
        diagnostics_service.calls
        == 2
    )

    assert (
        recommendation_service.calls
        == 1
    )

    assert (
        backup_service.calls
        == 1
    )


# ==========================================================
# TEST 2 — BŁĄD DIAGNOSTYKI POCZĄTKOWEJ
# ==========================================================


def test_workflow_initial_diagnostics_error():

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(
            fail=True
        ),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert (
        "Błąd diagnostyki początkowej"
        in result.error
    )

    assert result.initial_diagnostic is None
    assert result.final_diagnostic is None
    assert result.recommendations is None

    assert len(result.steps) == 1

    assert (
        result.steps[0].name
        == "Diagnostyka początkowa"
    )

    assert (
        result.steps[0].status
        == "ERROR"
    )


# ==========================================================
# TEST 3 — BŁĄD BACKUPU
# ==========================================================


def test_workflow_backup_error():

    statistics_service = (
        FakeStatisticsService()
    )

    diagnostics_service = (
        FakeDiagnosticsService()
    )

    backup_service = (
        FakeBackupService(
            success=False
        )
    )

    workflow = WorkflowService(
        statistics_service=statistics_service,
        diagnostics_service=diagnostics_service,
        recommendation_service=FakeRecommendationService(),
        backup_service=backup_service,
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert (
        result.error
        == "Backup nie powiódł się."
    )

    assert (
        result.initial_diagnostic
        is not None
    )

    assert result.final_diagnostic is None
    assert result.recommendations is None

    assert len(result.steps) == 2

    assert (
        result.steps[0].status
        == "SUCCESS"
    )

    assert (
        result.steps[1].name
        == "Backup"
    )

    assert (
        result.steps[1].status
        == "ERROR"
    )


# ==========================================================
# TEST 4 — BŁĄD PONOWNEJ DIAGNOSTYKI
# ==========================================================


def test_workflow_final_diagnostics_error():

    statistics_service = (
        FakeStatisticsService()
    )

    class DiagnosticsFailOnSecondCall:

        def __init__(self):
            self.calls = 0

        def analyze(
            self,
            stats,
        ):

            self.calls += 1

            if self.calls == 2:
                raise RuntimeError(
                    "Błąd drugiej diagnostyki"
                )

            return DiagnosticResult(
                status="success",
                message="OK",
                transaction_gap=0,
                active_gap=0,
                snapshot_gap=0,
                no_reserve_warning=False,
            )

    diagnostics_service = (
        DiagnosticsFailOnSecondCall()
    )

    workflow = WorkflowService(
        statistics_service=statistics_service,
        diagnostics_service=diagnostics_service,
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert (
        "Błąd ponownej diagnostyki"
        in result.error
    )

    assert (
        result.initial_diagnostic
        is not None
    )

    assert result.final_diagnostic is None
    assert result.recommendations is None

    assert len(result.steps) == 3

    assert (
        result.steps[2].name
        == "Ponowna diagnostyka"
    )

    assert (
        result.steps[2].status
        == "ERROR"
    )


# ==========================================================
# TEST 5 — BŁĄD REKOMENDACJI
# ==========================================================


def test_workflow_recommendation_error():

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(
            fail=True
        ),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert (
        "Błąd generowania rekomendacji"
        in result.error
    )

    assert (
        result.initial_diagnostic
        is not None
    )

    assert (
        result.final_diagnostic
        is not None
    )

    assert result.recommendations is None

    assert len(result.steps) == 4

    assert (
        result.steps[3].name
        == "Rekomendacje"
    )

    assert (
        result.steps[3].status
        == "ERROR"
    )


# ==========================================================
# TEST 6 — WYNIK ZAWIERA REKOMENDACJE
# ==========================================================


def test_workflow_has_recommendations():

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True

    assert result.has_recommendations is True

    assert (
        result.recommendations
        is not None
    )

    assert (
        len(
            result.recommendations.recommendations
        )
        > 0
    )


# ==========================================================
# TEST 7 — BRAK BŁĘDU
# ==========================================================


def test_workflow_has_no_error_after_success():

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True
    assert result.has_error is False
    assert result.error == ""
    # ==========================================================
# TEST 8 — WŁAŚCIWA KOLEJNOŚĆ OPERACJI
# ==========================================================


def test_workflow_execution_order():

    calls = []

    class OrderedStatisticsService:

        def statistics(self):

            calls.append("statistics")

            return FakeStatistics()


    class OrderedDiagnosticsService:

        def analyze(self, stats):

            calls.append("diagnostics")

            return DiagnosticResult(
                status="success",
                message="OK",
                transaction_gap=0,
                active_gap=0,
                snapshot_gap=0,
                no_reserve_warning=False,
            )


    class OrderedBackupService:

        def backup(self, destination):

            calls.append("backup")

            return (
                True,
                "Backup OK",
            )


    class OrderedRecommendationService:

        def recommend(self, diagnostic):

            calls.append("recommendations")

            return RecommendationResult(
                recommendations=[
                    "Brak dodatkowych rekomendacji."
                ]
            )


    workflow = WorkflowService(
        statistics_service=OrderedStatisticsService(),
        diagnostics_service=OrderedDiagnosticsService(),
        recommendation_service=OrderedRecommendationService(),
        backup_service=OrderedBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True

    assert calls == [
        "statistics",
        "diagnostics",
        "backup",
        "statistics",
        "diagnostics",
        "recommendations",
    ]


# ==========================================================
# TEST 9 — BACKUP NIE MOŻE WYKONAĆ PONOWNEJ DIAGNOSTYKI
# ==========================================================


def test_workflow_stops_after_backup_failure():

    statistics_service = FakeStatisticsService()

    backup_service = FakeBackupService(
        success=False
    )

    workflow = WorkflowService(
        statistics_service=statistics_service,
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=backup_service,
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert statistics_service.calls == 1

    assert backup_service.calls == 1

    assert result.final_diagnostic is None

    assert result.recommendations is None


# ==========================================================
# TEST 10 — BRAK REKOMENDACJI NIE JEST BŁĘDEM WORKFLOW
# ==========================================================


def test_workflow_empty_recommendations_are_success():

    class EmptyRecommendationService:

        def recommend(self, diagnostic):

            return RecommendationResult(
                recommendations=[]
            )

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=EmptyRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True
    assert result.error == ""

    assert result.recommendations is not None

    assert (
        result.recommendations.recommendations
        == []
    )

    assert result.has_recommendations is False


# ==========================================================
# TEST 11 — HAS_ERROR
# ==========================================================


def test_workflow_has_error_when_failed():

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(
            fail=True
        ),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False
    assert result.has_error is True
    assert result.error != ""


# ==========================================================
# TEST 12 — BACKUP ZAPISUJE ŚCIEŻKĘ
# ==========================================================


def test_workflow_stores_backup_path():

    backup_path = (
        "C:/KSBAZA/KS-APW/WAPTEKA_TEST.fbk"
    )

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=FakeRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        backup_path
    )

    assert result.success is True

    assert (
        result.backup_file
        == backup_path
    )


# ==========================================================
# TEST 13 — DIAGNOSTYKA JEST PRZEKAZYWANA DO REKOMENDACJI
# ==========================================================


def test_workflow_passes_final_diagnostic_to_recommendations():

    captured = {}

    class CapturingRecommendationService:

        def recommend(self, diagnostic):

            captured["diagnostic"] = diagnostic

            return RecommendationResult(
                recommendations=[
                    "OK"
                ]
            )

    workflow = WorkflowService(
        statistics_service=FakeStatisticsService(),
        diagnostics_service=FakeDiagnosticsService(),
        recommendation_service=CapturingRecommendationService(),
        backup_service=FakeBackupService(),
    )

    result = workflow.run(
        "C:/backup/test.fbk"
    )

    assert result.success is True

    assert (
        captured["diagnostic"]
        is result.final_diagnostic
    )