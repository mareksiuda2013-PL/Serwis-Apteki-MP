from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.restore_service import RestoreService


def create_service():

    service = RestoreService.__new__(
        RestoreService
    )

    service.gbak = Path(
        r"C:\Firebird\gbak.exe"
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.runner = MagicMock()

    return service


# ==========================================================
# BACKUP FILE
# ==========================================================


def test_restore_fails_when_backup_does_not_exist(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "missing.fbk"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result[0] is False

    assert "Nie znaleziono backupu" in result[1]

    service.runner.run.assert_not_called()


def test_restore_fails_when_backup_is_directory(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup"
    )

    backup_file.mkdir()

    database_file = (
        tmp_path / "database.fdb"
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result[0] is False

    assert (
        "nie jest plikiem"
        in result[1]
    )

    service.runner.run.assert_not_called()


# ==========================================================
# TARGET DATABASE
# ==========================================================


def test_restore_fails_when_database_exists_and_replace_false(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    database_file.write_text(
        "database"
    )

    result = service.restore(
        backup_file,
        database_file,
        replace=False,
    )

    assert result[0] is False

    assert (
        "Baza już istnieje"
        in result[1]
    )

    service.runner.run.assert_not_called()


# ==========================================================
# TARGET DIRECTORY
# ==========================================================


def test_restore_creates_target_directory(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path
        / "new"
        / "folder"
        / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="Restore OK",
        stderr="",
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result[0] is True

    assert database_file.parent.exists()


# ==========================================================
# SUCCESS
# ==========================================================


def test_restore_success(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="Restore OK",
        stderr="",
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result == (
        True,
        "Restore zakończony pomyślnie.",
    )


# ==========================================================
# FAILURE
# ==========================================================


def test_restore_failure_uses_stderr(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="Restore ERROR",
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result[0] is False
    assert result[1] == "Restore ERROR"


def test_restore_failure_uses_stdout_when_stderr_empty(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="Restore failed",
        stderr="",
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result[0] is False
    assert result[1] == "Restore failed"


def test_restore_failure_uses_default_message(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="",
    )

    result = service.restore(
        backup_file,
        database_file,
    )

    assert result == (
        False,
        "Restore nie powiódł się.",
    )


# ==========================================================
# COMMAND
# ==========================================================


def test_restore_builds_correct_command(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.restore(
        backup_file,
        database_file,
    )

    service.runner.run.assert_called_once()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gbak.exe",
        "-c",
        "-v",
        "-rep",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
        str(backup_file),
        str(database_file),
    ]


def test_restore_without_replace_does_not_add_rep(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.restore(
        backup_file,
        database_file,
        replace=False,
    )

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert "-rep" not in command


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_restore_uses_correct_runner_options(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.restore(
        backup_file,
        database_file,
    )

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "RESTORE"


# ==========================================================
# EXCEPTION
# ==========================================================


def test_restore_propagates_runner_exception(
    tmp_path,
):

    service = create_service()

    backup_file = (
        tmp_path / "backup.fbk"
    )

    backup_file.write_text(
        "backup"
    )

    database_file = (
        tmp_path / "database.fdb"
    )

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="ProcessRunner ERROR",
    ):

        service.restore(
            backup_file,
            database_file,
        )


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_restore_raises_when_gbak_is_missing():

    with patch(
        "services.firebird.restore_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = RestoreService.__new__(
            RestoreService
        )

        service.installation = MagicMock()
        service.installation.gbak = None

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono gbak.exe.",
        ):

            RestoreService.__init__(
                service
            )