from __future__ import annotations

from unittest.mock import MagicMock, patch

from services.firebird.firebird_controller import FirebirdController


# ==========================================================
# HELPERS
# ==========================================================


def create_controller():

    with (
        patch(
            "services.firebird.firebird_controller.FirebirdService"
        ) as firebird_cls,
        patch(
            "services.firebird.firebird_controller.StatisticsService"
        ) as statistics_cls,
        patch(
            "services.firebird.firebird_controller.HealthService"
        ) as health_cls,
        patch(
            "services.firebird.firebird_controller.DiagnosticsService"
        ) as diagnostics_cls,
        patch(
            "services.firebird.firebird_controller.RecommendationService"
        ) as recommendation_cls,
        patch(
            "services.firebird.firebird_controller.ReportService"
        ) as report_cls,
        patch(
            "services.firebird.firebird_controller.WorkflowService"
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
# INITIALIZATION
# ==========================================================


def test_controller_creates_all_services():

    with (
        patch(
            "services.firebird.firebird_controller.FirebirdService"
        ) as firebird_cls,
        patch(
            "services.firebird.firebird_controller.StatisticsService"
        ) as statistics_cls,
        patch(
            "services.firebird.firebird_controller.HealthService"
        ) as health_cls,
        patch(
            "services.firebird.firebird_controller.DiagnosticsService"
        ) as diagnostics_cls,
        patch(
            "services.firebird.firebird_controller.RecommendationService"
        ) as recommendation_cls,
        patch(
            "services.firebird.firebird_controller.ReportService"
        ) as report_cls,
        patch(
            "services.firebird.firebird_controller.WorkflowService"
        ) as workflow_cls,
    ):

        controller = FirebirdController()

    assert controller.firebird is firebird_cls.return_value
    assert controller.statistics_service is statistics_cls.return_value
    assert controller.health_service is health_cls.return_value
    assert controller.diagnostics_service is diagnostics_cls.return_value
    assert controller.recommendation_service is recommendation_cls.return_value
    assert controller.report_service is report_cls.return_value
    assert controller.workflow_service is workflow_cls.return_value


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

    firebird.cfg.database = r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"

    assert controller.database() == r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"


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

    firebird.get_info.assert_called_once_with(database=None)
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

    database = r"C:\test\database.fdb"
    expected = MagicMock()

    firebird.get_info.return_value = expected

    result = controller.info(database=database)

    firebird.get_info.assert_called_once_with(database=database)
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

    path = r"C:\test\database.fdb"
    expected = MagicMock()

    firebird.inspect_database.return_value = expected

    result = controller.inspect_database(path)

    firebird.inspect_database.assert_called_once_with(path)
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


def test_diagnostics_gets_statistics_automatically():

    (
        controller,
        _,
        _,
        _,
        diagnostics,
        _,
        _,
        _,
    ) = create_controller()

    stats = MagicMock()
    expected = MagicMock()

    with patch.object(
        controller,
        "statistics",
        return_value=stats,
    ) as statistics_method:

        diagnostics.analyze.return_value = expected

        result = controller.diagnostics()

    statistics_method.assert_called_once_with()
    diagnostics.analyze.assert_called_once_with(stats)
    assert result is expected


def test_diagnostics_uses_provided_statistics():

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

    diagnostics.analyze.return_value = expected

    result = controller.diagnostics(stats)

    statistics.statistics.assert_not_called()
    diagnostics.analyze.assert_called_once_with(stats)
    assert result is expected


# ==========================================================
# RECOMMENDATIONS
# ==========================================================


def test_recommendations_gets_diagnostics_automatically():

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

        recommendations.recommend.return_value = expected

        result = controller.recommendations()

    diagnostics_method.assert_called_once_with()
    recommendations.recommend.assert_called_once_with(diagnostic)
    assert result is expected


def test_recommendations_uses_provided_diagnostic():

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

    recommendations.recommend.return_value = expected

    result = controller.recommendations(diagnostic)

    recommendations.recommend.assert_called_once_with(diagnostic)
    assert result is expected


# ==========================================================
# HEALTH
# ==========================================================


def test_health_gets_statistics_automatically():

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

    stats = MagicMock()
    expected = MagicMock()

    with patch.object(
        controller,
        "statistics",
        return_value=stats,
    ) as statistics_method:

        health.check.return_value = expected

        result = controller.health()

    statistics_method.assert_called_once_with()
    health.check.assert_called_once_with(stats)
    assert result is expected


def test_health_uses_provided_statistics():

    (
        controller,
        _,
        statistics,
        health,
        _,
        _,
        _,
        _,
    ) = create_controller()

    stats = MagicMock()
    expected = MagicMock()

    health.check.return_value = expected

    result = controller.health(stats)

    statistics.statistics.assert_not_called()
    health.check.assert_called_once_with(stats)
    assert result is expected


# ==========================================================
# REPORT
# ==========================================================


def test_report_builds_all_missing_data():

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

    database = r"C:\test\database.fdb"
    stats = MagicMock()
    health_result = MagicMock()
    diagnostic_result = MagicMock()
    recommendation_result = MagicMock()
    expected_report = MagicMock()

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
        ) as statistics_method,
        patch.object(
            controller,
            "health",
            return_value=health_result,
        ) as health_method,
        patch.object(
            controller,
            "diagnostics",
            return_value=diagnostic_result,
        ) as diagnostics_method,
        patch.object(
            controller,
            "recommendations",
            return_value=recommendation_result,
        ) as recommendations_method,
    ):

        report_service.generate.return_value = expected_report

        result = controller.report()

    statistics_method.assert_called_once_with()
    health_method.assert_called_once_with(stats)
    diagnostics_method.assert_called_once_with(stats)
    recommendations_method.assert_called_once_with(diagnostic_result)

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
        _,
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
        ) as statistics_method,
    ):

        report_service.generate.return_value = expected_report

        result = controller.report(
            diagnostic=diagnostic_result,
            health=health_result,
            recommendations=recommendation_result,
        )

    statistics_method.assert_called_once_with()
    health.check.assert_not_called()
    diagnostics.analyze.assert_not_called()
    recommendations.recommend.assert_not_called()

    report_service.generate.assert_called_once_with(
        database=database,
        statistics=stats,
        health=health_result,
        recommendations=recommendation_result,
    )

    assert result is expected_report


def test_report_uses_provided_diagnostic():

    (
        controller,
        _,
        _,
        _,
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
            "recommendations",
            return_value=recommendation_result,
        ) as recommendations_method,
    ):

        report_service.generate.return_value = expected_report

        result = controller.report(
            diagnostic=diagnostic_result,
        )

    recommendations_method.assert_called_once_with(diagnostic_result)
    diagnostics.analyze.assert_not_called()

    report_service.generate.assert_called_once_with(
        database=database,
        statistics=stats,
        health=health_result,
        recommendations=recommendation_result,
    )

    assert result is expected_report


def test_report_uses_provided_health():

    (
        controller,
        _,
        _,
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
            "diagnostics",
            return_value=diagnostic_result,
        ),
        patch.object(
            controller,
            "recommendations",
            return_value=recommendation_result,
        ),
    ):

        report_service.generate.return_value = expected_report

        result = controller.report(
            health=health_result,
        )

    health.check.assert_not_called()
    diagnostics.analyze.assert_not_called()
    recommendations.recommend.assert_not_called()

    report_service.generate.assert_called_once_with(
        database=database,
        statistics=stats,
        health=health_result,
        recommendations=recommendation_result,
    )

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

    backup_file = r"C:\backup\WAPTEKA.FBK"
    expected = MagicMock()

    workflow_service.run.return_value = expected

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

    database = r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    workflow = MagicMock()
    expected = MagicMock()

    with patch.object(
        controller,
        "database",
        return_value=database,
    ):

        report_service.generate_workflow_report.return_value = expected

        result = controller.workflow_report(workflow)

    report_service.generate_workflow_report.assert_called_once_with(
        database=database,
        workflow=workflow,
    )

    assert result is expected


def test_workflow_report_uses_configured_database():

    (
        controller,
        firebird,
        _,
        _,
        _,
        _,
        report_service,
        _,
    ) = create_controller()

    database = r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    workflow = MagicMock()
    expected = MagicMock()

    firebird.cfg.database = database
    report_service.generate_workflow_report.return_value = expected

    result = controller.workflow_report(workflow)

    report_service.generate_workflow_report.assert_called_once_with(
        database=database,
        workflow=workflow,
    )

    assert result is expected


# ==========================================================
# ERROR PROPAGATION
# ==========================================================


def test_statistics_propagates_service_exception():

    (
        controller,
        _,
        statistics_service,
        _,
        _,
        _,
        _,
        _,
    ) = create_controller()

    statistics_service.statistics.side_effect = RuntimeError(
        "Błąd statystyk"
    )

    try:
        controller.statistics()
    except RuntimeError as exc:
        assert str(exc) == "Błąd statystyk"
    else:
        raise AssertionError(
            "Controller powinien przekazać wyjątek dalej"
        )


def test_info_propagates_firebird_service_exception():

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

    firebird.get_info.side_effect = RuntimeError(
        "Błąd Firebird"
    )

    try:
        controller.info()
    except RuntimeError as exc:
        assert str(exc) == "Błąd Firebird"
    else:
        raise AssertionError(
            "Controller powinien przekazać wyjątek dalej"
        )


def test_inspect_database_propagates_service_exception():

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

    firebird.inspect_database.side_effect = RuntimeError(
        "Błąd inspekcji"
    )

    try:
        controller.inspect_database(
            r"C:\test\database.fdb"
        )
    except RuntimeError as exc:
        assert str(exc) == "Błąd inspekcji"
    else:
        raise AssertionError(
            "Controller powinien przekazać wyjątek dalej"
        )


def test_workflow_propagates_service_exception():

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

    workflow_service.run.side_effect = RuntimeError(
        "Błąd workflow"
    )

    try:
        controller.workflow(
            backup_file=r"C:\backup\WAPTEKA.FBK"
        )
    except RuntimeError as exc:
        assert str(exc) == "Błąd workflow"
    else:
        raise AssertionError(
            "Controller powinien przekazać wyjątek dalej"
        )
