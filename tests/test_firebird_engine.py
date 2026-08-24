from __future__ import annotations

from unittest.mock import MagicMock, patch

from models.operation_result import OperationResult
from services.firebird_engine import FirebirdEngine


def create_engine():

    operation_service = MagicMock()

    engine = FirebirdEngine(
        operation_service=operation_service
    )

    return engine, operation_service


# ==========================================================
# BACKUP
# ==========================================================


def test_engine_backup():

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

    _, name = operation_service.execute.call_args.args

    assert name == "BACKUP"


def test_engine_backup_executes_service():

    engine, operation_service = create_engine()

    def execute(operation, name):

        assert name == "BACKUP"

        with patch(
            "services.firebird_engine.BackupService"
        ) as service_cls:

            service_cls.return_value.backup.return_value = (
                True,
                "Backup OK",
            )

            result = operation()

            service_cls.return_value.backup.assert_called_once_with(
                "C:/backup/test.fbk"
            )

        return OperationResult(
            success=result[0],
            message=result[1],
        )

    operation_service.execute.side_effect = execute

    result = engine.backup(
        "C:/backup/test.fbk"
    )

    assert result.success is True
    assert result.message == "Backup OK"


# ==========================================================
# RESTORE
# ==========================================================


def test_engine_restore():

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

    _, name = operation_service.execute.call_args.args

    assert name == "RESTORE"


def test_engine_restore_passes_arguments():

    engine, operation_service = create_engine()

    def execute(operation, name):

        assert name == "RESTORE"

        with patch(
            "services.firebird_engine.RestoreService"
        ) as service_cls:

            service_cls.return_value.restore.return_value = (
                True,
                "Restore OK",
            )

            result = operation()

            service_cls.return_value.restore.assert_called_once_with(
                backup_file="C:/backup/test.fbk",
                database_file="C:/database/test.fdb",
                replace=False,
            )

        return OperationResult(
            success=result[0],
            message=result[1],
        )

    operation_service.execute.side_effect = execute

    result = engine.restore(
        "C:/backup/test.fbk",
        "C:/database/test.fdb",
        replace=False,
    )

    assert result.success is True


# ==========================================================
# VALIDATE
# ==========================================================


def test_engine_validate():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Validation OK",
    )

    operation_service.execute.return_value = expected

    result = engine.validate()

    assert result is expected

    operation_service.execute.assert_called_once()

    _, name = operation_service.execute.call_args.args

    assert name == "VALIDATE"


def test_engine_validate_executes_service():

    engine, operation_service = create_engine()

    def execute(operation, name):

        assert name == "VALIDATE"

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

            result = operation()

            service_cls.return_value.validate.assert_called_once_with()

        return OperationResult(
            success=True,
            message=result.stdout,
            output=result.stdout,
        )

    operation_service.execute.side_effect = execute

    result = engine.validate()

    assert result.success is True
    assert result.message == "Validation OK"


# ==========================================================
# SWEEP
# ==========================================================


def test_engine_sweep():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="Sweep OK",
    )

    operation_service.execute.return_value = expected

    result = engine.sweep()

    assert result is expected

    operation_service.execute.assert_called_once()

    _, name = operation_service.execute.call_args.args

    assert name == "SWEEP"


def test_engine_sweep_executes_service():

    engine, operation_service = create_engine()

    def execute(operation, name):

        assert name == "SWEEP"

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

            result = operation()

            service_cls.return_value.sweep.assert_called_once_with()

        return OperationResult(
            success=True,
            message=result.stdout,
            output=result.stdout,
        )

    operation_service.execute.side_effect = execute

    result = engine.sweep()

    assert result.success is True
    assert result.message == "Sweep OK"


# ==========================================================
# MEND
# ==========================================================


def test_engine_mend():

    engine, operation_service = create_engine()

    expected = OperationResult(
        success=True,
        message="MEND OK",
    )

    operation_service.execute.return_value = expected

    result = engine.mend()

    assert result is expected

    operation_service.execute.assert_called_once()

    _, name = operation_service.execute.call_args.args

    assert name == "MEND"


def test_engine_mend_executes_service():

    engine, operation_service = create_engine()

    def execute(operation, name):

        assert name == "MEND"

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

            result = operation()

            service_cls.return_value.mend.assert_called_once_with()

        return OperationResult(
            success=True,
            message=result.stdout,
            output=result.stdout,
        )

    operation_service.execute.side_effect = execute

    result = engine.mend()

    assert result.success is True
    assert result.message == "MEND OK"


# ==========================================================
# INJECTION
# ==========================================================


def test_engine_accepts_operation_service():

    operation_service = MagicMock()

    engine = FirebirdEngine(
        operation_service=operation_service
    )

    assert engine.operation_service is operation_service


def test_engine_creates_operation_service():

    engine = FirebirdEngine()

    assert engine.operation_service is not None