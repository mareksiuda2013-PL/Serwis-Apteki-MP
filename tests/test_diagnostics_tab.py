from __future__ import annotations

from unittest.mock import MagicMock

from modules.firebird.tabs.diagnostics_tab import DiagnosticsTab


def test_refresh_generates_recommendations():

    tab = DiagnosticsTab.__new__(
        DiagnosticsTab
    )

    stats = MagicMock()
    diagnostic = MagicMock()
    health = MagicMock()
    recommendation_result = MagicMock()

    tab.controller = MagicMock()

    tab.controller.statistics.return_value = stats
    tab.controller.diagnostics.return_value = diagnostic
    tab.controller.health.return_value = health
    tab.controller.recommendations.return_value = (
        recommendation_result
    )

    tab.refresh_button = MagicMock()
    tab.diagnostic_message = MagicMock()
    tab.recommendation_message = MagicMock()

    tab.lbl_active = MagicMock()
    tab.lbl_buffers = MagicMock()
    tab.lbl_creation = MagicMock()
    tab.lbl_dialect = MagicMock()
    tab.lbl_force_write = MagicMock()
    tab.lbl_generation = MagicMock()
    tab.lbl_health_summary = MagicMock()
    tab.lbl_next = MagicMock()
    tab.lbl_no_reserve = MagicMock()
    tab.lbl_ods = MagicMock()
    tab.lbl_oldest = MagicMock()
    tab.lbl_page_size = MagicMock()
    tab.lbl_snapshot = MagicMock()
    tab.lbl_sweep = MagicMock()

    tab.set_diagnostic_style = MagicMock()
    tab.update_health_check = MagicMock()
    tab.set_recommendations = MagicMock()
    tab.set_health_style = MagicMock()
    tab._clear_statistics = MagicMock()

    tab.refresh()

    tab.controller.statistics.assert_called_once_with()

    tab.controller.diagnostics.assert_called_once_with(
        stats
    )

    tab.controller.health.assert_called_once_with(
        stats
    )

    tab.controller.recommendations.assert_called_once_with(
        diagnostic
    )

    tab.set_recommendations.assert_called_once_with(
        recommendation_result.recommendations
    )
