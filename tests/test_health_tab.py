from types import SimpleNamespace
from unittest.mock import MagicMock

from modules.firebird.tabs.health_tab import HealthTab


def make_tab():
    with __import__("unittest").mock.patch.object(
        HealthTab,
        "__init__",
        return_value=None,
    ):
        tab = HealthTab.__new__(HealthTab)

    tab.controller = MagicMock()
    tab.status_label = MagicMock()
    tab.summary_label = MagicMock()
    tab.lbl_transactions = MagicMock()
    tab.lbl_force_write = MagicMock()
    tab.lbl_no_reserve = MagicMock()
    tab.refresh_button = MagicMock()

    return tab


def test_set_status_style_handles_error_warning_and_success():
    tab = make_tab()

    tab.set_status_style("ERROR")
    error_style = tab.status_label.setStyleSheet.call_args.args[0]

    tab.status_label.setStyleSheet.reset_mock()

    tab.set_status_style("WARNING")
    warning_style = tab.status_label.setStyleSheet.call_args.args[0]

    tab.status_label.setStyleSheet.reset_mock()

    tab.set_status_style("OK")
    success_style = tab.status_label.setStyleSheet.call_args.args[0]

    assert "#dc3545" in error_style
    assert "#ffc107" in warning_style
    assert "#28a745" in success_style


def test_format_check_returns_expected_text():
    tab = make_tab()

    check = SimpleNamespace(
        status="OK",
        value="100",
        message="Brak problemów",
    )

    assert tab.format_check(check) == (
        "OK | 100 | Brak problemów"
    )


def test_refresh_populates_health_information():
    tab = make_tab()

    health = SimpleNamespace(
        status="WARNING",
        summary="Wykryto ostrzeżenie",
        checks=[
            SimpleNamespace(
                name="Transakcje",
                status="OK",
                value="100",
                message="Brak problemów",
            ),
            SimpleNamespace(
                name="Force Write",
                status="OK",
                value="TAK",
                message="Włączone",
            ),
            SimpleNamespace(
                name="No Reserve",
                status="WARNING",
                value="NIE",
                message="Ustawienie zalecane",
            ),
        ],
    )

    tab.controller.health.return_value = health

    tab.refresh()

    tab.refresh_button.setEnabled.assert_any_call(False)
    tab.refresh_button.setEnabled.assert_any_call(True)

    tab.status_label.setText.assert_called_once_with("WARNING")
    tab.summary_label.setText.assert_called_once_with(
        "Wykryto ostrzeżenie"
    )

    tab.lbl_transactions.setText.assert_called_once_with(
        "OK | 100 | Brak problemów"
    )
    tab.lbl_force_write.setText.assert_called_once_with(
        "OK | TAK | Włączone"
    )
    tab.lbl_no_reserve.setText.assert_called_once_with(
        "WARNING | NIE | Ustawienie zalecane"
    )


def test_refresh_ignores_unknown_check():
    tab = make_tab()

    health = SimpleNamespace(
        status="OK",
        summary="Baza jest zdrowa",
        checks=[
            SimpleNamespace(
                name="Nieznana kontrola",
                status="OK",
                value="X",
                message="Test",
            ),
        ],
    )

    tab.controller.health.return_value = health

    tab.refresh()

    tab.status_label.setText.assert_called_once_with("OK")
    tab.summary_label.setText.assert_called_once_with(
        "Baza jest zdrowa"
    )

    tab.lbl_transactions.setText.assert_not_called()
    tab.lbl_force_write.setText.assert_not_called()
    tab.lbl_no_reserve.setText.assert_not_called()


def test_refresh_handles_controller_error_and_clears_checks():
    tab = make_tab()

    tab.controller.health.side_effect = RuntimeError(
        "test error"
    )

    tab.refresh()

    tab.status_label.setText.assert_called_once_with("ERROR")
    tab.summary_label.setText.assert_called_once_with(
        "Błąd kontroli bazy: test error"
    )

    tab.lbl_transactions.setText.assert_called_once_with("-")
    tab.lbl_force_write.setText.assert_called_once_with("-")
    tab.lbl_no_reserve.setText.assert_called_once_with("-")

    assert tab.refresh_button.setEnabled.call_args_list == [
        ((False,), {}),
        ((True,), {}),
    ]
