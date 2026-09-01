from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from models.operation_result import OperationResult
from services.firebird.operation_service import (
    FirebirdOperationService,
)
from services.firebird_engine import FirebirdEngine


# ==========================================================
# HELPERS
# ==========================================================


def create_engine():

    operation_service = MagicMock(
        spec=FirebirdOperationService
    )

    engine = FirebirdEngine(
        operation_service=operation_service
    )

    return engine, operation_service


def get_operation(
    operation_service,
):
    return (
        operation_service
        .execute
        .call_args
        .args[0]
    )


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_engine_uses_provided_operation_service():

    operation_service = MagicMock(
        spec=FirebirdOperationService
    )

    engine = FirebirdEngine(
        operation_service=operation_service
    )

    assert (
        engine.operation_service
        is operation_service
    )


def test_engine_creates_default_operation_service():

    with patch(
        "services.firebird_engine.FirebirdOperationService"
    ) as service_cls:

        service = FirebirdEngine()

    service_cls.assert_called_once_with()

    assert engine_service_matches(
        service,
        service_cls.return_value,
    )


def engine_service_matches(
    engine,
    expected,
):
    return (
        engine.operation_service
        is expected
    )


# ==========================================================
# BACKUP
# ==========================================================


def test_engine_backup_delegates_to_operation_service():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Backup OK",
    )

    operation_service.execute.return_value = expected

    result = engine.backup(
        "C:/backup/test.fbk"
    )

    assert result is expected

    operation_service.execute.assert_called_once()

    name = (
        operation_service
        .execute
        .call_args
        .args[1]
    )

    assert name == "BACKUP"


def test_engine_backup_passes_destination():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    destination = Path(
        "C:/backup/test.fbk"
    )

    engine.backup(
        destination
    )

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_cls:

        service_cls.return_value.backup.return_value = (
            True,
            "Backup OK",
        )

        operation()

        service_cls.return_value.backup.assert_called_once_with(
            destination
        )


def test_engine_backup_accepts_string_destination():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    destination = "C:/backup/test.fbk"

    engine.backup(
        destination
    )

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_cls:

        service_cls.return_value.backup.return_value = (
            True,
            "Backup OK",
        )

        operation()

        service_cls.return_value.backup.assert_called_once_with(
            destination
        )


# ==========================================================
# RESTORE
# ==========================================================


def test_engine_restore_delegates_to_operation_service():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Restore OK",
    )

    operation_service.execute.return_value = expected

    result = engine.restore(
        "C:/backup/test.fbk",
        "C:/database/test.fdb",
    )

    assert result is expected

    operation_service.execute.assert_called_once()

    name = (
        operation_service
        .execute
        .call_args
        .args[1]
    )

    assert name == "RESTORE"


def test_engine_restore_passes_arguments():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    backup_file = Path(
        "C:/backup/test.fbk"
    )

    database_file = Path(
        "C:/database/test.fdb"
    )

    engine.restore(
        backup_file,
        database_file,
        replace=False,
    )

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.return_value = (
            True,
            "Restore OK",
        )

        operation()

        service_cls.return_value.restore.assert_called_once_with(
            backup_file=backup_file,
            database_file=database_file,
            replace=False,
        )


def test_engine_restore_defaults_replace_to_true():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    backup_file = Path(
        "C:/backup/test.fbk"
    )

    database_file = Path(
        "C:/database/test.fdb"
    )

    engine.restore(
        backup_file,
        database_file,
    )

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.return_value = (
            True,
            "Restore OK",
        )

        operation()

        service_cls.return_value.restore.assert_called_once_with(
            backup_file=backup_file,
            database_file=database_file,
            replace=True,
        )


# ==========================================================
# VALIDATE
# ==========================================================


def test_engine_validate_delegates_to_operation_service():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Validation OK",
    )

    operation_service.execute.return_value = expected

    result = engine.validate()

    assert result is expected

    operation_service.execute.assert_called_once()

    name = (
        operation_service
        .execute
        .call_args
        .args[1]
    )

    assert name == "VALIDATE"


def test_engine_validate_calls_validate_service():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    engine.validate()

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_cls:

        service_cls.return_value.validate.return_value = (
            MagicMock(
                success=True,
                stdout="Validation OK",
                stderr="",
            )
        )

        operation()

        service_cls.return_value.validate.assert_called_once_with()


# ==========================================================
# SWEEP
# ==========================================================


def test_engine_sweep_delegates_to_operation_service():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Sweep OK",
    )

    operation_service.execute.return_value = expected

    result = engine.sweep()

    assert result is expected

    operation_service.execute.assert_called_once()

    name = (
        operation_service
        .execute
        .call_args
        .args[1]
    )

    assert name == "SWEEP"


def test_engine_sweep_calls_sweep_service():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    engine.sweep()

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_cls:

        service_cls.return_value.sweep.return_value = (
            MagicMock(
                success=True,
                stdout="Sweep OK",
                stderr="",
            )
        )

        operation()

        service_cls.return_value.sweep.assert_called_once_with()


# ==========================================================
# MEND
# ==========================================================


def test_engine_mend_delegates_to_operation_service():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="MEND OK",
    )

    operation_service.execute.return_value = expected

    result = engine.mend()

    assert result is expected

    operation_service.execute.assert_called_once()

    name = (
        operation_service
        .execute
        .call_args
        .args[1]
    )

    assert name == "MEND"


def test_engine_mend_calls_mend_service():

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    engine.mend()

    operation = get_operation(
        operation_service
    )

    with patch(
        "services.firebird_engine.MendService"
    ) as service_cls:

        service_cls.return_value.mend.return_value = (
            MagicMock(
                success=True,
                stdout="MEND OK",
                stderr="",
            )
        )

        operation()

        service_cls.return_value.mend.assert_called_once_with()


# ==========================================================
# OPERATION NAMES
# ==========================================================


@pytest.mark.parametrize(
    "method,expected_name",
    [
        ("validate", "VALIDATE"),
        ("sweep", "SWEEP"),
        ("mend", "MEND"),
    ],
)
def test_engine_uses_correct_operation_name(
    method,
    expected_name,
):

    engine, operation_service = create_engine()

    operation_service.execute.return_value = (
        OperationResult(
            success=True
        )
    )

    getattr(engine, method)()

    assert (
        operation_service
        .execute
        .call_args
        .args[1]
        == expected_name
    )


# ==========================================================
# RESULT PASSTHROUGH
# ==========================================================


def test_engine_returns_operation_service_result_unchanged():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=False,
        message="Operation ERROR",
        error="Operation ERROR",
    )

    operation_service.execute.return_value = expected

    result = engine.validate()

    assert result is expected