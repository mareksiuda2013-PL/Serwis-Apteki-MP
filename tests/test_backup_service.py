from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.backup_service import BackupService


# ==========================================================
# HELPERS
# ==========================================================


def create_service():

    with (
        patch(
            "services.firebird.backup_service.BaseFirebirdService.__init__",
            return_value=None,
        ),
        patch(
            "services.firebird.backup_service.BackupService.installation",
            create=True,
        ),
    ):

        service = BackupService.__new__(
            BackupService
        )

        service.installation = MagicMock()
        service.installation.gbak = Path(
            r"C:\Firebird\gbak.exe"
        )

        service.gbak = service.installation.gbak

        service.database = Path(
            r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
        )

        service.cfg = MagicMock()
        service.cfg.user = "SYSDBA"
        service.cfg.password = "masterkey"

        service.runner = MagicMock()

        return service


# ==========================================================
# BACKUP SUCCESS
# ==========================================================


def test_backup_success():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="Backup completed successfully.",
        stderr="",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result[0] is True

    assert (
        result[1]
        == "Backup completed successfully."
    )


# ==========================================================
# BACKUP FAILURE
# ==========================================================


def test_backup_failure_uses_stderr():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="Backup ERROR",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result[0] is False
    assert result[1] == "Backup ERROR"


def test_backup_failure_uses_stdout_when_stderr_empty():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="Backup failed.",
        stderr="",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result[0] is False
    assert result[1] == "Backup failed."


# ==========================================================
# DESTINATION DIRECTORY
# ==========================================================


def test_backup_creates_destination_directory(
    tmp_path,
):

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = (
        tmp_path
        / "backup"
        / "nested"
        / "test.fbk"
    )

    assert destination.parent.exists() is False

    service.backup(
        destination
    )

    assert destination.parent.exists() is True


# ==========================================================
# COMMAND
# ==========================================================


def test_backup_builds_correct_gbak_command():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = Path(
        r"C:\backup\test.fbk"
    )

    service.backup(
        destination
    )

    service.runner.run.assert_called_once()

    command = (
        service.runner.run.call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gbak.exe",
        "-b",
        "-g",
        "-v",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        r"C:\backup\test.fbk",
    ]


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_backup_uses_correct_runner_options():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.backup(
        r"C:\backup\test.fbk"
    )

    kwargs = (
        service.runner.run.call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "BACKUP"


# ==========================================================
# PATH TYPES
# ==========================================================


def test_backup_accepts_string_destination():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result[0] is True


def test_backup_accepts_path_destination():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    result = service.backup(
        Path(
            r"C:\backup\test.fbk"
        )
    )

    assert result[0] is True


# ==========================================================
# RUNNER EXCEPTION
# ==========================================================


def test_backup_propagates_runner_exception():

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
        service.backup(
            r"C:\backup\test.fbk"
        )


# ==========================================================
# EMPTY OUTPUT
# ==========================================================


def test_backup_success_with_empty_output():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="",
        stderr="",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result == (
        True,
        "",
    )


# ==========================================================
# NO STDERR / NO STDOUT
# ==========================================================


def test_backup_failure_with_empty_output():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="",
    )

    result = service.backup(
        r"C:\backup\test.fbk"
    )

    assert result == (
        False,
        "",
    )