from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from services.firebird.backup_service import BackupService
from services.firebird.restore_service import RestoreService
from services.firebird.validate_service import ValidateService
from services.firebird.sweep_service import SweepService
from services.firebird.mend_service import MendService


# ==========================================================
# BACKUP
# ==========================================================


def test_backup_success(monkeypatch, tmp_path):

    service = object.__new__(BackupService)

    service.gbak = Path("gbak.exe")
    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        "C:/database/test.fdb"
    )

    runner = MagicMock()

    runner.run.return_value = MagicMock(
        success=True,
        stdout="Backup OK",
        stderr="",
    )

    service.runner = runner

    destination = (
        tmp_path / "backup" / "test.fbk"
    )

    success, message = service.backup(
        destination
    )

    assert success is True
    assert message == "Backup OK"

    runner.run.assert_called_once()

    command = runner.run.call_args.args[0]

    assert "-b" in command
    assert "-g" in command
    assert "-v" in command
    assert str(destination) in command


def test_backup_failure(monkeypatch, tmp_path):

    service = object.__new__(BackupService)

    service.gbak = Path("gbak.exe")
    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        "C:/database/test.fdb"
    )

    runner = MagicMock()

    runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="Backup ERROR",
    )

    service.runner = runner

    destination = (
        tmp_path / "backup" / "test.fbk"
    )

    success, message = service.backup(
        destination
    )

    assert success is False
    assert message == "Backup ERROR"


# ==========================================================
# RESTORE
# ==========================================================


def create_restore_service():

    service = object.__new__(RestoreService)

    service.gbak = Path("gbak.exe")

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.runner = MagicMock()

    return service


def test_restore_missing_backup(tmp_path):

    service = create_restore_service()

    backup = (
        tmp_path / "missing.fbk"
    )

    database = (
        tmp_path / "database.fdb"
    )

    success, message = service.restore(
        backup,
        database,
    )

    assert success is False
    assert "Nie znaleziono backupu" in message


def test_restore_existing_database_without_replace(
    tmp_path,
):

    service = create_restore_service()

    backup = (
        tmp_path / "test.fbk"
    )

    backup.write_text(
        "backup"
    )

    database = (
        tmp_path / "database.fdb"
    )

    database.write_text(
        "database"
    )

    success, message = service.restore(
        backup,
        database,
        replace=False,
    )

    assert success is False
    assert "Baza już istnieje" in message


def test_restore_success(tmp_path):

    service = create_restore_service()

    backup = (
        tmp_path / "test.fbk"
    )

    backup.write_text(
        "backup"
    )

    database = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = (
        MagicMock(
            success=True,
            stdout="Restore OK",
            stderr="",
        )
    )

    success, message = service.restore(
        backup,
        database,
    )

    assert success is True
    assert (
        message
        == "Restore zakończony pomyślnie."
    )

    service.runner.run.assert_called_once()

    command = (
        service.runner.run
        .call_args.args[0]
    )

    assert "-c" in command
    assert "-v" in command
    assert "-rep" in command


def test_restore_failure(tmp_path):

    service = create_restore_service()

    backup = (
        tmp_path / "test.fbk"
    )

    backup.write_text(
        "backup"
    )

    database = (
        tmp_path / "database.fdb"
    )

    service.runner.run.return_value = (
        MagicMock(
            success=False,
            stdout="",
            stderr="Restore ERROR",
        )
    )

    success, message = service.restore(
        backup,
        database,
    )

    assert success is False
    assert message == "Restore ERROR"


# ==========================================================
# VALIDATE
# ==========================================================


def create_validate_service():

    service = object.__new__(
        ValidateService
    )

    service.gfix = Path("gfix.exe")

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        "C:/database/test.fdb"
    )

    service.runner = MagicMock()

    return service


def test_validate():

    service = create_validate_service()

    expected = MagicMock()

    service.runner.run.return_value = (
        expected
    )

    result = service.validate()

    assert result is expected

    service.runner.run.assert_called_once()

    command = (
        service.runner.run
        .call_args.args[0]
    )

    assert "-validate" in command
    assert "-full" in command
    assert str(service.database) in command


# ==========================================================
# SWEEP
# ==========================================================


def create_sweep_service():

    service = object.__new__(
        SweepService
    )

    service.gfix = Path("gfix.exe")

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        "C:/database/test.fdb"
    )

    service.runner = MagicMock()

    return service


def test_sweep():

    service = create_sweep_service()

    expected = MagicMock()

    service.runner.run.return_value = (
        expected
    )

    result = service.sweep()

    assert result is expected

    service.runner.run.assert_called_once()

    command = (
        service.runner.run
        .call_args.args[0]
    )

    assert "-sweep" in command
    assert str(service.database) in command


# ==========================================================
# MEND
# ==========================================================


def create_mend_service():

    service = object.__new__(
        MendService
    )

    service.gfix = Path("gfix.exe")

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        "C:/database/test.fdb"
    )

    service.service = MagicMock()
    service.runner = MagicMock()

    return service


def test_mend_success():

    service = create_mend_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.return_value = (
        "Running"
    )

    service.service.stop.return_value = True
    service.service.start.return_value = True

    mend_result = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    validation_result = MagicMock(
        success=True,
        stdout="Validation OK",
        stderr="",
    )

    service.runner.run.return_value = (
        mend_result
    )

    # ValidateService jest tworzony wewnątrz MendService,
    # dlatego podmieniamy jego metodę validate.
    original_validate = (
        ValidateService.validate
    )

    try:

        ValidateService.validate = (
            lambda self: validation_result
        )

        result = service.mend()

    finally:

        ValidateService.validate = (
            original_validate
        )

    assert result is mend_result

    service.service.stop.assert_called_once_with(
        "FirebirdServerDefaultInstance"
    )

    service.service.start.assert_called_once_with(
        "FirebirdServerDefaultInstance"
    )

    service.runner.run.assert_called_once()

    command = (
        service.runner.run
        .call_args.args[0]
    )

    assert "-mend" in command
    assert "-full" in command


def test_mend_service_not_found():

    service = create_mend_service()

    service.service.find_firebird_service.return_value = (
        None
    )

    with pytest.raises(
        RuntimeError,
        match="Nie znaleziono usługi Firebird",
    ):

        service.mend()


def test_mend_stop_failure():

    service = create_mend_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.return_value = (
        "Running"
    )

    service.service.stop.return_value = False

    with pytest.raises(
        RuntimeError,
        match="Nie udało się zatrzymać usługi",
    ):

        service.mend()