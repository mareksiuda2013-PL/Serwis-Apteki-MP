from __future__ import annotations

from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from services.firebird.report_service import (
    ReportService,
)
from services.firebird.workflow_service import (
    WorkflowResult,
    WorkflowStep,
)
from services.firebird.recommendation_service import (
    RecommendationResult,
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