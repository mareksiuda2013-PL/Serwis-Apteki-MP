from __future__ import annotations

from services.firebird.report_service import (
    ReportService,
)
from services.firebird.diagnostics_service import (
    DiagnosticResult,
)
from models import DatabaseStatistics
from models.database_health import (
    DatabaseHealth,
    HealthCheck,
)
from models.report import (
    DatabaseReport,
    ReportItem,
)
from services.firebird.workflow_service import (
    WorkflowResult,
)


def create_service():
    return ReportService()


def create_statistics():

    return DatabaseStatistics(
        ods="13.0",
        page_size=8192,
        page_buffers=2048,
        sweep_interval=20_000,
        forced_writes=True,
        no_reserve=False,
        oldest_transaction=100,
        oldest_active=150,
        oldest_snapshot=120,
        next_transaction=500,
        database_dialect=3,
        generation=42,
        creation_date="2026-08-25 10:00",
    )


def create_health(
    status="OK",
    summary="Baza wygląda prawidłowo.",
):

    health = DatabaseHealth(
        status=status,
        summary=summary,
    )

    health.checks.append(
        HealthCheck(
            name="ODS",
            status="OK",
            value="13.0",
            message="ODS OK",
        )
    )

    health.checks.append(
        HealthCheck(
            name="Page Size",
            status="WARNING",
            value="8192",
            message="Test warning",
        )
    )

    return health


def create_diagnostic(
    *,
    status="success",
    message="Baza działa prawidłowo.",
    transaction_gap=100,
    active_gap=50,
    snapshot_gap=25,
    no_reserve_warning=False,
):

    return DiagnosticResult(
        status=status,
        message=message,
        transaction_gap=transaction_gap,
        active_gap=active_gap,
        snapshot_gap=snapshot_gap,
        no_reserve_warning=no_reserve_warning,
    )


# ==========================================================
# GENERATE
# ==========================================================


def test_generate_returns_database_report():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    assert isinstance(
        result,
        DatabaseReport,
    )


def test_generate_sets_database():

    service = create_service()

    result = service.generate(
        database="C:/database/TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    assert result.database == (
        "C:/database/TEST.FDB"
    )


def test_generate_uses_health_status():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(
            status="WARNING",
        ),
    )

    assert result.status == "WARNING"


def test_generate_uses_health_summary():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(
            summary="Wykryto ostrzeżenia.",
        ),
    )

    assert result.summary == (
        "Wykryto ostrzeżenia."
    )


# ==========================================================
# STATISTICS
# ==========================================================


def test_generate_adds_statistics():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    statistics_items = [
        item
        for item in result.items
        if item.section == "Statystyki"
    ]

    assert len(statistics_items) == 13


def test_statistics_contains_ods():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "ODS"
        )
    )

    assert item.status == "INFO"
    assert item.value == "13.0"


def test_statistics_contains_page_size():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Page Size"
        )
    )

    assert item.value == "8192"


def test_statistics_contains_page_buffers():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Page Buffers"
        )
    )

    assert item.value == "2048"


def test_statistics_contains_sweep_interval():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Sweep Interval"
        )
    )

    assert item.value == "20000"


def test_statistics_contains_force_write():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Force Write"
        )
    )

    assert item.value == "ON"


def test_statistics_contains_no_reserve():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "No Reserve"
        )
    )

    assert item.value == "OFF"


def test_statistics_contains_creation_date():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Creation Date"
        )
    )

    assert item.value == (
        "2026-08-25 10:00"
    )


def test_empty_ods_is_replaced_with_dash():

    service = create_service()

    statistics = create_statistics()
    statistics.ods = ""

    result = service.generate(
        database="TEST.FDB",
        statistics=statistics,
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "ODS"
        )
    )

    assert item.value == "-"


def test_empty_creation_date_is_replaced_with_dash():

    service = create_service()

    statistics = create_statistics()
    statistics.creation_date = ""

    result = service.generate(
        database="TEST.FDB",
        statistics=statistics,
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Statystyki"
            and item.name == "Creation Date"
        )
    )

    assert item.value == "-"


# ==========================================================
# HEALTH
# ==========================================================


def test_generate_adds_health_status():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Health Check"
            and item.name == "Status"
        )
    )

    assert item.value == "OK"
    assert item.status == "OK"


def test_generate_adds_health_checks():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    health_items = [
        item
        for item in result.items
        if item.section == "Health Check"
    ]

    assert len(health_items) == 3


def test_health_check_message_is_preserved():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Health Check"
            and item.name == "Page Size"
        )
    )

    assert item.message == (
        "Test warning"
    )


# ==========================================================
# RECOMMENDATIONS
# ==========================================================


def test_generate_adds_recommendations_from_list():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
        recommendations=[
            "Wykonaj Sweep.",
            "Sprawdź transakcje.",
        ],
    )

    assert result.recommendations == [
        "Wykonaj Sweep.",
        "Sprawdź transakcje.",
    ]


def test_generate_adds_recommendations_from_tuple():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
        recommendations=(
            "Test 1",
            "Test 2",
        ),
    )

    assert result.recommendations == [
        "Test 1",
        "Test 2",
    ]


def test_generate_adds_recommendations_from_result_object():

    service = create_service()

    recommendations = type(
        "RecommendationMock",
        (),
        {
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
            ]
        },
    )()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
        recommendations=recommendations,
    )

    assert result.recommendations == [
        "Recommendation 1",
        "Recommendation 2",
    ]


def test_generate_adds_single_recommendation():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
        recommendations="Jedna rekomendacja",
    )

    assert result.recommendations == [
        "Jedna rekomendacja"
    ]


def test_generate_without_recommendations():

    service = create_service()

    result = service.generate(
        database="TEST.FDB",
        statistics=create_statistics(),
        health=create_health(),
    )

    assert result.recommendations == []


# ==========================================================
# NORMALIZE STATUS
# ==========================================================


def test_normalize_success():

    assert (
        ReportService._normalize_status(
            "success"
        )
        == "OK"
    )


def test_normalize_uppercase_success():

    assert (
        ReportService._normalize_status(
            "SUCCESS"
        )
        == "OK"
    )


def test_normalize_ok():

    assert (
        ReportService._normalize_status(
            "ok"
        )
        == "OK"
    )


def test_normalize_warning():

    assert (
        ReportService._normalize_status(
            "warning"
        )
        == "WARNING"
    )


def test_normalize_error():

    assert (
        ReportService._normalize_status(
            "error"
        )
        == "ERROR"
    )


def test_normalize_pending():

    assert (
        ReportService._normalize_status(
            "pending"
        )
        == "INFO"
    )


def test_normalize_info():

    assert (
        ReportService._normalize_status(
            "info"
        )
        == "INFO"
    )


def test_normalize_unknown():

    assert (
        ReportService._normalize_status(
            "unknown"
        )
        == "INFO"
    )


def test_normalize_unrecognized_status():

    assert (
        ReportService._normalize_status(
            "SOMETHING_ELSE"
        )
        == "INFO"
    )


# ==========================================================
# DIAGNOSTIC DETAILS
# ==========================================================


def test_add_diagnostic_details():

    service = create_service()

    report = DatabaseReport(
        database="TEST.FDB",
        status="OK",
        summary="OK",
    )

    diagnostic = create_diagnostic(
        transaction_gap=1000,
        active_gap=2000,
        snapshot_gap=3000,
        no_reserve_warning=True,
    )

    service._add_diagnostic_details(
        report,
        diagnostic,
        "Test Diagnostic",
    )

    assert len(report.items) == 4

    assert report.items[0].name == (
        "Transaction Gap"
    )
    assert report.items[0].value == "1000"

    assert report.items[1].name == (
        "Active Gap"
    )
    assert report.items[1].value == "2000"

    assert report.items[2].name == (
        "Snapshot Gap"
    )
    assert report.items[2].value == "3000"

    assert report.items[3].name == (
        "No Reserve"
    )
    assert report.items[3].value == "ON"


# ==========================================================
# WORKFLOW HELPERS
# ==========================================================


def test_workflow_status_error_when_error_exists():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        error="Workflow ERROR",
    )

    assert service._workflow_status(
        workflow
    ) == "ERROR"


def test_workflow_status_error_when_final_diagnostic_error():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            status="error"
        ),
    )

    assert service._workflow_status(
        workflow
    ) == "ERROR"


def test_workflow_status_warning_when_final_diagnostic_warning():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            status="warning"
        ),
    )

    assert service._workflow_status(
        workflow
    ) == "WARNING"


def test_workflow_status_error_when_workflow_failed():

    service = create_service()

    workflow = WorkflowResult(
        success=False,
    )

    assert service._workflow_status(
        workflow
    ) == "ERROR"


def test_workflow_status_ok_when_successful():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    assert service._workflow_status(
        workflow
    ) == "OK"


# ==========================================================
# WORKFLOW SUMMARY
# ==========================================================


def test_workflow_summary_contains_error():

    service = create_service()

    workflow = WorkflowResult(
        success=False,
        error="Test ERROR",
    )

    assert service._workflow_summary(
        workflow
    ) == (
        "Workflow zakończony błędem: "
        "Test ERROR"
    )


def test_workflow_summary_uses_final_diagnostic():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            message="Diagnostyka zakończona.",
        ),
    )

    assert service._workflow_summary(
        workflow
    ) == (
        "Workflow zakończony. "
        "Diagnostyka zakończona."
    )


def test_workflow_summary_success():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    assert service._workflow_summary(
        workflow
    ) == (
        "Workflow zakończony pomyślnie."
    )


def test_workflow_summary_not_finished():

    service = create_service()

    workflow = WorkflowResult(
        success=False,
    )

    assert service._workflow_summary(
        workflow
    ) == (
        "Workflow nie został zakończony."
    )


# ==========================================================
# WORKFLOW REPORT
# ==========================================================


def test_generate_workflow_report_returns_report():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert isinstance(
        result,
        DatabaseReport,
    )


def test_generate_workflow_report_sets_database():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    result = service.generate_workflow_report(
        database="C:/TEST.FDB",
        workflow=workflow,
    )

    assert result.database == (
        "C:/TEST.FDB"
    )


def test_generate_workflow_report_success_status():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert result.status == "OK"


def test_generate_workflow_report_adds_steps():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
    )

    workflow.steps = [
        type(
            "Step",
            (),
            {
                "name": "Backup",
                "status": "success",
                "message": "Backup OK",
            },
        )(),
        type(
            "Step",
            (),
            {
                "name": "Validate",
                "status": "warning",
                "message": "Validate WARNING",
            },
        )(),
    ]

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert len(result.items) == 2

    assert result.items[0].section == (
        "Workflow"
    )

    assert result.items[0].name == (
        "Backup"
    )

    assert result.items[0].status == "OK"

    assert result.items[1].status == (
        "WARNING"
    )


def test_generate_workflow_report_adds_backup_file():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        backup_file="C:/backup/test.fbk",
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    item = next(
        item
        for item in result.items
        if (
            item.section == "Backup"
            and item.name == "Plik backupu"
        )
    )

    assert item.section == "Backup"
    assert item.status == "INFO"
    assert item.value == (
        "C:/backup/test.fbk"
    )


def test_generate_workflow_report_adds_initial_diagnostic():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        initial_diagnostic=create_diagnostic(
            status="warning",
            message="Initial warning",
        ),
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    items = [
        item
        for item in result.items
        if item.section
        == "Diagnostyka początkowa"
    ]

    assert len(items) == 5

    assert items[0].name == "Status"
    assert items[0].status == "WARNING"
    assert items[0].value == "warning"
    assert items[0].message == (
        "Initial warning"
    )


def test_generate_workflow_report_adds_final_diagnostic():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            status="success",
            message="Final OK",
        ),
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    items = [
        item
        for item in result.items
        if item.section
        == "Diagnostyka końcowa"
    ]

    assert len(items) == 5

    assert items[0].name == "Status"
    assert items[0].status == "OK"
    assert items[0].value == "success"
    assert items[0].message == (
        "Final OK"
    )


def test_generate_workflow_report_adds_recommendations():

    service = create_service()

    recommendations = type(
        "RecommendationMock",
        (),
        {
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
            ]
        },
    )()

    workflow = WorkflowResult(
        success=True,
        recommendations=recommendations,
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert result.recommendations == [
        "Recommendation 1",
        "Recommendation 2",
    ]


def test_generate_workflow_report_adds_error():

    service = create_service()

    workflow = WorkflowResult(
        success=False,
        error="Workflow ERROR",
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert result.status == "ERROR"

    item = next(
        item
        for item in result.items
        if (
            item.section == "Workflow"
            and item.name == "Błąd"
        )
    )

    assert item.section == "Workflow"
    assert item.status == "ERROR"
    assert item.value == "ERROR"
    assert item.message == (
        "Workflow ERROR"
    )


def test_generate_workflow_report_final_error_has_error_status():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            status="error",
            message="Critical error",
        ),
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert result.status == "ERROR"


def test_generate_workflow_report_final_warning_has_warning_status():

    service = create_service()

    workflow = WorkflowResult(
        success=True,
        final_diagnostic=create_diagnostic(
            status="warning",
            message="Warning",
        ),
    )

    result = service.generate_workflow_report(
        database="TEST.FDB",
        workflow=workflow,
    )

    assert result.status == "WARNING"