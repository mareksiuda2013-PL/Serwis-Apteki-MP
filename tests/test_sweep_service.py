from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from services.firebird.sweep_service import SweepService


def create_service():

    service = SweepService.__new__(
        SweepService
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


def test_sweep_success():

    service = create_service()

    expected = MagicMock(
        success=True,
        stdout="Sweep OK",
        stderr="",
    )

    service.runner.run.return_value = expected

    result = service.sweep()

    assert result is expected


# ==========================================================
# FAILURE
# ==========================================================


def test_sweep_failure():

    service = create_service()

    expected = MagicMock(
        success=False,
        stdout="",
        stderr="Sweep ERROR",
    )

    service.runner.run.return_value = expected

    result = service.sweep()

    assert result is expected


# ==========================================================
# COMMAND
# ==========================================================


def test_sweep_builds_correct_command():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.sweep()

    service.runner.run.assert_called_once()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gfix.exe",
        "-sweep",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
    ]


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_sweep_uses_correct_runner_options():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.sweep()

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["operation"] == "SWEEP"


# ==========================================================
# DATABASE
# ==========================================================


def test_sweep_uses_configured_database():

    service = create_service()

    service.database = Path(
        r"C:\test\database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.sweep()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert (
        r"C:\test\database.fdb"
        in command
    )


# ==========================================================
# CREDENTIALS
# ==========================================================


def test_sweep_uses_configured_credentials():

    service = create_service()

    service.cfg.user = "TESTUSER"
    service.cfg.password = "TESTPASSWORD"

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.sweep()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert "TESTUSER" in command
    assert "TESTPASSWORD" in command


# ==========================================================
# RUNNER EXCEPTION
# ==========================================================


def test_sweep_propagates_runner_exception():

    service = create_service()

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    try:

        service.sweep()

    except RuntimeError as exc:

        assert str(exc) == (
            "ProcessRunner ERROR"
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )