from __future__ import annotations

from unittest.mock import MagicMock, patch

from modules.firebird.controller import FirebirdController


def create_controller():

    with (
        patch(
            "modules.firebird.controller.FirebirdService"
        ) as firebird_cls,
        patch(
            "modules.firebird.controller.StatisticsService"
        ) as statistics_cls,
        patch(
            "modules.firebird.controller.HealthService"
        ) as health_cls,
        patch(
            "modules.firebird.controller.DiagnosticsService"
        ) as diagnostics_cls,
        patch(
            "modules.firebird.controller.RecommendationService"
        ) as recommendation_cls,
        patch(
            "modules.firebird.controller.ReportService"
        ) as report_cls,
        patch(
            "modules.firebird.controller.WorkflowService"
        ) as workflow_cls,
    ):

        controller = FirebirdController()

        return (
            controller,
            firebird_cls.return_value,
            statistics_cls.return_value,
            health_cls.return_value,
            diagnostics_cls.return_value,
            recommendation_cls.return_value,
            report_cls.return_value,
            workflow_cls.return_value,
        )


# ==========================================================
# DATABASE
# ==========================================================


def test_database_returns_configured_database():

    (
        controller,
        firebird,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    firebird.cfg.database = (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    assert controller.database() == (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )


# ==========================================================
# INFO
# ==========================================================


def test_info_calls_firebird_service():

    (
        controller,
        firebird,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    expected = MagicMock()

    firebird.get_info.return_value = expected

    result = controller.info()

    firebird.get_info.assert_called_once_with(
        database=None
    )

    assert result is expected


def test_info_passes_database():

    (
        controller,
        firebird,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    expected = MagicMock()

    firebird.get_info.return_value = expected

    database = r"C:\test\database.fdb"

    result = controller.info(
        database=database
    )

    firebird.get_info.assert_called_once_with(
        database=database
    )

    assert result is expected


# ==========================================================
# INSPECT DATABASE
# ==========================================================


def test_inspect_database_calls_firebird_service():

    (
        controller,
        firebird,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    expected = MagicMock()

    firebird.inspect_database.return_value = expected

    path = r"C:\test\database.fdb"

    result = controller.inspect_database(
        path
    )

    firebird.inspect_database.assert_called_once_with(
        path
    )

    assert result is expected


# ==========================================================
# STATISTICS
# ==========================================================


def test_statistics_calls_statistics_service():

    (
        controller,
        _,
        statistics,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    expected = MagicMock()

    statistics.statistics.return_value = expected

    result = controller.statistics()

    statistics.statistics.assert_called_once_with()

    assert result is expected


# ==========================================================
# DIAGNOSTICS
# ==========================================================


def test_diagnostics_gets_statistics_and_analyzes():

    (
        controller,
        _,
        statistics,
        _,
        diagnostics,
        _,
        _,
        _,
    ) = create_controller()

    stats = MagicMock()
    expected = MagicMock()

    statistics.statistics.return_value = stats
    diagnostics.analyze.return_value = expected

    result = controller.diagnostics()

    statistics.statistics.assert_called_once_with()

    diagnostics.analyze.assert_called_once_with(
        stats
    )

    assert result is expected


# ==========================================================
# RECOMMENDATIONS
# ==========================================================


def test_recommendations_automatically_gets_diagnostics():

    (
        controller,
        _,
        _,
        _,
        _,
        recommendations,
        _,
        _,
    ) = create_controller()

    diagnostic = MagicMock()
    expected = MagicMock()

    with patch.object(
        controller,
        "diagnostics",
        return_value=diagnostic,
    ) as diagnostics_method:

        recommendations.recommend.return_value = (
            expected
        )

        result = controller.recommendations()

    diagnostics_method.assert_called_once_with()

    recommendations.recommend.assert_called_once_with(
        diagnostic
    )

    assert result is expected


def test_recommendations_uses_provided_diagnostic():

    (
        controller,
        _,
        _,
        diagnostics,
        _,
        recommendations,
        _,
        _,
    ) = create_controller()

    diagnostic = MagicMock()
    expected = MagicMock()

    recommendations.recommend.return_value = (
        expected
    )

    result = controller.recommendations(
        diagnostic
    )

    diagnostics.analyze.assert_not_called()

    recommendations.recommend.assert_called_once_with(
        diagnostic
    )

    assert result is expected


# ==========================================================
# HEALTH
# ==========================================================


def test_health_calls_health_service():

    (
        controller,
        _,
        _,
        health,
        _,
        _,
        _,
        _,
    ) = create_controller()

    expected = MagicMock()

    health.check.return_value = expected

    result = controller.health()

    health.check.assert_called_once_with()

    assert result is expected


# ==========================================================
# REPORT
# ==========================================================


def test_report_generates_complete_report():

    (
        controller,
        firebird,
        statistics,
        health,
        diagnostics,
        recommendations,
        report_service,
        _,
    ) = create_controller()

    database = r"C:\test\database.fdb"

    stats = MagicMock()
    health_result = MagicMock()
    diagnostic_result = MagicMock()
    recommendation_result = MagicMock()
    expected_report = MagicMock()

    firebird.cfg.database = database

    statistics.statistics.return_value = stats
    health.check.return_value = health_result
    diagnostics.analyze.return_value = diagnostic_result
    recommendations.recommend.return_value = (
        recommendation_result
    )
    report_service.generate.return_value = (
        expected_report
    )

    with (
        patch.object(
            controller,
            "database",
            return_value=database,
        ),
        patch.object(
            controller,
            "statistics",
            return_value=stats,
        ),
        patch.object(
            controller,
            "health",
            return_value=health_result,
        ),
        patch.object(
            controller,
            "diagnostics",
            return_value=diagnostic_result,
        ),
        patch.object(
            controller,
            "recommendations",
            return_value=recommendation_result,
        ),
    ):

        result = controller.report()

    report_service.generate.assert_called_once_with(
        database=database,
        statistics=stats,
        health=health_result,
        recommendations=recommendation_result,
    )

    assert result is expected_report


def test_report_uses_provided_data():

    (
        controller,
        _,
        statistics,
        health,
        diagnostics,
        recommendations,
        report_service,
        _,
    ) = create_controller()

    database = r"C:\test\database.fdb"

    stats = MagicMock()
    health_result = MagicMock()
    diagnostic_result = MagicMock()
    recommendation_result = MagicMock()
    expected_report = MagicMock()

    report_service.generate.return_value = (
        expected_report
    )

    with (
        patch.object(
            controller,
            "database",
            return_value=database,
        ),
        patch.object(
            controller,
            "statistics",
            return_value=stats,
        ),
    ):

        result = controller.report(
            diagnostic=diagnostic_result,
            health=health_result,
            recommendations=recommendation_result,
        )

    report_service.generate.assert_called_once_with(
        database=database,
        statistics=stats,
        health=health_result,
        recommendations=recommendation_result,
    )

    diagnostics.analyze.assert_not_called()

    recommendations.recommend.assert_not_called()

    health.check.assert_not_called()

    assert result is expected_report


# ==========================================================
# WORKFLOW
# ==========================================================


def test_workflow_calls_workflow_service():

    (
        controller,
        _,
        _,
        _,
        _,
        _,
        _,
        workflow_service,
    ) = create_controller()

    backup_file = (
        r"C:\backup\WAPTEKA.FBK"
    )

    expected = MagicMock()

    workflow_service.run.return_value = (
        expected
    )

    result = controller.workflow(
        backup_file=backup_file
    )

    workflow_service.run.assert_called_once_with(
        backup_file=backup_file
    )

    assert result is expected


# ==========================================================
# WORKFLOW REPORT
# ==========================================================


def test_workflow_report_calls_report_service():

    (
        controller,
        _,
        _,
        _,
        _,
        _,
        report_service,
        _,
    ) = create_controller()

    database = (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    workflow = MagicMock()
    expected = MagicMock()

    with patch.object(
        controller,
        "database",
        return_value=database,
    ):

        report_service.generate_workflow_report.return_value = (
            expected
        )

        result = controller.workflow_report(
            workflow
        )

    report_service.generate_workflow_report.assert_called_once_with(
        database=database,
        workflow=workflow,
    )

    assert result is expected