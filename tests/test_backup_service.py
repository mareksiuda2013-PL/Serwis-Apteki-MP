from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from services.firebird.backup_service import BackupService


def create_service():

    service = BackupService.__new__(
        BackupService
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    service.gbak = Path(
        r"C:\Firebird\gbak.exe"
    )

    service.runner = MagicMock()

    return service


# ==========================================================
# SUCCESS
# ==========================================================


def test_backup_success(tmp_path):

    service = create_service()

    expected = MagicMock(
        success=True,
        stdout="Backup OK",
        stderr="",
    )

    service.runner.run.return_value = expected

    destination = (
        tmp_path / "backup.fbk"
    )

    result = service.backup(
        destination
    )

    assert result == (
        True,
        "Backup OK",
    )


# ==========================================================
# FAILURE
# ==========================================================


def test_backup_failure(tmp_path):

    service = create_service()

    expected = MagicMock(
        success=False,
        stdout="",
        stderr="Backup ERROR",
    )

    service.runner.run.return_value = expected

    destination = (
        tmp_path / "backup.fbk"
    )

    result = service.backup(
        destination
    )

    assert result == (
        False,
        "Backup ERROR",
    )


# ==========================================================
# COMMAND
# ==========================================================


def test_backup_builds_correct_command(tmp_path):

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = (
        tmp_path / "backup.fbk"
    )

    service.backup(destination)

    command = (
        service.runner
        .run
        .call_args.args[0]
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
        str(destination),
    ]


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_backup_uses_correct_runner_options(tmp_path):

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = (
        tmp_path / "backup.fbk"
    )

    service.backup(destination)

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "BACKUP"


# ==========================================================
# DATABASE
# ==========================================================


def test_backup_uses_configured_database(tmp_path):

    service = create_service()

    service.database = Path(
        r"C:\test\database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = (
        tmp_path / "backup.fbk"
    )

    service.backup(destination)

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


def test_backup_uses_configured_credentials(tmp_path):

    service = create_service()

    service.cfg.user = "TESTUSER"
    service.cfg.password = "TESTPASSWORD"

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    destination = (
        tmp_path / "backup.fbk"
    )

    service.backup(destination)

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert "TESTUSER" in command
    assert "TESTPASSWORD" in command


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
        / "nested"
        / "backup"
        / "test.fbk"
    )

    service.backup(destination)

    assert destination.parent.exists()


# ==========================================================
# RUNNER EXCEPTION
# ==========================================================


def test_backup_propagates_runner_exception(
    tmp_path,
):

    service = create_service()

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    destination = (
        tmp_path / "backup.fbk"
    )

    try:

        service.backup(destination)

    except RuntimeError as exc:

        assert str(exc) == (
            "ProcessRunner ERROR"
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_backup_raises_when_gbak_is_missing():

    with patch(
        "services.firebird.backup_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = BackupService.__new__(
            BackupService
        )

        service.installation = MagicMock()
        service.installation.gbak = None

        try:

            BackupService.__init__(
                service
            )

        except RuntimeError as exc:

            assert str(exc) == (
                "Nie znaleziono gbak.exe."
            )

        else:

            raise AssertionError(
                "Expected RuntimeError"
            )