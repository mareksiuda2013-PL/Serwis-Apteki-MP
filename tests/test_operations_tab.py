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
