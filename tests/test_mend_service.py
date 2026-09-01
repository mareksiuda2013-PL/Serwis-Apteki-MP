from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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


def create_successful_validation():

    return MagicMock(
        success=True,
        stdout="VALIDATION OK",
        stderr="",
    )


# ==========================================================
# SERVICE DISCOVERY
# ==========================================================


def test_mend_fails_when_firebird_service_not_found():

    service = create_service()

    service.service.find_firebird_service.return_value = None

    with pytest.raises(
        RuntimeError,
        match="Nie znaleziono usługi Firebird",
    ):

        service.mend()


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

    with pytest.raises(
        RuntimeError,
        match="Usługa Firebird nie istnieje",
    ):

        service.mend()


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

    with pytest.raises(
        RuntimeError,
        match="Nie udało się zatrzymać usługi Firebird",
    ):

        service.mend()


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

    with patch(
        "services.firebird.mend_service.ValidateService"
    ) as validate_cls:

        validate_cls.return_value.validate.return_value = (
            create_successful_validation()
        )

        result = service.mend()

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

    with patch(
        "services.firebird.mend_service.ValidateService"
    ) as validate_cls:

        validate_cls.return_value.validate.return_value = (
            create_successful_validation()
        )

        service.mend()

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["timeout"] == 1800
    assert kwargs["operation"] == "MEND"


# ==========================================================
# VALIDATION
# ==========================================================


def test_mend_runs_validation_after_successful_mend():

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

    with patch(
        "services.firebird.mend_service.ValidateService"
    ) as validate_cls:

        validate_cls.return_value.validate.return_value = (
            create_successful_validation()
        )

        service.mend()

        validate_cls.assert_called_once_with(
            database=service.database
        )

        validate_cls.return_value.validate.assert_called_once_with()


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
        "Running",
    ]

    service.service.stop.return_value = True
    service.service.start.return_value = True

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="MEND OK",
        stderr="",
    )

    validation = MagicMock(
        success=False,
        stdout="",
        stderr="VALIDATION ERROR",
    )

    with patch(
        "services.firebird.mend_service.ValidateService"
    ) as validate_cls:

        validate_cls.return_value.validate.return_value = (
            validation
        )

        with pytest.raises(
            RuntimeError,
            match="walidacja po naprawie",
        ):

            service.mend()


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

    with pytest.raises(
        RuntimeError,
        match="nie udało się uruchomić",
    ):

        service.mend()


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

    with pytest.raises(
        RuntimeError,
        match="MEND ERROR",
    ):

        service.mend()

    service.service.start.assert_called()


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_mend_raises_when_firebird_installation_is_missing():

    with patch(
        "services.firebird.mend_service.InstallationService"
    ) as installation_cls:

        installation_cls.return_value.first_installation.return_value = (
            None
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono instalacji Firebird",
        ):

            MendService()


def test_mend_raises_when_gfix_is_missing():

    installation = MagicMock()
    installation.gfix = None

    with patch(
        "services.firebird.mend_service.InstallationService"
    ) as installation_cls:

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono gfix.exe",
        ):

            MendService()


def test_mend_uses_provided_database():

    database = Path(
        r"C:\test\database.fdb"
    )

    installation = MagicMock()
    installation.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    with (
        patch(
            "services.firebird.mend_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.mend_service.Config"
        ) as config_cls,
        patch(
            "services.firebird.mend_service.ServiceService"
        ),
        patch(
            "services.firebird.mend_service.ProcessRunner"
        ),
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        config_cls.return_value.database = (
            r"C:\configured\database.fdb"
        )

        service = MendService(
            database=database
        )

    assert service.database == database


def test_mend_uses_configured_database():

    installation = MagicMock()
    installation.gfix = Path(
        r"C:\Firebird\gfix.exe"
    )

    configured_database = (
        r"C:\configured\database.fdb"
    )

    with (
        patch(
            "services.firebird.mend_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.mend_service.Config"
        ) as config_cls,
        patch(
            "services.firebird.mend_service.ServiceService"
        ),
        patch(
            "services.firebird.mend_service.ProcessRunner"
        ),
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        config_cls.return_value.database = (
            configured_database
        )

        service = MendService()

    assert service.database == Path(
        configured_database
    )