from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from modules.firebird.page import FirebirdPage


def get_app():
    return QApplication.instance() or QApplication([])


def test_firebird_page_creates_controller_and_tabs():
    get_app()

    controller = MagicMock()
    information_tab = MagicMock()
    diagnostics_tab = MagicMock()
    operations_tab = MagicMock()

    with patch(
        "modules.firebird.page.FirebirdController",
        return_value=controller,
    ), patch(
        "modules.firebird.page.InformationTab",
        return_value=information_tab,
    ), patch(
        "modules.firebird.page.DiagnosticsTab",
        return_value=diagnostics_tab,
    ), patch(
        "modules.firebird.page.OperationsTab",
        return_value=operations_tab,
    ), patch(
        "modules.firebird.page.QVBoxLayout"
    ), patch(
        "modules.firebird.page.QTabWidget"
    ) as tab_widget_class:

        tabs = MagicMock()
        tab_widget_class.return_value = tabs

        page = FirebirdPage()

    assert page.controller is controller
    assert page.information_tab is information_tab
    assert page.diagnostics_tab is diagnostics_tab
    assert page.operations_tab is operations_tab

    tabs.addTab.assert_any_call(
        information_tab,
        "Informacje",
    )
    tabs.addTab.assert_any_call(
        diagnostics_tab,
        "Diagnostyka",
    )
    tabs.addTab.assert_any_call(
        operations_tab,
        "Operacje",
    )


def test_firebird_page_passes_same_controller_to_all_tabs():
    get_app()

    controller = MagicMock()

    with patch(
        "modules.firebird.page.FirebirdController",
        return_value=controller,
    ), patch(
        "modules.firebird.page.InformationTab"
    ) as information_class, patch(
        "modules.firebird.page.DiagnosticsTab"
    ) as diagnostics_class, patch(
        "modules.firebird.page.OperationsTab"
    ) as operations_class, patch(
        "modules.firebird.page.QVBoxLayout"
    ), patch(
        "modules.firebird.page.QTabWidget"
    ):

        FirebirdPage()

    information_class.assert_called_once_with(controller)
    diagnostics_class.assert_called_once_with(controller)
    operations_class.assert_called_once_with(controller)


def test_firebird_page_adds_tabs_in_expected_order():
    get_app()

    controller = MagicMock()
    information_tab = MagicMock()
    diagnostics_tab = MagicMock()
    operations_tab = MagicMock()

    with patch(
        "modules.firebird.page.FirebirdController",
        return_value=controller,
    ), patch(
        "modules.firebird.page.InformationTab",
        return_value=information_tab,
    ), patch(
        "modules.firebird.page.DiagnosticsTab",
        return_value=diagnostics_tab,
    ), patch(
        "modules.firebird.page.OperationsTab",
        return_value=operations_tab,
    ), patch(
        "modules.firebird.page.QVBoxLayout"
    ), patch(
        "modules.firebird.page.QTabWidget"
    ) as tab_widget_class:

        tabs = MagicMock()
        tab_widget_class.return_value = tabs

        FirebirdPage()

    assert tabs.addTab.call_args_list == [
        ((information_tab, "Informacje"), {}),
        ((diagnostics_tab, "Diagnostyka"), {}),
        ((operations_tab, "Operacje"), {}),
    ]
