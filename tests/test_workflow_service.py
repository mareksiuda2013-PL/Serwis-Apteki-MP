from __future__ import annotations

from unittest.mock import MagicMock

from services.firebird.workflow_service import (
    WorkflowResult,
    WorkflowService,
    WorkflowStep,
)


# ==========================================================
# FACTORIES
# ==========================================================


def create_services():

    statistics_service = MagicMock()
    diagnostics_service = MagicMock()
    recommendation_service = MagicMock()
    backup_service = MagicMock()

    return (
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    )


def create_diagnostic(
    status="success",
    message="Baza działa prawidłowo.",
):

    diagnostic = MagicMock()

    diagnostic.status = status
    diagnostic.message = message

    return diagnostic


def create_recommendations(
    recommendations=None,
):

    result = MagicMock()

    if recommendations is None:
        recommendations = [
            "Brak dodatkowych rekomendacji."
        ]

    result.recommendations = recommendations
    result.has_recommendations = bool(
        recommendations
    )

    return result


def create_workflow():

    (
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_services()

    service = WorkflowService(
        statistics_service=statistics_service,
        diagnostics_service=diagnostics_service,
        recommendation_service=recommendation_service,
        backup_service=backup_service,
    )

    return (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    )


# ==========================================================
# WORKFLOW STEP
# ==========================================================


def test_workflow_step_defaults():

    step = WorkflowStep(
        name="Test"
    )

    assert step.name == "Test"
    assert step.status == "PENDING"
    assert step.message == ""


def test_workflow_step_values():

    step = WorkflowStep(
        name="Backup",
        status="SUCCESS",
        message="Backup OK",
    )

    assert step.name == "Backup"
    assert step.status == "SUCCESS"
    assert step.message == "Backup OK"


# ==========================================================
# WORKFLOW RESULT
# ==========================================================


def test_workflow_result_defaults():

    result = WorkflowResult()

    assert result.success is False
    assert result.initial_diagnostic is None
    assert result.final_diagnostic is None
    assert result.recommendations is None
    assert result.steps == []
    assert result.backup_file == ""
    assert result.error == ""


def test_workflow_result_has_error():

    result = WorkflowResult(
        error="Test ERROR"
    )

    assert result.has_error is True


def test_workflow_result_has_no_error():

    result = WorkflowResult()

    assert result.has_error is False


def test_workflow_result_has_recommendations():

    result = WorkflowResult(
        recommendations=create_recommendations()
    )

    assert result.has_recommendations is True


def test_workflow_result_has_no_recommendations_when_none():

    result = WorkflowResult()

    assert result.has_recommendations is False


def test_workflow_result_has_no_recommendations_when_empty():

    recommendations = create_recommendations(
        []
    )

    result = WorkflowResult(
        recommendations=recommendations
    )

    assert result.has_recommendations is False


# ==========================================================
# SUCCESSFUL WORKFLOW
# ==========================================================


def test_workflow_success():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    initial_stats = MagicMock(
        name="InitialStatistics"
    )

    final_stats = MagicMock(
        name="FinalStatistics"
    )

    initial_diagnostic = create_diagnostic(
        message="Initial OK"
    )

    final_diagnostic = create_diagnostic(
        message="Final OK"
    )

    recommendations = create_recommendations(
        [
            "Wykonaj Sweep."
        ]
    )

    statistics_service.statistics.side_effect = [
        initial_stats,
        final_stats,
    ]

    diagnostics_service.analyze.side_effect = [
        initial_diagnostic,
        final_diagnostic,
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        recommendations
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert isinstance(
        result,
        WorkflowResult,
    )

    assert result.success is True
    assert result.error == ""

    assert result.initial_diagnostic is (
        initial_diagnostic
    )

    assert result.final_diagnostic is (
        final_diagnostic
    )

    assert result.recommendations is (
        recommendations
    )

    assert result.backup_file == (
        "C:/backup/test.fbk"
    )


def test_workflow_creates_four_steps():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert len(result.steps) == 4


def test_workflow_steps_have_correct_order():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(
            message="Initial"
        ),
        create_diagnostic(
            message="Final"
        ),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert [
        step.name
        for step in result.steps
    ] == [
        "Diagnostyka początkowa",
        "Backup",
        "Ponowna diagnostyka",
        "Rekomendacje",
    ]


def test_workflow_steps_are_successful():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert [
        step.status
        for step in result.steps
    ] == [
        "SUCCESS",
        "SUCCESS",
        "SUCCESS",
        "SUCCESS",
    ]


# ==========================================================
# INITIAL DIAGNOSTIC
# ==========================================================


def test_initial_diagnostic_uses_statistics():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    initial_stats = MagicMock()

    statistics_service.statistics.side_effect = [
        initial_stats,
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    service.run(
        "C:/backup/test.fbk"
    )

    diagnostics_service.analyze.assert_any_call(
        initial_stats
    )


def test_initial_diagnostic_message_is_preserved():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(
            message="Initial diagnostic message"
        ),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.steps[0].message == (
        "Initial diagnostic message"
    )


def test_initial_diagnostic_exception_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = (
        RuntimeError(
            "Statistics ERROR"
        )
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False
    assert result.error == (
        "Błąd diagnostyki początkowej: "
        "Statistics ERROR"
    )

    assert len(result.steps) == 1

    assert result.steps[0].status == "ERROR"

    backup_service.backup.assert_not_called()
    recommendation_service.recommend.assert_not_called()


def test_initial_diagnostic_analyze_exception_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.return_value = (
        MagicMock()
    )

    diagnostics_service.analyze.side_effect = (
        RuntimeError(
            "Diagnostic ERROR"
        )
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False
    assert result.error == (
        "Błąd diagnostyki początkowej: "
        "Diagnostic ERROR"
    )

    assert len(result.steps) == 1

    backup_service.backup.assert_not_called()


# ==========================================================
# BACKUP
# ==========================================================


def test_backup_receives_requested_file():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    service.run(
        "C:/backup/my_database.fbk"
    )

    backup_service.backup.assert_called_once_with(
        "C:/backup/my_database.fbk"
    )


def test_backup_success_sets_backup_file():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup completed",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.backup_file == (
        "C:/backup/test.fbk"
    )


def test_backup_message_is_preserved():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup completed",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    backup_step = result.steps[1]

    assert backup_step.status == "SUCCESS"
    assert backup_step.message == (
        "Backup completed"
    )


def test_backup_failure_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.return_value = (
        MagicMock()
    )

    diagnostics_service.analyze.return_value = (
        create_diagnostic()
    )

    backup_service.backup.return_value = (
        False,
        "Backup ERROR",
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False
    assert result.error == (
        "Backup ERROR"
    )

    assert len(result.steps) == 2

    assert result.steps[1].status == "ERROR"
    assert result.steps[1].message == (
        "Backup ERROR"
    )

    assert result.final_diagnostic is None

    recommendation_service.recommend.assert_not_called()


def test_backup_failure_without_message_uses_default():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.return_value = (
        MagicMock()
    )

    diagnostics_service.analyze.return_value = (
        create_diagnostic()
    )

    backup_service.backup.return_value = (
        False,
        "",
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert result.error == (
        "Backup nie powiódł się."
    )

    assert result.steps[1].message == (
        "Backup nie powiódł się."
    )


def test_backup_exception_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.return_value = (
        MagicMock()
    )

    diagnostics_service.analyze.return_value = (
        create_diagnostic()
    )

    backup_service.backup.side_effect = (
        RuntimeError(
            "Backup exception"
        )
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert result.error == (
        "Błąd backupu: Backup exception"
    )

    assert len(result.steps) == 2

    assert result.steps[1].status == "ERROR"

    recommendation_service.recommend.assert_not_called()


# ==========================================================
# FINAL DIAGNOSTIC
# ==========================================================


def test_final_diagnostic_runs_after_backup():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    initial_stats = MagicMock(
        name="InitialStats"
    )

    final_stats = MagicMock(
        name="FinalStats"
    )

    statistics_service.statistics.side_effect = [
        initial_stats,
        final_stats,
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(
            message="Initial"
        ),
        create_diagnostic(
            message="Final"
        ),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.final_diagnostic is not None

    diagnostics_service.analyze.assert_any_call(
        final_stats
    )


def test_final_diagnostic_message_is_preserved():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(
            message="Final diagnostic message"
        ),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.steps[2].message == (
        "Final diagnostic message"
    )


def test_final_diagnostic_exception_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        RuntimeError(
            "Final diagnostic ERROR"
        ),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert result.error == (
        "Błąd ponownej diagnostyki: "
        "Final diagnostic ERROR"
    )

    assert len(result.steps) == 3

    recommendation_service.recommend.assert_not_called()


# ==========================================================
# RECOMMENDATIONS
# ==========================================================


def test_recommendations_receive_final_diagnostic():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    initial_diagnostic = create_diagnostic()
    final_diagnostic = create_diagnostic()

    diagnostics_service.analyze.side_effect = [
        initial_diagnostic,
        final_diagnostic,
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendations = create_recommendations()

    recommendation_service.recommend.return_value = (
        recommendations
    )

    service.run(
        "C:/backup/test.fbk"
    )

    recommendation_service.recommend.assert_called_once_with(
        final_diagnostic
    )


def test_recommendations_are_stored():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendations = create_recommendations(
        [
            "Sweep",
            "Sprawdź transakcje",
        ]
    )

    recommendation_service.recommend.return_value = (
        recommendations
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.recommendations is (
        recommendations
    )


def test_recommendations_step_success():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.return_value = (
        create_recommendations()
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.steps[3].status == (
        "SUCCESS"
    )

    assert result.steps[3].message == (
        "Rekomendacje zostały wygenerowane."
    )


def test_recommendations_exception_stops_workflow():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.side_effect = [
        MagicMock(),
        MagicMock(),
    ]

    diagnostics_service.analyze.side_effect = [
        create_diagnostic(),
        create_diagnostic(),
    ]

    backup_service.backup.return_value = (
        True,
        "Backup OK",
    )

    recommendation_service.recommend.side_effect = (
        RuntimeError(
            "Recommendation ERROR"
        )
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False

    assert result.error == (
        "Błąd generowania rekomendacji: "
        "Recommendation ERROR"
    )

    assert len(result.steps) == 4

    assert result.steps[3].status == (
        "ERROR"
    )

    assert result.steps[3].message == (
        "Recommendation ERROR"
    )


# ==========================================================
# FINAL SUCCESS
# ==========================================================


def test_success_is_false_when_any_step_fails():

    (
        service,
        statistics_service,
        diagnostics_service,
        recommendation_service,
        backup_service,
    ) = create_workflow()

    statistics_service.statistics.return_value = (
        MagicMock()
    )

    diagnostics_service.analyze.return_value = (
        create_diagnostic()
    )

    backup_service.backup.return_value = (
        False,
        "Backup ERROR",
    )

    result = service.run(
        "C:/backup/test.fbk"
    )

    assert result.success is False
    assert result.has_error is True