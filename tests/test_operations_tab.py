from __future__ import annotations

from unittest.mock import MagicMock, patch

from modules.firebird.tabs.operations_tab import OperationsTab


def test_start_operation_passes_operation_configuration():

    tab = OperationsTab.__new__(
        OperationsTab
    )

    operation = MagicMock()

    tab.run_async_operation = MagicMock()

    tab._start_operation(
        operation=operation,
        name="BACKUP",
        success_text="Backup zakończony pomyślnie.",
        error_text="Backup zakończony błędem.",
        dialog_title="Backup",
        warning_on_failure=True,
    )

    assert tab._success_text == (
        "Backup zakończony pomyślnie."
    )

    assert tab._error_text == (
        "Backup zakończony błędem."
    )

    assert tab._dialog_title == "Backup"

    assert tab._warning_on_failure is True

    tab.run_async_operation.assert_called_once_with(
        operation=operation,
        name="BACKUP",
        success_text="Backup zakończony pomyślnie.",
        error_text="Backup zakończony błędem.",
        dialog_title="Backup",
        warning_on_failure=True,
    )


def test_run_async_operation_does_not_start_when_operation_is_running():

    tab = OperationsTab.__new__(OperationsTab)

    thread = MagicMock()
    thread.isRunning.return_value = True

    tab._thread = thread
    tab.operation_started = MagicMock()

    tab.run_async_operation(
        operation=MagicMock(),
        name="BACKUP",
        success_text="OK",
        error_text="BŁĄD",
        dialog_title="Backup",
    )

    thread.isRunning.assert_called_once_with()
    tab.operation_started.assert_not_called()


def test_run_async_operation_starts_worker_thread():

    tab = OperationsTab.__new__(OperationsTab)

    tab._thread = None
    tab._worker = None
    tab.operation_started = MagicMock()

    fake_thread = MagicMock()
    fake_worker = MagicMock()
    fake_service = MagicMock()

    with (
        patch(
            "modules.firebird.tabs.operations_tab.QThread",
            return_value=fake_thread,
        ),
        patch(
            "modules.firebird.tabs.operations_tab.OperationWorker",
            return_value=fake_worker,
        ),
        patch(
            "modules.firebird.tabs.operations_tab.FirebirdOperationService",
            return_value=fake_service,
        ),
    ):

        operation = MagicMock()

        tab.run_async_operation(
            operation=operation,
            name="BACKUP",
            success_text="OK",
            error_text="BŁĄD",
            dialog_title="Backup",
        )

    fake_service.execute.assert_not_called()

    fake_worker.moveToThread.assert_called_once_with(
        fake_thread
    )

    fake_thread.start.assert_called_once_with()

    assert tab._worker is fake_worker
    assert tab._thread is fake_thread

def test_operation_result_success_shows_information_message():

    tab = OperationsTab.__new__(OperationsTab)

    result = MagicMock()
    result.success = True
    result.message = "Backup wykonany."

    tab._success_text = "Backup zako?czony pomy?lnie."
    tab._dialog_title = "Backup"
    tab.operation_finished = MagicMock()

    with patch(
        "modules.firebird.tabs.operations_tab.QMessageBox.information"
    ) as information:

        tab._operation_result(result)

    tab.operation_finished.assert_called_once_with(
        "Backup zako?czony pomy?lnie.",
        "success",
    )

    information.assert_called_once_with(
        tab,
        "Backup",
        "Backup wykonany.",
    )

def test_operation_result_failure_with_warning_shows_warning_message():

    tab = OperationsTab.__new__(OperationsTab)

    result = MagicMock()
    result.success = False
    result.message = "Wykryto problemy."

    tab._error_text = "Walidacja zako?czona b??dem."
    tab._dialog_title = "Walidacja"
    tab._warning_on_failure = True
    tab.operation_finished = MagicMock()

    with (
        patch(
            "modules.firebird.tabs.operations_tab.QMessageBox.warning"
        ) as warning,
        patch(
            "modules.firebird.tabs.operations_tab.QMessageBox.critical"
        ) as critical,
    ):

        tab._operation_result(result)

    tab.operation_finished.assert_called_once_with(
        "Walidacja zako?czona b??dem.",
        "warning",
    )

    warning.assert_called_once_with(
        tab,
        "Walidacja",
        "Wykryto problemy.",
    )

    critical.assert_not_called()

def test_operation_result_failure_without_warning_shows_critical_message():

    tab = OperationsTab.__new__(OperationsTab)

    result = MagicMock()
    result.success = False
    result.message = "B??d odtwarzania bazy."

    tab._error_text = "Restore zako?czony b??dem."
    tab._dialog_title = "Restore"
    tab._warning_on_failure = False
    tab.operation_finished = MagicMock()

    with (
        patch(
            "modules.firebird.tabs.operations_tab.QMessageBox.critical"
        ) as critical,
        patch(
            "modules.firebird.tabs.operations_tab.QMessageBox.warning"
        ) as warning,
    ):

        tab._operation_result(result)

    tab.operation_finished.assert_called_once_with(
        "Restore zako?czony b??dem.",
        "error",
    )

    critical.assert_called_once_with(
        tab,
        "Restore",
        "B??d odtwarzania bazy.",
    )

    warning.assert_not_called()

def test_operation_error_enables_operations_sets_error_status_and_shows_message():

    tab = OperationsTab.__new__(OperationsTab)

    tab.set_operations_enabled = MagicMock()
    tab.set_status = MagicMock()

    message = "Wyj?tek podczas wykonywania operacji."

    with (
        patch(
            "modules.firebird.tabs.operations_tab.logger.error"
        ) as logger_error,
        patch(
            "modules.firebird.tabs.operations_tab.QMessageBox.critical"
        ) as critical,
    ):

        tab._operation_error(message)

    tab.set_operations_enabled.assert_called_once_with(True)

    tab.set_status.assert_called_once_with(
        "B\u0142\u0105d operacji.",
        "error",
    )

    logger_error.assert_called_once_with(
        f"OPERATION ERROR: {message}"
    )

    critical.assert_called_once()
    critical_args = critical.call_args.args

    assert critical_args[0] is tab
    assert critical_args[1] == "B\u0142\u0105d operacji"
    assert critical_args[2] == message

def test_thread_finished_clears_worker_and_thread():

    tab = OperationsTab.__new__(OperationsTab)

    tab._worker = MagicMock()
    tab._thread = MagicMock()

    tab._thread_finished()

    assert tab._worker is None
    assert tab._thread is None

def test_set_operations_enabled_updates_all_operation_buttons():

    tab = OperationsTab.__new__(OperationsTab)

    tab.backup_button = MagicMock()
    tab.validate_button = MagicMock()
    tab.sweep_button = MagicMock()
    tab.restore_button = MagicMock()
    tab.mend_button = MagicMock()

    tab.set_operations_enabled(False)

    tab.backup_button.setEnabled.assert_called_once_with(False)
    tab.validate_button.setEnabled.assert_called_once_with(False)
    tab.sweep_button.setEnabled.assert_called_once_with(False)
    tab.restore_button.setEnabled.assert_called_once_with(False)
    tab.mend_button.setEnabled.assert_called_once_with(False)

def test_set_status_sets_text_and_success_style():

    tab = OperationsTab.__new__(OperationsTab)

    tab.status = MagicMock()

    tab.set_status(
        "Operacja zako?czona.",
        "success",
    )

    tab.status.setText.assert_called_once_with(
        "Operacja zako?czona."
    )

    stylesheet = tab.status.setStyleSheet.call_args.args[0]

    assert "#28a745" in stylesheet
    assert "#ffffff" in stylesheet

def test_set_status_uses_normal_style_for_unknown_color():

    tab = OperationsTab.__new__(OperationsTab)

    tab.status = MagicMock()

    tab.set_status(
        "Nieznany status.",
        "unknown",
    )

    tab.status.setText.assert_called_once_with(
        "Nieznany status."
    )

    stylesheet = tab.status.setStyleSheet.call_args.args[0]

    assert "#e9ecef" in stylesheet
    assert "#202020" in stylesheet

def test_operation_started_disables_operations_sets_info_status_and_logs():

    tab = OperationsTab.__new__(OperationsTab)

    tab.set_operations_enabled = MagicMock()
    tab.set_status = MagicMock()

    with patch(
        "modules.firebird.tabs.operations_tab.logger.info"
    ) as logger_info:

        tab.operation_started(
            "Trwa operacja BACKUP..."
        )

    tab.set_operations_enabled.assert_called_once_with(False)

    tab.set_status.assert_called_once_with(
        "Trwa operacja BACKUP...",
        "info",
    )

    logger_info.assert_called_once_with(
        "Trwa operacja BACKUP..."
    )

def test_operation_finished_enables_operations_sets_status_logs_and_refreshes():

    tab = OperationsTab.__new__(OperationsTab)

    tab.set_operations_enabled = MagicMock()
    tab.set_status = MagicMock()
    tab.refresh_database = MagicMock()

    with patch(
        "modules.firebird.tabs.operations_tab.logger.info"
    ) as logger_info:

        tab.operation_finished(
            "Backup zako?czony.",
            "success",
        )

    tab.set_operations_enabled.assert_called_once_with(True)

    tab.set_status.assert_called_once_with(
        "Backup zako?czony.",
        "success",
    )

    logger_info.assert_called_once_with(
        "Backup zako?czony."
    )

    tab.refresh_database.assert_called_once_with()

def test_refresh_database_calls_controller_info():

    tab = OperationsTab.__new__(OperationsTab)

    tab.controller = MagicMock()

    tab.refresh_database()

    tab.controller.info.assert_called_once_with()


def test_refresh_database_logs_controller_error():

    tab = OperationsTab.__new__(OperationsTab)

    error = RuntimeError("B??d po??czenia z baz?.")

    tab.controller = MagicMock()
    tab.controller.info.side_effect = error

    with patch(
        "modules.firebird.tabs.operations_tab.logger.error"
    ) as logger_error:

        tab.refresh_database()

    logger_error.assert_called_once_with(
        f"B\u0142\u0105d od\u015bwie\u017cania informacji Firebird: {error}"
    )

