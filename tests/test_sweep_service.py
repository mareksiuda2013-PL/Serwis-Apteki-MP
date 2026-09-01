from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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

    with pytest.raises(
        RuntimeError,
        match="ProcessRunner ERROR",
    ):

        service.sweep()


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_sweep_raises_when_firebird_installation_is_missing():

    with patch(
        "services.firebird.sweep_service.InstallationService"
    ) as installation_cls:

        installation_cls.return_value.first_installation.return_value = (
            None
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono Firebird",
        ):

            SweepService()


def test_sweep_raises_when_gfix_is_missing():

    installation = MagicMock()
    installation.gfix = None

    with patch(
        "services.firebird.sweep_service.InstallationService"
    ) as installation_cls:

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono gfix.exe",
        ):

            SweepService()


def test_sweep_uses_provided_database():

    database = Path(
        r"C:\test\database.fdb"
    )

    installation = MagicMock()
    installation.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    with (
        patch(
            "services.firebird.sweep_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.sweep_service.Config"
        ) as config_cls,
        patch(
            "services.firebird.sweep_service.ProcessRunner"
        ),
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        config_cls.return_value.database = (
            r"C:\configured\database.fdb"
        )

        service = SweepService(
            database=database
        )

    assert service.database == database


def test_sweep_uses_configured_database():

    configured_database = (
        r"C:\configured\database.fdb"
    )

    installation = MagicMock()
    installation.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    with (
        patch(
            "services.firebird.sweep_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.sweep_service.Config"
        ) as config_cls,
        patch(
            "services.firebird.sweep_service.ProcessRunner"
        ),
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        config_cls.return_value.database = (
            configured_database
        )

        service = SweepService()

    assert service.database == Path(
        configured_database
    )