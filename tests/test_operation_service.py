from __future__ import annotations

from dataclasses import dataclass

from models.operation_result import OperationResult
from services.firebird.operation_service import (
    FirebirdOperationService,
)


# ==========================================================
# HELPERS
# ==========================================================


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


# ==========================================================
# STANDARD RESULT
# ==========================================================


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
    assert result.message == (
        "Operacja zakończona pomyślnie."
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


# ==========================================================
# TUPLE RESULT
# ==========================================================


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
    assert result.output == ""


# ==========================================================
# OPERATION RESULT PASSED THROUGH
# ==========================================================


def test_operation_result_is_returned_unchanged():

    service = FirebirdOperationService()

    expected = OperationResult(
        success=True,
        message="Already normalized",
        command="TEST",
        output="OUTPUT",
        error="",
        exit_code=0,
        duration=1.5,
    )

    result = service.execute(
        lambda: expected,
        "TEST",
    )

    assert result is expected


def test_failed_operation_result_is_returned_unchanged():

    service = FirebirdOperationService()

    expected = OperationResult(
        success=False,
        message="ERROR",
        output="",
        error="ERROR",
        command="TEST",
        exit_code=1,
    )

    result = service.execute(
        lambda: expected,
        "TEST",
    )

    assert result is expected


# ==========================================================
# PROCESS RESULT
# ==========================================================


def test_process_result_success():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=True,
        stdout="Validation OK",
        stderr="",
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


def test_process_result_failure():

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

    assert result.success is False
    assert result.message == "Validation ERROR"
    assert result.output == ""
    assert result.error == "Validation ERROR"
    assert result.command == "gfix -validate"
    assert result.exit_code == 1


def test_process_result_uses_output_when_stderr_empty():

    service = FirebirdOperationService()

    process_result = FakeProcessResult(
        success=False,
        stdout="Validation output",
        stderr="",
        command="gfix -validate",
        exit_code=1,
    )

    result = service.execute(
        lambda: process_result,
        "VALIDATE",
    )

    assert result.success is False
    assert result.message == "Validation output"
    assert result.output == "Validation output"
    assert result.error == ""


# ==========================================================
# OUTPUT ATTRIBUTE
# ==========================================================


def test_process_result_uses_output_attribute():

    service = FirebirdOperationService()

    class ResultWithOutput:

        success = True
        stdout = ""
        stderr = ""
        output = "Alternative output"
        command = "TEST"
        exit_code = 0
        started = None
        finished = None
        duration = 0.5

    result = service.execute(
        lambda: ResultWithOutput(),
        "TEST",
    )

    assert result.success is True
    assert result.message == "Alternative output"
    assert result.output == "Alternative output"
    assert result.error == ""