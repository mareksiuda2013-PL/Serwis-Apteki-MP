from __future__ import annotations

from dataclasses import dataclass

from models.operation_result import OperationResult
from services.firebird.operation_service import (
    FirebirdOperationService,
)


def test_operation_success():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: True,
        "TEST",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is True
    assert (
        result.message
        == "Operacja zakończona pomyślnie."
    )


def test_operation_exception():

    service = FirebirdOperationService()

    def failing_operation():

        raise RuntimeError(
            "Testowy błąd"
        )

    result = service.execute(
        failing_operation,
        "TEST",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is False
    assert result.message == "Testowy błąd"
    assert result.error == "Testowy błąd"


def test_operation_tuple_success():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: (
            True,
            "Backup OK",
        ),
        "BACKUP",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is True
    assert result.message == "Backup OK"
    assert result.output == "Backup OK"
    assert result.error == ""


def test_operation_tuple_failure():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: (
            False,
            "Backup ERROR",
        ),
        "BACKUP",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is False
    assert result.message == "Backup ERROR"
    assert result.error == "Backup ERROR"


@dataclass
class FakeProcessResult:

    success: bool
    stdout: str = ""
    stderr: str = ""
    command: str = ""
    exit_code: int = 0
    started: object = None
    finished: object = None
    duration: float = 0.0


def test_operation_process_success():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=True,
        stdout="Validation OK",
        command="gfix -validate",
        exit_code=0,
        duration=1.5,
    )

    result = service.execute(
        lambda: process_result,
        "VALIDATE",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is True
    assert result.message == "Validation OK"
    assert result.output == "Validation OK"
    assert result.error == ""
    assert result.command == "gfix -validate"
    assert result.exit_code == 0
    assert result.duration == 1.5


def test_operation_process_failure():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=False,
        stdout="",
        stderr="Validation ERROR",
        command="gfix -validate",
        exit_code=1,
        duration=2.0,
    )

    result = service.execute(
        lambda: process_result,
        "VALIDATE",
    )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is False
    assert result.message == "Validation ERROR"
    assert result.output == ""
    assert result.error == "Validation ERROR"
    assert result.command == "gfix -validate"
    assert result.exit_code == 1
    assert result.duration == 2.0


def test_operation_process_failure_uses_output_when_no_error():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=False,
        stdout="Process output",
        stderr="",
        command="gfix",
        exit_code=1,
    )

    result = service.execute(
        lambda: process_result,
        "VALIDATE",
    )

    assert result.success is False
    assert result.message == "Process output"
    assert result.output == "Process output"
    assert result.error == ""


def test_operation_process_uses_output_attribute():

    service = FirebirdOperationService()

    class Result:

        success = True
        stdout = ""
        stderr = ""
        output = "Alternative output"
        error = ""
        command = "TEST"
        exit_code = 0
        started = None
        finished = None
        duration = 0.5

    result = service.execute(
        lambda: Result(),
        "TEST",
    )

    assert result.success is True
    assert result.message == "Alternative output"
    assert result.output == "Alternative output"


def test_operation_copies_process_metadata():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=True,
        stdout="OK",
        command="TEST COMMAND",
        exit_code=7,
        started="START",
        finished="FINISH",
        duration=3.25,
    )

    result = service.execute(
        lambda: process_result,
        "TEST",
    )

    assert result.command == "TEST COMMAND"
    assert result.exit_code == 7
    assert result.started == "START"
    assert result.finished == "FINISH"
    assert result.duration == 3.25