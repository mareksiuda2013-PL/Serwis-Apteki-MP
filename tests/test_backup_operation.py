from services.firebird.operation_service import (
    FirebirdOperationService,
)


def test_backup_operation_success():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: (
            True,
            "Backup OK",
        ),
        "BACKUP",
    )

    assert result.success is True
    assert result.message == "Backup OK"


def test_backup_operation_failure():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: (
            False,
            "Backup ERROR",
        ),
        "BACKUP",
    )

    assert result.success is False
    assert result.message == "Backup ERROR"