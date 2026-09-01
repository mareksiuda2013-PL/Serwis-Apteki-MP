from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.statistics_service import (
    StatisticsService,
)


# ==========================================================
# FACTORIES
# ==========================================================


def installation_mock():

    installation = MagicMock()

    installation.install_path = Path(
        "C:/Firebird"
    )

    installation.gstat = Path(
        "C:/Firebird/bin/gstat.exe"
    )

    return installation


def create_service():

    cfg = MagicMock()

    cfg.database = (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    cfg.user = "SYSDBA"
    cfg.password = "masterkey"

    installation = installation_mock()

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ) as runner_cls,
        patch(
            "services.firebird.statistics_service.StatisticsParser"
        ) as parser_cls,
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        service = StatisticsService()

    return (
        service,
        cfg,
        installation,
        runner_cls.return_value,
        parser_cls.return_value,
    )


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_init_creates_service():

    (
        service,
        _,
        installation,
        runner,
        parser,
    ) = create_service()

    assert service.installation is installation
    assert service.runner is runner
    assert service.parser is parser


def test_init_stores_gstat_path():

    (
        service,
        _,
        installation,
        _,
        _,
    ) = create_service()

    assert service.gstat == (
        installation.gstat
    )


def test_init_raises_when_gstat_missing():

    cfg = MagicMock()
    cfg.database = "database.fdb"
    cfg.user = "SYSDBA"
    cfg.password = "masterkey"

    installation = installation_mock()
    installation.gstat = None

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ),
    ):

        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono gstat.exe.",
        ):

            StatisticsService()


# ==========================================================
# HEADER
# ==========================================================


def test_header_calls_runner():

    (
        service,
        cfg,
        _,
        runner,
        _,
    ) = create_service()

    result = MagicMock()

    runner.run.return_value = result

    returned = service.header()

    assert returned is result

    runner.run.assert_called_once()


def test_header_uses_gstat():

    (
        service,
        _,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert command[0] == str(
        service.gstat
    )


def test_header_uses_header_option():

    (
        service,
        _,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert "-h" in command


def test_header_uses_database():

    (
        service,
        _,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert str(
        service.database
    ) in command


def test_header_uses_configured_user():

    (
        service,
        cfg,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert cfg.user in command


def test_header_uses_configured_password():

    (
        service,
        cfg,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert cfg.password in command


def test_header_uses_gstat_operation():

    (
        service,
        _,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    runner.run.assert_called_once()

    assert (
        runner.run.call_args.kwargs["operation"]
        == "GSTAT"
    )


def test_header_builds_expected_command():

    (
        service,
        cfg,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.return_value = MagicMock()

    service.header()

    command = (
        runner.run.call_args.args[0]
    )

    assert command == [
        str(service.gstat),
        "-h",
        str(service.database),
        "-user",
        cfg.user,
        "-password",
        cfg.password,
    ]


# ==========================================================
# STATISTICS
# ==========================================================


def test_statistics_calls_header():

    (
        service,
        _,
        _,
        _,
        _,
    ) = create_service()

    header_result = MagicMock(
        success=True,
        stdout="GSTAT OUTPUT",
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ) as header:

        service.statistics()

    header.assert_called_once_with()


def test_statistics_parses_stdout():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=True,
        stdout="GSTAT OUTPUT",
    )

    expected = MagicMock()

    parser.parse.return_value = expected

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        result = service.statistics()

    assert result is expected

    parser.parse.assert_called_once_with(
        "GSTAT OUTPUT"
    )


def test_statistics_returns_parser_result():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=True,
        stdout="GSTAT OUTPUT",
    )

    expected = MagicMock()

    parser.parse.return_value = expected

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        result = service.statistics()

    assert result is expected


# ==========================================================
# GSTAT FAILURE
# ==========================================================


def test_statistics_raises_when_gstat_fails_with_stderr():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=False,
        stderr="GSTAT ERROR",
        stdout="GSTAT OUTPUT",
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        with pytest.raises(
            RuntimeError,
            match="GSTAT ERROR",
        ):

            service.statistics()

    parser.parse.assert_not_called()


def test_statistics_uses_stdout_when_stderr_empty():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=False,
        stderr="",
        stdout="GSTAT OUTPUT",
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        with pytest.raises(
            RuntimeError,
            match="GSTAT OUTPUT",
        ):

            service.statistics()

    parser.parse.assert_not_called()


def test_statistics_uses_default_message_when_output_empty():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=False,
        stderr="",
        stdout="",
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        with pytest.raises(
            RuntimeError,
            match="GSTAT zakończył się błędem.",
        ):

            service.statistics()

    parser.parse.assert_not_called()


def test_statistics_does_not_parse_failed_result():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=False,
        stderr="ERROR",
        stdout="",
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        with pytest.raises(RuntimeError):

            service.statistics()

    parser.parse.assert_not_called()


# ==========================================================
# ERROR PROPAGATION
# ==========================================================


def test_header_propagates_runner_error():

    (
        service,
        _,
        _,
        runner,
        _,
    ) = create_service()

    runner.run.side_effect = RuntimeError(
        "RUNNER ERROR"
    )

    with pytest.raises(
        RuntimeError,
        match="RUNNER ERROR",
    ):

        service.header()


def test_statistics_propagates_header_error():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    with patch.object(
        service,
        "header",
        side_effect=RuntimeError(
            "HEADER ERROR"
        ),
    ):

        with pytest.raises(
            RuntimeError,
            match="HEADER ERROR",
        ):

            service.statistics()

    parser.parse.assert_not_called()


def test_statistics_propagates_parser_error():

    (
        service,
        _,
        _,
        _,
        parser,
    ) = create_service()

    header_result = MagicMock(
        success=True,
        stdout="GSTAT OUTPUT",
    )

    parser.parse.side_effect = RuntimeError(
        "PARSER ERROR"
    )

    with patch.object(
        service,
        "header",
        return_value=header_result,
    ):

        with pytest.raises(
            RuntimeError,
            match="PARSER ERROR",
        ):

            service.statistics()