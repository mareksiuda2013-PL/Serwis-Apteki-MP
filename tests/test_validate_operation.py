from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from services.firebird.validate_service import ValidateService


# ==========================================================
# FACTORY
# ==========================================================


def create_service(
    database: str | Path | None = None,
):
    installation = MagicMock()
    installation.gfix = r"C:\Firebird\gfix.exe"

    with (
        patch(
            "services.firebird.validate_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.validate_service.ProcessRunner"
        ) as runner_cls,
    ):
        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        service = ValidateService(
            database=database
        )

        return (
            service,
            runner_cls.return_value,
            installation,
        )


# ==========================================================
# DATABASE
# ==========================================================


def test_validate_service_uses_configured_database():

    service, _, _ = create_service()

    assert service.database == Path(
        service.cfg.database
    )


def test_validate_service_accepts_custom_database():

    database = r"C:\test\database.fdb"

    service, _, _ = create_service(
        database=database
    )

    assert service.database == Path(
        database
    )


# ==========================================================
# GFIX
# ==========================================================


def test_validate_service_raises_when_gfix_missing():

    installation = MagicMock()
    installation.gfix = None

    with patch(
        "services.firebird.validate_service.InstallationService"
    ) as installation_cls:

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        try:
            ValidateService()

            assert False, (
                "ValidateService powinien zgłosić "
                "RuntimeError"
            )

        except RuntimeError as exc:

            assert "gfix.exe" in str(exc)


# ==========================================================
# COMMAND
# ==========================================================


def test_validate_builds_correct_command():

    service, runner, _ = create_service(
        database=r"C:\test\database.fdb"
    )

    result_mock = MagicMock()
    result_mock.success = True
    result_mock.stdout = "Validation successful"
    result_mock.stderr = ""

    runner.run.return_value = result_mock

    result = service.validate()

    runner.run.assert_called_once()

    command = runner.run.call_args.args[0]

    assert command[0] == (
        r"C:\Firebird\gfix.exe"
    )

    assert "-validate" in command
    assert "-full" in command

    assert r"C:\test\database.fdb" in command

    assert "-user" in command
    assert service.cfg.user in command

    assert "-password" in command
    assert service.cfg.password in command

    assert result.success is True


# ==========================================================
# SUCCESS
# ==========================================================


def test_validate_returns_success_result():

    service, runner, _ = create_service()

    expected = MagicMock()
    expected.success = True
    expected.stdout = "Validation successful"
    expected.stderr = ""

    runner.run.return_value = expected

    result = service.validate()

    assert result is expected
    assert result.success is True
    assert result.stdout == (
        "Validation successful"
    )


# ==========================================================
# FAILURE
# ==========================================================


def test_validate_returns_failed_result():

    service, runner, _ = create_service()

    expected = MagicMock()
    expected.success = False
    expected.stdout = ""
    expected.stderr = "Validation failed"

    runner.run.return_value = expected

    result = service.validate()

    assert result is expected
    assert result.success is False
    assert result.stderr == (
        "Validation failed"
    )