from services.firebird.operation_service import (
    FirebirdOperationService,
)


def test_operation_success():

    service = FirebirdOperationService()

    result = service.execute(
        lambda: True,
        "TEST",
    )

    assert result.success is True


def test_operation_exception():

    service = FirebirdOperationService()

    def failing_operation():

        raise RuntimeError(
            "Testowy błąd"
        )

    result = service.execute(
        failing_operation,
        "TEST",
    )

    assert result.success is False
    assert "Testowy błąd" in result.message


def test_operation_tuple_result():

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