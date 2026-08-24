from __future__ import annotations

from unittest.mock import patch

from models.operation_result import OperationResult
from services.firebird_engine import FirebirdEngine


def test_backup_delegates_to_backup_service():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_class:

        service_class.return_value.backup.return_value = (
            True,
            "Backup OK",
        )

        result = engine.backup(
            "C:/backup/test.fbk"
        )

        service_class.return_value.backup.assert_called_once_with(
            "C:/backup/test.fbk"
        )

        assert isinstance(
            result,
            OperationResult,
        )

        assert result.success is True
        assert result.message == "Backup OK"


def test_backup_returns_error_when_service_fails():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_class:

        service_class.return_value.backup.return_value = (
            False,
            "Backup ERROR",
        )

        result = engine.backup(
            "C:/backup/test.fbk"
        )

        assert result.success is False
        assert result.message == "Backup ERROR"


def test_backup_handles_exception():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_class:

        service_class.return_value.backup.side_effect = (
            RuntimeError("gbak error")
        )

        result = engine.backup(
            "C:/backup/test.fbk"
        )

        assert result.success is False
        assert result.error == "gbak error"


def test_restore_delegates_to_restore_service():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_class:

        service_class.return_value.restore.return_value = (
            True,
            "Restore OK",
        )

        result = engine.restore(
            "C:/backup/test.fbk",
            "C:/data/test.fdb",
            replace=True,
        )

        service_class.return_value.restore.assert_called_once_with(
            backup_file="C:/backup/test.fbk",
            database_file="C:/data/test.fdb",
            replace=True,
        )

        assert result.success is True
        assert result.message == "Restore OK"


def test_validate_delegates_to_validate_service():
    engine = FirebirdEngine()

    process_result = OperationResult(
        success=True,
        output="Validate OK",
    )

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_class:

        service_class.return_value.validate.return_value = (
            process_result
        )

        result = engine.validate()

        service_class.return_value.validate.assert_called_once()

        assert result.success is True
        assert result.output == "Validate OK"


def test_sweep_delegates_to_sweep_service():
    engine = FirebirdEngine()

    process_result = OperationResult(
        success=True,
        output="Sweep OK",
    )

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_class:

        service_class.return_value.sweep.return_value = (
            process_result
        )

        result = engine.sweep()

        service_class.return_value.sweep.assert_called_once()

        assert result.success is True
        assert result.output == "Sweep OK"


def test_mend_delegates_to_mend_service():
    engine = FirebirdEngine()

    process_result = OperationResult(
        success=True,
        output="MEND OK",
    )

    with patch(
        "services.firebird_engine.MendService"
    ) as service_class:

        service_class.return_value.mend.return_value = (
            process_result
        )

        result = engine.mend()

        service_class.return_value.mend.assert_called_once()

        assert result.success is True
        assert result.output == "MEND OK"


def test_validate_handles_exception():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_class:

        service_class.return_value.validate.side_effect = (
            RuntimeError("gfix error")
        )

        result = engine.validate()

        assert result.success is False
        assert result.error == "gfix error"


def test_sweep_handles_exception():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_class:

        service_class.return_value.sweep.side_effect = (
            RuntimeError("sweep error")
        )

        result = engine.sweep()

        assert result.success is False
        assert result.error == "sweep error"


def test_mend_handles_exception():
    engine = FirebirdEngine()

    with patch(
        "services.firebird_engine.MendService"
    ) as service_class:

        service_class.return_value.mend.side_effect = (
            RuntimeError("mend error")
        )

        result = engine.mend()

        assert result.success is False
        assert result.error == "mend error"