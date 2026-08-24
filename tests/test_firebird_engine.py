from __future__ import annotations

from unittest.mock import MagicMock, patch

from models.operation_result import OperationResult
from services.firebird_engine import FirebirdEngine


# ==========================================================
# BACKUP
# ==========================================================


def test_engine_backup_success():

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_cls:

        service_cls.return_value.backup.return_value = (
            True,
            "Backup OK",
        )

        engine = FirebirdEngine()

        result = engine.backup(
            "C:/backup/test.fbk"
        )

    assert isinstance(
        result,
        OperationResult,
    )

    assert result.success is True
    assert result.message == "Backup OK"

    service_cls.return_value.backup.assert_called_once_with(
        "C:/backup/test.fbk"
    )


def test_engine_backup_failure():

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_cls:

        service_cls.return_value.backup.return_value = (
            False,
            "Backup ERROR",
        )

        engine = FirebirdEngine()

        result = engine.backup(
            "C:/backup/test.fbk"
        )

    assert result.success is False
    assert result.message == "Backup ERROR"


def test_engine_backup_exception():

    with patch(
        "services.firebird_engine.BackupService"
    ) as service_cls:

        service_cls.return_value.backup.side_effect = (
            RuntimeError("Backup exception")
        )

        engine = FirebirdEngine()

        result = engine.backup(
            "C:/backup/test.fbk"
        )

    assert result.success is False
    assert result.message == "Backup exception"
    assert result.error == "Backup exception"


# ==========================================================
# RESTORE
# ==========================================================


def test_engine_restore_success():

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.return_value = (
            True,
            "Restore OK",
        )

        engine = FirebirdEngine()

        result = engine.restore(
            "C:/backup/test.fbk",
            "C:/database/test.fdb",
        )

    assert result.success is True
    assert result.message == "Restore OK"

    service_cls.return_value.restore.assert_called_once_with(
        backup_file="C:/backup/test.fbk",
        database_file="C:/database/test.fdb",
        replace=True,
    )


def test_engine_restore_without_replace():

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.return_value = (
            True,
            "Restore OK",
        )

        engine = FirebirdEngine()

        result = engine.restore(
            "C:/backup/test.fbk",
            "C:/database/test.fdb",
            replace=False,
        )

    assert result.success is True

    service_cls.return_value.restore.assert_called_once_with(
        backup_file="C:/backup/test.fbk",
        database_file="C:/database/test.fdb",
        replace=False,
    )


def test_engine_restore_failure():

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.return_value = (
            False,
            "Restore ERROR",
        )

        engine = FirebirdEngine()

        result = engine.restore(
            "C:/backup/test.fbk",
            "C:/database/test.fdb",
        )

    assert result.success is False
    assert result.message == "Restore ERROR"


def test_engine_restore_exception():

    with patch(
        "services.firebird_engine.RestoreService"
    ) as service_cls:

        service_cls.return_value.restore.side_effect = (
            RuntimeError("Restore exception")
        )

        engine = FirebirdEngine()

        result = engine.restore(
            "C:/backup/test.fbk",
            "C:/database/test.fdb",
        )

    assert result.success is False
    assert result.message == "Restore exception"
    assert result.error == "Restore exception"


# ==========================================================
# VALIDATE
# ==========================================================


def test_engine_validate_success():

    process_result = MagicMock(
        success=True,
        stdout="Validation OK",
        stderr="",
        error="",
        command="gfix -validate",
        exit_code=0,
        started=None,
        finished=None,
        duration=1.5,
    )

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_cls:

        service_cls.return_value.validate.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.validate()

    assert result.success is True
    assert result.message == "Validation OK"
    assert result.output == "Validation OK"
    assert result.error == ""
    assert result.command == "gfix -validate"
    assert result.exit_code == 0
    assert result.duration == 1.5


def test_engine_validate_failure():

    process_result = MagicMock(
        success=False,
        stdout="",
        stderr="Validation ERROR",
        error="",
        command="gfix -validate",
        exit_code=1,
        started=None,
        finished=None,
        duration=2.0,
    )

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_cls:

        service_cls.return_value.validate.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.validate()

    assert result.success is False
    assert result.message == "Validation ERROR"
    assert result.error == "Validation ERROR"
    assert result.exit_code == 1


def test_engine_validate_exception():

    with patch(
        "services.firebird_engine.ValidateService"
    ) as service_cls:

        service_cls.return_value.validate.side_effect = (
            RuntimeError("Validate exception")
        )

        engine = FirebirdEngine()

        result = engine.validate()

    assert result.success is False
    assert result.message == "Validate exception"
    assert result.error == "Validate exception"


# ==========================================================
# SWEEP
# ==========================================================


def test_engine_sweep_success():

    process_result = MagicMock(
        success=True,
        stdout="Sweep OK",
        stderr="",
        error="",
        command="gfix -sweep",
        exit_code=0,
        started=None,
        finished=None,
        duration=1.0,
    )

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_cls:

        service_cls.return_value.sweep.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.sweep()

    assert result.success is True
    assert result.message == "Sweep OK"
    assert result.output == "Sweep OK"
    assert result.error == ""


def test_engine_sweep_failure():

    process_result = MagicMock(
        success=False,
        stdout="",
        stderr="Sweep ERROR",
        error="",
        command="gfix -sweep",
        exit_code=1,
        started=None,
        finished=None,
        duration=1.0,
    )

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_cls:

        service_cls.return_value.sweep.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.sweep()

    assert result.success is False
    assert result.message == "Sweep ERROR"
    assert result.error == "Sweep ERROR"


def test_engine_sweep_exception():

    with patch(
        "services.firebird_engine.SweepService"
    ) as service_cls:

        service_cls.return_value.sweep.side_effect = (
            RuntimeError("Sweep exception")
        )

        engine = FirebirdEngine()

        result = engine.sweep()

    assert result.success is False
    assert result.message == "Sweep exception"
    assert result.error == "Sweep exception"


# ==========================================================
# MEND
# ==========================================================


def test_engine_mend_success():

    process_result = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
        error="",
        command="gfix -mend",
        exit_code=0,
        started=None,
        finished=None,
        duration=3.0,
    )

    with patch(
        "services.firebird_engine.MendService"
    ) as service_cls:

        service_cls.return_value.mend.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.mend()

    assert result.success is True
    assert result.message == "MEND OK"
    assert result.output == "MEND OK"
    assert result.error == ""
    assert result.duration == 3.0


def test_engine_mend_failure():

    process_result = MagicMock(
        success=False,
        stdout="",
        stderr="MEND ERROR",
        error="",
        command="gfix -mend",
        exit_code=1,
        started=None,
        finished=None,
        duration=3.0,
    )

    with patch(
        "services.firebird_engine.MendService"
    ) as service_cls:

        service_cls.return_value.mend.return_value = (
            process_result
        )

        engine = FirebirdEngine()

        result = engine.mend()

    assert result.success is False
    assert result.message == "MEND ERROR"
    assert result.error == "MEND ERROR"


def test_engine_mend_exception():

    with patch(
        "services.firebird_engine.MendService"
    ) as service_cls:

        service_cls.return_value.mend.side_effect = (
            RuntimeError("MEND exception")
        )

        engine = FirebirdEngine()

        result = engine.mend()

    assert result.success is False
    assert result.message == "MEND exception"
    assert result.error == "MEND exception"


# ==========================================================
# PROCESS RESULT CONVERSION
# ==========================================================


def test_from_process_result_success():

    process_result = MagicMock(
        success=True,
        stdout="OUTPUT",
        stderr="",
        error="",
        command="TEST COMMAND",
        exit_code=0,
        started="START",
        finished="FINISH",
        duration=2.5,
    )

    result = FirebirdEngine._from_process_result(
        process_result
    )

    assert result.success is True
    assert result.message == "OUTPUT"
    assert result.output == "OUTPUT"
    assert result.error == ""
    assert result.command == "TEST COMMAND"
    assert result.exit_code == 0
    assert result.started == "START"
    assert result.finished == "FINISH"
    assert result.duration == 2.5


def test_from_process_result_failure():

    process_result = MagicMock(
        success=False,
        stdout="OUTPUT",
        stderr="ERROR",
        error="",
        command="TEST COMMAND",
        exit_code=1,
        started="START",
        finished="FINISH",
        duration=2.5,
    )

    result = FirebirdEngine._from_process_result(
        process_result
    )

    assert result.success is False
    assert result.message == "ERROR"
    assert result.output == "OUTPUT"
    assert result.error == "ERROR"
    assert result.command == "TEST COMMAND"
    assert result.exit_code == 1


def test_from_process_result_uses_output_when_no_stderr():

    process_result = MagicMock(
        success=False,
        stdout="OUTPUT",
        stderr="",
        error="",
        command="TEST COMMAND",
        exit_code=1,
        started=None,
        finished=None,
        duration=0.0,
    )

    result = FirebirdEngine._from_process_result(
        process_result
    )

    assert result.success is False
    assert result.message == "OUTPUT"
    assert result.output == "OUTPUT"
    assert result.error == ""


def test_from_process_result_uses_output_attribute():

    process_result = MagicMock(
        success=True,
        stdout="",
        stderr="",
        error="",
        output="ALTERNATIVE OUTPUT",
        command="TEST COMMAND",
        exit_code=0,
        started=None,
        finished=None,
        duration=0.0,
    )

    result = FirebirdEngine._from_process_result(
        process_result
    )

    assert result.message == "ALTERNATIVE OUTPUT"
    assert result.output == "ALTERNATIVE OUTPUT"