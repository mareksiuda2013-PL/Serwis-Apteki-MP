from __future__ import annotations

from models import DatabaseStatistics
from models.database_health import DatabaseHealth
from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
)
from services.firebird.report_service import (
    ReportService,
)
from services.firebird.workflow_service import (
    WorkflowResult,
    WorkflowStep,
)


# ==========================================================
# POMOCNICZE
# ==========================================================


def create_success_workflow() -> WorkflowResult:

    diagnostic = DiagnosticResult(
        status="success",
        message="Baza działa prawidłowo.",
        transaction_gap=100,
        active_gap=10,
        snapshot_gap=20,
        no_reserve_warning=False,
    )

    return WorkflowResult(
        success=True,
        initial_diagnostic=diagnostic,
        final_diagnostic=diagnostic,
        recommendations=RecommendationResult(
            recommendations=[
                "Brak dodatkowych rekomendacji."
            ]
        ),
        steps=[
            WorkflowStep(
                name="Diagnostyka początkowa",
                status="SUCCESS",
                message="Baza działa prawidłowo.",
            ),
            WorkflowStep(
                name="Backup",
                status="SUCCESS",
                message="Backup wykonany pomyślnie.",
            ),
            WorkflowStep(
                name="Ponowna diagnostyka",
                status="SUCCESS",
                message="Baza działa prawidłowo.",
            ),
            WorkflowStep(
                name="Rekomendacje",
                status="SUCCESS",
                message="Rekomendacje zostały wygenerowane.",
            ),
        ],
        backup_file="C:/backup/test.fbk",
    )


# ==========================================================
# TEST 1
# ==========================================================


def test_generate_workflow_report_success():

    service = ReportService()

    workflow = create_success_workflow()

    report = service.generate_workflow_report(
        database="C:/database/test.fdb",
        workflow=workflow,
    )

    assert report.database == (
        "C:/database/test.fdb"
    )

    assert report.status == "OK"

    assert (
        "Workflow zakończony"
        in report.summary
    )

    assert len(report.items) > 0


# ==========================================================
# TEST 2
# ==========================================================


def test_generate_workflow_report_contains_steps():

    service = ReportService()

    workflow = create_success_workflow()

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    workflow_items = [
        item
        for item in report.items
        if item.section == "Workflow"
    ]

    assert len(workflow_items) == 4

    names = [
        item.name
        for item in workflow_items
    ]

    assert (
        "Diagnostyka początkowa"
        in names
    )

    assert "Backup" in names

    assert (
        "Ponowna diagnostyka"
        in names
    )

    assert (
        "Rekomendacje"
        in names
    )


# ==========================================================
# TEST 3
# ==========================================================


def test_generate_workflow_report_contains_backup():

    service = ReportService()

    workflow = create_success_workflow()

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    backup_items = [
        item
        for item in report.items
        if item.section == "Backup"
    ]

    assert len(backup_items) == 1

    assert (
        backup_items[0].name
        == "Plik backupu"
    )

    assert (
        backup_items[0].value
        == "C:/backup/test.fbk"
    )


# ==========================================================
# TEST 4
# ==========================================================


def test_generate_workflow_report_contains_recommendations():

    service = ReportService()

    workflow = create_success_workflow()

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert (
        "Brak dodatkowych rekomendacji."
        in report.recommendations
    )


# ==========================================================
# TEST 5
# ==========================================================


def test_generate_workflow_report_error():

    service = ReportService()

    workflow = WorkflowResult(
        success=False,
        steps=[
            WorkflowStep(
                name="Diagnostyka początkowa",
                status="SUCCESS",
                message="OK",
            ),
            WorkflowStep(
                name="Backup",
                status="ERROR",
                message="Backup nie powiódł się.",
            ),
        ],
        error="Backup nie powiódł się.",
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "ERROR"

    assert (
        "Backup nie powiódł się."
        in report.summary
    )

    error_items = [
        item
        for item in report.items
        if item.status == "ERROR"
    ]

    assert len(error_items) >= 1

    assert any(
        item.name == "Błąd"
        for item in error_items
    )


# ==========================================================
# TEST 6
# ==========================================================


def test_generate_workflow_report_warning():

    service = ReportService()

    diagnostic = DiagnosticResult(
        status="warning",
        message="Duży dystans transakcji.",
        transaction_gap=100_000,
        active_gap=0,
        snapshot_gap=0,
        no_reserve_warning=False,
    )

    workflow = WorkflowResult(
        success=True,
        initial_diagnostic=diagnostic,
        final_diagnostic=diagnostic,
        recommendations=RecommendationResult(
            recommendations=[
                "Zalecane wykonanie Sweep bazy danych."
            ]
        ),
        steps=[
            WorkflowStep(
                name="Diagnostyka początkowa",
                status="SUCCESS",
                message="OK",
            ),
            WorkflowStep(
                name="Backup",
                status="SUCCESS",
                message="OK",
            ),
            WorkflowStep(
                name="Ponowna diagnostyka",
                status="SUCCESS",
                message="Duży dystans transakcji.",
            ),
            WorkflowStep(
                name="Rekomendacje",
                status="SUCCESS",
                message="Wygenerowano.",
            ),
        ],
        backup_file="C:/backup/test.fbk",
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "WARNING"

    assert (
        "Zalecane wykonanie Sweep bazy danych."
        in report.recommendations
    )


# ==========================================================
# TEST 7
# ==========================================================


def test_generate_workflow_report_contains_diagnostics():

    service = ReportService()

    workflow = create_success_workflow()

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    initial_items = [
        item
        for item in report.items
        if item.section
        == "Diagnostyka początkowa"
    ]

    final_items = [
        item
        for item in report.items
        if item.section
        == "Diagnostyka końcowa"
    ]

    assert len(initial_items) == 5
    assert len(final_items) == 5

    assert any(
        item.name == "Status"
        for item in initial_items
    )

    assert any(
        item.name == "Transaction Gap"
        for item in initial_items
    )

    assert any(
        item.name == "Active Gap"
        for item in final_items
    )

    assert any(
        item.name == "Snapshot Gap"
        for item in final_items
    )


# ==========================================================
# TEST 8
# ==========================================================


def test_generate_workflow_report_no_reserve():

    service = ReportService()

    diagnostic = DiagnosticResult(
        status="success",
        message=(
            "Baza działa prawidłowo. "
            "No Reserve jest włączone."
        ),
        transaction_gap=0,
        active_gap=0,
        snapshot_gap=0,
        no_reserve_warning=True,
    )

    workflow = WorkflowResult(
        success=True,
        initial_diagnostic=diagnostic,
        final_diagnostic=diagnostic,
        recommendations=RecommendationResult(
            recommendations=[
                "No Reserve jest włączone."
            ]
        ),
        steps=[
            WorkflowStep(
                name="Diagnostyka początkowa",
                status="SUCCESS",
            ),
            WorkflowStep(
                name="Backup",
                status="SUCCESS",
            ),
            WorkflowStep(
                name="Ponowna diagnostyka",
                status="SUCCESS",
            ),
            WorkflowStep(
                name="Rekomendacje",
                status="SUCCESS",
            ),
        ],
        backup_file="C:/backup/test.fbk",
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "OK"

    no_reserve_items = [
        item
        for item in report.items
        if item.name == "No Reserve"
    ]

    assert len(no_reserve_items) == 2

    assert all(
        item.value == "ON"
        for item in no_reserve_items
    )


# ==========================================================
# TEST 9
# ==========================================================


def test_generate_database_report():

    service = ReportService()

    statistics = DatabaseStatistics(
        ods="13.0",
        page_size=8192,
        page_buffers=2048,
        sweep_interval=20000,
        oldest_transaction=100,
        oldest_active=110,
        oldest_snapshot=120,
        next_transaction=500,
        database_dialect=3,
        generation=10,
        forced_writes=True,
        no_reserve=False,
        creation_date="Aug 24, 2026",
    )

    health = DatabaseHealth(
        status="success",
        summary="Baza działa prawidłowo.",
        checks=[],
    )

    report = service.generate(
        database="C:/database/test.fdb",
        statistics=statistics,
        health=health,
        recommendations=[
            "Zalecane wykonanie Sweep."
        ],
    )

    assert report.database == (
        "C:/database/test.fdb"
    )

    assert report.status == "success"

    assert (
        report.summary
        == "Baza działa prawidłowo."
    )

    assert (
        "Zalecane wykonanie Sweep."
        in report.recommendations
    )

    names = [
        item.name
        for item in report.items
    ]

    assert "ODS" in names
    assert "Page Size" in names
    assert "Page Buffers" in names
    assert "Sweep Interval" in names
    assert "Force Write" in names
    assert "No Reserve" in names
    assert "Creation Date" in names


# ==========================================================
# TEST 10
# ==========================================================


def test_generate_database_report_recommendation_result():

    service = ReportService()

    statistics = DatabaseStatistics()

    health = DatabaseHealth(
        status="success",
        summary="OK",
        checks=[],
    )

    recommendations = RecommendationResult(
        recommendations=[
            "Sweep",
            "Sprawdź transakcje",
        ]
    )

    report = service.generate(
        database="test.fdb",
        statistics=statistics,
        health=health,
        recommendations=recommendations,
    )

    assert report.recommendations == [
        "Sweep",
        "Sprawdź transakcje",
    ]


# ==========================================================
# TEST 11
# ==========================================================


def test_generate_database_report_single_recommendation():

    service = ReportService()

    report = service.generate(
        database="test.fdb",
        statistics=DatabaseStatistics(),
        health=DatabaseHealth(
            status="success",
            summary="OK",
            checks=[],
        ),
        recommendations="Wykonaj Sweep.",
    )

    assert report.recommendations == [
        "Wykonaj Sweep."
    ]


# ==========================================================
# TEST 12
# ==========================================================


def test_generate_database_report_no_recommendations():

    service = ReportService()

    report = service.generate(
        database="test.fdb",
        statistics=DatabaseStatistics(),
        health=DatabaseHealth(
            status="success",
            summary="OK",
            checks=[],
        ),
        recommendations=None,
    )

    assert report.recommendations == []


# ==========================================================
# TEST 13
# ==========================================================


def test_normalize_status():

    service = ReportService()

    assert service._normalize_status("success") == "OK"
    assert service._normalize_status("SUCCESS") == "OK"
    assert service._normalize_status("ok") == "OK"
    assert service._normalize_status("OK") == "OK"

    assert (
        service._normalize_status("warning")
        == "WARNING"
    )

    assert (
        service._normalize_status("WARNING")
        == "WARNING"
    )

    assert (
        service._normalize_status("error")
        == "ERROR"
    )

    assert (
        service._normalize_status("ERROR")
        == "ERROR"
    )

    assert (
        service._normalize_status("pending")
        == "INFO"
    )

    assert (
        service._normalize_status("PENDING")
        == "INFO"
    )

    assert (
        service._normalize_status("info")
        == "INFO"
    )

    assert (
        service._normalize_status("INFO")
        == "INFO"
    )

    assert (
        service._normalize_status("unknown")
        == "INFO"
    )

    assert (
        service._normalize_status("UNKNOWN")
        == "INFO"
    )

    assert (
        service._normalize_status("nieznany-status")
        == "INFO"
    )


# ==========================================================
# TEST 14
# ==========================================================


def test_generate_workflow_report_without_backup():

    service = ReportService()

    workflow = WorkflowResult(
        success=True,
        steps=[],
        backup_file=None,
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "OK"

    backup_items = [
        item
        for item in report.items
        if item.section == "Backup"
    ]

    assert backup_items == []


# ==========================================================
# TEST 15
# ==========================================================


def test_generate_workflow_report_without_final_diagnostic():

    service = ReportService()

    workflow = WorkflowResult(
        success=True,
        steps=[],
        final_diagnostic=None,
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "OK"

    assert (
        report.summary
        == "Workflow zakończony pomyślnie."
    )


# ==========================================================
# TEST 16
# ==========================================================


def test_generate_workflow_report_pending_status():

    service = ReportService()

    workflow = WorkflowResult(
        success=True,
        steps=[
            WorkflowStep(
                name="Test",
                status="PENDING",
                message="Oczekuje.",
            )
        ],
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert len(report.items) == 1

    assert report.items[0].status == "INFO"


# ==========================================================
# TEST 17
# ==========================================================


def test_generate_workflow_report_final_diagnostic_error():

    service = ReportService()

    diagnostic = DiagnosticResult(
        status="error",
        message="Poważny problem.",
        transaction_gap=1_500_000,
        active_gap=100_000,
        snapshot_gap=100_000,
        no_reserve_warning=False,
    )

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=diagnostic,
        steps=[],
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "ERROR"

    assert (
        "Workflow zakończony. Poważny problem."
        == report.summary
    )

    diagnostic_items = [
        item
        for item in report.items
        if item.section == "Diagnostyka końcowa"
    ]

    assert len(diagnostic_items) == 5


# ==========================================================
# TEST 18
# ==========================================================


def test_generate_workflow_report_error_without_error_message():

    service = ReportService()

    workflow = WorkflowResult(
        success=False,
        steps=[],
        error="",
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert report.status == "ERROR"

    assert (
        report.summary
        == "Workflow nie został zakończony."
    )


# ==========================================================
# TEST 19
# ==========================================================


def test_generate_workflow_report_unknown_step_status():

    service = ReportService()

    workflow = WorkflowResult(
        success=True,
        steps=[
            WorkflowStep(
                name="Test",
                status="SOMETHING",
                message="Test",
            )
        ],
    )

    report = service.generate_workflow_report(
        database="test.fdb",
        workflow=workflow,
    )

    assert len(report.items) == 1

    assert report.items[0].status == "INFO"


# ==========================================================
# TEST 20
# ==========================================================


def test_generate_database_report_recommendation_tuple():

    service = ReportService()

    report = service.generate(
        database="test.fdb",
        statistics=DatabaseStatistics(),
        health=DatabaseHealth(
            status="success",
            summary="OK",
            checks=[],
        ),
        recommendations=(
            "Sweep",
            "Sprawdź transakcje",
        ),
    )

    assert report.recommendations == [
        "Sweep",
        "Sprawdź transakcje",
    ]