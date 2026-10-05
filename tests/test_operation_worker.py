from unittest.mock import Mock

from core.operation_worker import OperationWorker


def test_operation_worker_emits_finished_with_result():
    function = Mock(return_value="wynik")
    worker = OperationWorker(function)

    received = []
    worker.finished.connect(received.append)

    worker.run()

    function.assert_called_once_with()
    assert received == ["wynik"]


def test_operation_worker_emits_error_when_function_raises():
    function = Mock(side_effect=RuntimeError("Błąd testowy"))
    worker = OperationWorker(function)

    received = []
    worker.error.connect(received.append)

    worker.run()

    function.assert_called_once_with()
    assert received == ["Błąd testowy"]


def test_operation_worker_does_not_emit_error_on_success():
    function = Mock(return_value=123)
    worker = OperationWorker(function)

    finished = []
    errors = []

    worker.finished.connect(finished.append)
    worker.error.connect(errors.append)

    worker.run()

    assert finished == [123]
    assert errors == []
