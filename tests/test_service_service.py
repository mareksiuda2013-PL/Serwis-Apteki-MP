from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from services.firebird.statistics_service import (
    StatisticsService,
)


def create_service():

    service = StatisticsService.__new__(
        StatisticsService
    )

    service.cfg = MagicMock()
    service.cfg.user = "SYSDBA"
    service.cfg.password = "masterkey"

    service.database = Path(
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    service.gstat = Path(
        r"C:\Firebird\gstat.exe"
    )

    service.runner = MagicMock()
    service.parser = MagicMock()

    return service


# ==========================================================
# HEADER — SUCCESS
# ==========================================================


def test_header_success():

    service = create_service()

    expected = MagicMock(
        success=True,
        stdout="Database statistics",
        stderr="",
    )

    service.runner.run.return_value = expected

    result = service.header()

    assert result is expected


# ==========================================================
# HEADER — FAILURE
# ==========================================================


def test_header_failure():

    service = create_service()

    expected = MagicMock(
        success=False,
        stdout="",
        stderr="GSTAT ERROR",
    )

    service.runner.run.return_value = expected

    result = service.header()

    assert result is expected


# ==========================================================
# HEADER — COMMAND
# ==========================================================


def test_header_builds_correct_command():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.header()

    service.runner.run.assert_called_once()

    command = (
        service.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\gstat.exe",
        "-h",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
    ]


# ==========================================================
# HEADER — RUNNER OPTIONS
# ==========================================================


def test_header_uses_correct_runner_options():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
        stderr="",
    )

    service.header()

    kwargs = (
        service.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["operation"] == "GSTAT"


# ==========================================================
# HEADER — DATABASE
# ==========================================================


def test_header_uses_configured_database():

    service = create_service()

    service.database = Path(
        r"C:\test\database.fdb"
    )

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
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
# HEADER — CREDENTIALS
# ==========================================================


def test_header_uses_configured_credentials():

    service = create_service()

    service.cfg.user = "TESTUSER"
    service.cfg.password = "TESTPASSWORD"

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="OK",
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


# ==========================================================
# HEADER — RUNNER EXCEPTION
# ==========================================================


def test_header_propagates_runner_exception():

    service = create_service()

    service.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    try:

        service.header()

    except RuntimeError as exc:

        assert str(exc) == (
            "ProcessRunner ERROR"
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# STATISTICS — SUCCESS
# ==========================================================


def test_statistics_returns_parsed_result():

    service = create_service()

    process_result = MagicMock(
        success=True,
        stdout="GSTAT OUTPUT",
        stderr="",
    )

    expected = MagicMock()

    service.runner.run.return_value = (
        process_result
    )

    service.parser.parse.return_value = (
        expected
    )

    result = service.statistics()

    assert result is expected

    service.parser.parse.assert_called_once_with(
        "GSTAT OUTPUT"
    )


# ==========================================================
# STATISTICS — FAILURE WITH STDERR
# ==========================================================


def test_statistics_raises_on_failure_with_stderr():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="GSTAT ERROR",
    )

    try:

        service.statistics()

    except RuntimeError as exc:

        assert str(exc) == "GSTAT ERROR"

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# STATISTICS — FAILURE WITH STDOUT
# ==========================================================


def test_statistics_raises_on_failure_with_stdout():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="GSTAT FAILURE OUTPUT",
        stderr="",
    )

    try:

        service.statistics()

    except RuntimeError as exc:

        assert str(exc) == (
            "GSTAT FAILURE OUTPUT"
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# STATISTICS — FAILURE WITHOUT MESSAGE
# ==========================================================


def test_statistics_raises_default_error():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=False,
        stdout="",
        stderr="",
    )

    try:

        service.statistics()

    except RuntimeError as exc:

        assert str(exc) == (
            "GSTAT zakończył się błędem."
        )

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )


# ==========================================================
# STATISTICS — PARSER
# ==========================================================


def test_statistics_uses_parser():

    service = create_service()

    process_result = MagicMock(
        success=True,
        stdout="RAW GSTAT DATA",
        stderr="",
    )

    parsed = MagicMock()

    service.runner.run.return_value = (
        process_result
    )

    service.parser.parse.return_value = (
        parsed
    )

    result = service.statistics()

    assert result is parsed

    service.parser.parse.assert_called_once_with(
        "RAW GSTAT DATA"
    )


# ==========================================================
# STATISTICS — PARSER EXCEPTION
# ==========================================================


def test_statistics_propagates_parser_exception():

    service = create_service()

    service.runner.run.return_value = MagicMock(
        success=True,
        stdout="RAW GSTAT DATA",
        stderr="",
    )

    service.parser.parse.side_effect = (
        RuntimeError(
            "Parser ERROR"
        )
    )

    try:

        service.statistics()

    except RuntimeError as exc:

        assert str(exc) == "Parser ERROR"

    else:

        raise AssertionError(
            "Expected RuntimeError"
        )