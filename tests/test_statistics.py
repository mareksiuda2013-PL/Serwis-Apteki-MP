from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.statistics_service import (
    StatisticsService,
)


GSTAT_OUTPUT = """
Database "C:\\KSBAZA\\KS-APW\\WAPTEKA.FDB"

Page size 8192
ODS version 13.0
Oldest transaction 100
Oldest active 120
Oldest snapshot 125
Next transaction 500
Page buffers 2048
Database dialect 3
Creation date Aug 24, 2026 10:00:00
Attributes force write
Sweep interval 20000
Generation 10
"""


def create_service() -> StatisticsService:

    installation = MagicMock()

    installation.gstat = (
        "C:/Firebird/bin/gstat.exe"
    )

    with patch(
        "services.firebird.statistics_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = StatisticsService.__new__(
            StatisticsService
        )

    service.installation = installation
    service.gstat = installation.gstat
    service.database = Path(
        "C:/database/test.fdb"
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.runner = MagicMock()

    from services.firebird.statistics_parser import (
        StatisticsParser,
    )

    service.parser = StatisticsParser()

    return service


# ==========================================================
# HEADER
# ==========================================================


def test_header_builds_correct_command():

    service = create_service()

    process_result = MagicMock(
        success=True,
        stdout=GSTAT_OUTPUT,
        stderr="",
        return_code=0,
    )

    service.runner.run.return_value = (
        process_result
    )

    result = service.header()

    assert result is process_result

    service.runner.run.assert_called_once()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        "C:/Firebird/bin/gstat.exe",
        "-h",
        r"C:\database\test.fdb",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
    ]


def test_header_uses_correct_runner_operation():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="",
        stderr="",
    )

    service.header()

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["operation"] == "GSTAT"


def test_header_uses_configured_credentials():

    service = create_service()

    service.cfg.user = "TESTUSER"
    service.cfg.password = "TESTPASSWORD"

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="",
        stderr="",
    )

    service.header()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert "TESTUSER" in command
    assert "TESTPASSWORD" in command


def test_header_uses_configured_database():

    service = create_service()

    service.database = Path(
        r"C:\test\database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="",
        stderr="",
    )

    service.header()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert (
        r"C:\test\database.fdb"
        in command
    )


# ==========================================================
# STATISTICS
# ==========================================================


def test_statistics_uses_parser():

    service = create_service()

    process_result = MagicMock(
        success=True,
        stdout=GSTAT_OUTPUT,
        stderr="",
    )

    service.header = MagicMock(
        return_value=process_result
    )

    service.parser = MagicMock()

    expected = MagicMock()

    service.parser.parse.return_value = (
        expected
    )

    result = service.statistics()

    assert result is expected

    service.parser.parse.assert_called_once_with(
        GSTAT_OUTPUT
    )


def test_statistics_returns_parsed_statistics():

    service = create_service()

    process_result = MagicMock(
        success=True,
        stdout=GSTAT_OUTPUT,
        stderr="",
    )

    service.header = MagicMock(
        return_value=process_result
    )

    result = service.statistics()

    assert result.page_size == 8192
    assert result.ods == "13.0"
    assert result.oldest_transaction == 100
    assert result.oldest_active == 120
    assert result.oldest_snapshot == 125
    assert result.next_transaction == 500
    assert result.page_buffers == 2048
    assert result.database_dialect == 3
    assert result.creation_date == (
        "Aug 24, 2026 10:00:00"
    )
    assert result.sweep_interval == 20000
    assert result.generation == 10
    assert result.forced_writes is True


# ==========================================================
# GSTAT ERROR
# ==========================================================


def test_statistics_raises_when_gstat_fails():

    service = create_service()

    process_result = MagicMock(
        success=False,
        stdout="",
        stderr="GSTAT ERROR",
    )

    service.header = MagicMock(
        return_value=process_result
    )

    with pytest.raises(
        RuntimeError,
        match="GSTAT ERROR",
    ):

        service.statistics()


def test_statistics_uses_stdout_when_stderr_empty():

    service = create_service()

    process_result = MagicMock(
        success=False,
        stdout="GSTAT OUTPUT ERROR",
        stderr="",
    )

    service.header = MagicMock(
        return_value=process_result
    )

    with pytest.raises(
        RuntimeError,
        match="GSTAT OUTPUT ERROR",
    ):

        service.statistics()


def test_statistics_uses_default_error_message():

    service = create_service()

    process_result = MagicMock(
        success=False,
        stdout="",
        stderr="",
    )

    service.header = MagicMock(
        return_value=process_result
    )

    with pytest.raises(
        RuntimeError,
        match="GSTAT zakończył się błędem",
    ):

        service.statistics()


# ==========================================================
# EXCEPTION
# ==========================================================


def test_header_propagates_runner_exception():

    service = create_service()

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="ProcessRunner ERROR",
    ):

        service.header()


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_statistics_raises_when_gstat_is_missing():

    with patch(
        "services.firebird.statistics_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = StatisticsService.__new__(
            StatisticsService
        )

        service.installation = MagicMock()
        service.installation.gstat = None

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono gstat.exe",
        ):

            StatisticsService.__init__(
                service
            )


def test_statistics_initializes_parser():

    installation = MagicMock()

    installation.gstat = Path(
        r"C:\Firebird\gstat.exe"
    )

    with patch(
        "services.firebird.statistics_service.BaseFirebirdService.__init__",
        return_value=None,
    ):

        service = StatisticsService.__new__(
            StatisticsService
        )

        service.installation = installation

        with patch(
            "services.firebird.statistics_service.StatisticsParser"
        ) as parser_cls:

            StatisticsService.__init__(
                service
            )

    parser_cls.assert_called_once()

    assert service.parser is (
        parser_cls.return_value
    )