from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from services.firebird.validate_service import ValidateService


def create_service():

    service = ValidateService.__new__(
        ValidateService
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    service.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    service.runner = MagicMock()

    return service


# ==========================================================
# SUCCESS
# ==========================================================


def test_validate_success():

    service = create_service()

    expected = MagicMock(
        success=True,
        stdout="Validation OK",
        stderr="",
    )

    service.runner.run.return_value = expected

    result = service.validate()

    assert result is expected


# ==========================================================
# FAILURE
# ==========================================================


def test_validate_failure():

    service = create_service()

    expected = MagicMock(
        success=False,
        stdout="",
        stderr="Validation ERROR",
    )

    service.runner.run.return_value = expected

    result = service.validate()

    assert result is expected


# ==========================================================
# COMMAND
# ==========================================================


def test_validate_builds_correct_command():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.validate()

    service.runner.run.assert_called_once()

    command = (
        service.runner.run.call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gfix.exe",
        "-validate",
        "-full",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
    ]


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_validate_uses_correct_runner_options():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.validate()

    kwargs = (
        service.runner.run.call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "VALIDATE"


# ==========================================================
# DATABASE
# ==========================================================


def test_validate_uses_configured_database():

    service = create_service()

    service.database = Path(
        r"C:\test\database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.validate()

    command = (
        service.runner.run.call_args.args[0]
    )

    assert (
        r"C:\test\database.fdb"
        in command
    )


# ==========================================================
# CREDENTIALS
# ==========================================================


def test_validate_uses_configured_credentials():

    service = create_service()

    service.cfg.user = "TESTUSER"
    service.cfg.password = "TESTPASSWORD"

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.validate()

    command = (
        service.runner.run.call_args.args[0]
    )

    assert "TESTUSER" in command
    assert "TESTPASSWORD" in command


# ==========================================================
# RUNNER EXCEPTION
# ==========================================================


def test_validate_propagates_runner_exception():

    service = create_service()

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    try:

        service.validate()

    except RuntimeError as exc:

        assert str(exc) == (
            "ProcessRunner ERROR"
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )