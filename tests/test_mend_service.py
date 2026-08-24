from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from services.firebird.mend_service import MendService


def create_service():

    service = MendService.__new__(
        MendService
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    service.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    service.service = MagicMock()
    service.runner = MagicMock()

    return service


# ==========================================================
# SERVICE DISCOVERY
# ==========================================================


def test_mend_fails_when_firebird_service_not_found():

    service = create_service()

    service.service.find_firebird_service.return_value = None

    try:

        service.mend()

    except RuntimeError as exc:

        assert str(exc) == (
            "Nie znaleziono usługi Firebird."
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# SERVICE STATUS
# ==========================================================


def test_mend_fails_when_service_not_installed():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.return_value = (
        "Not Installed"
    )

    try:

        service.mend()

    except RuntimeError as exc:

        assert "Usługa Firebird nie istnieje" in str(exc)

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# STOP SERVICE
# ==========================================================


def test_mend_fails_when_service_cannot_be_stopped():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.return_value = (
        "Running"
    )

    service.service.stop.return_value = False

    try:

        service.mend()

    except RuntimeError as exc:

        assert "Nie udało się zatrzymać usługi Firebird" in str(exc)

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# MEND COMMAND
# ==========================================================


def test_mend_builds_correct_command():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.side_effect = [
        "Running",
        "Running",
    ]

    service.service.stop.return_value = True
    service.service.start.return_value = True

    process_result = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    service.runner.run.return_value = (
        process_result
    )

    # ValidateService jest tworzony wewnątrz mend().
    # Podstawiamy prosty mock przez moduł.
    import services.firebird.mend_service as module

    original_validate = module.ValidateService

    class FakeValidateService:

        def __init__(self, database=None):

            self.database = database

        def validate(self):

            return MagicMock(
                success=True,
                stdout="VALIDATION OK",
                stderr="",
            )

    module.ValidateService = FakeValidateService

    try:

        result = service.mend()

    finally:

        module.ValidateService = original_validate

    assert result is process_result

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gfix.exe",
        "-mend",
        "-full",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
    ]


# ==========================================================
# RUNNER OPTIONS
# ==========================================================


def test_mend_uses_correct_runner_options():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.side_effect = [
        "Running",
        "Running",
    ]

    service.service.stop.return_value = True
    service.service.start.return_value = True

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    import services.firebird.mend_service as module

    original_validate = module.ValidateService

    class FakeValidateService:

        def __init__(self, database=None):
            self.database = database

        def validate(self):
            return MagicMock(
                success=True,
                stdout="OK",
                stderr="",
            )

    module.ValidateService = FakeValidateService

    try:

        service.mend()

    finally:

        module.ValidateService = original_validate

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "MEND"


# ==========================================================
# VALIDATION FAILURE
# ==========================================================


def test_mend_fails_when_validation_fails():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.side_effect = [
        "Running",
        "Running",
    ]

    service.service.stop.return_value = True
    service.service.start.return_value = True

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    import services.firebird.mend_service as module

    original_validate = module.ValidateService

    class FakeValidateService:

        def __init__(self, database=None):
            self.database = database

        def validate(self):
            return MagicMock(
                success=False,
                stdout="",
                stderr="VALIDATION ERROR",
            )

    module.ValidateService = FakeValidateService

    try:

        try:

            service.mend()

        except RuntimeError as exc:

            assert (
                "walidacja po naprawie"
                in str(exc)
            )

        else:

            raise AssertionError(
                "Expected RuntimeError"
            )

    finally:

        module.ValidateService = original_validate


# ==========================================================
# SERVICE START FAILURE
# ==========================================================


def test_mend_fails_when_service_cannot_be_started():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.side_effect = [
        "Running",
        "Running",
        "Stopped",
    ]

    service.service.stop.return_value = True
    service.service.start.return_value = False

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    try:

        service.mend()

    except RuntimeError as exc:

        assert (
            "nie udało się uruchomić"
            in str(exc)
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# RUNNER EXCEPTION
# ==========================================================


def test_mend_restarts_service_after_exception():

    service = create_service()

    service.service.find_firebird_service.return_value = (
        "FirebirdServerDefaultInstance"
    )

    service.service.status.side_effect = [
        "Running",
        "Stopped",
    ]

    service.service.stop.return_value = True

    service.runner.run.side_effect = RuntimeError(
        "MEND ERROR"
    )

    try:

        service.mend()

    except RuntimeError as exc:

        assert str(exc) == "MEND ERROR"

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )

    service.service.start.assert_called()