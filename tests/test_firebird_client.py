from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from services.firebird.client import FirebirdClient
from services.firebird.discovery.installation_service import (
    FirebirdInstallation,
)


def create_installation(
    isql: Path | None = Path(
        r"C:\Firebird\isql.exe"
    ),
):

    return FirebirdInstallation(
        install_path=Path(
            r"C:\Firebird"
        ),
        version="Firebird_5_0",
        isql=isql,
    )


def create_client():

    client = FirebirdClient.__new__(
        FirebirdClient
    )

    client.installation = create_installation()

    client.cfg = MagicMock()
    client.cfg.user = "SYSDBA"
    client.cfg.password = "masterkey"
    client.cfg.database = (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )

    client.runner = MagicMock()

    return client


def create_process_result(
    success=True,
    stdout="",
    stderr="",
):

    return MagicMock(
        success=success,
        stdout=stdout,
        stderr=stderr,
    )


# ==========================================================
# EXECUTE - INSTALLATION
# ==========================================================


def test_execute_fails_when_installation_is_missing():

    client = create_client()

    client.installation = None

    ok, output = client.execute(
        "SELECT 1 FROM RDB$DATABASE"
    )

    assert ok is False
    assert output == (
        "Brak instalacji Firebird."
    )

    client.runner.run.assert_not_called()


def test_execute_fails_when_isql_is_missing():

    client = create_client()

    client.installation = create_installation(
        isql=None
    )

    ok, output = client.execute(
        "SELECT 1 FROM RDB$DATABASE"
    )

    assert ok is False
    assert output == (
        "Nie znaleziono isql.exe."
    )

    client.runner.run.assert_not_called()


# ==========================================================
# EXECUTE - SQL
# ==========================================================


def test_execute_adds_semicolon():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout="RESULT",
        )
    )

    ok, output = client.execute(
        "SELECT CURRENT_USER FROM RDB$DATABASE"
    )

    assert ok is True
    assert output == "RESULT"

    kwargs = (
        client.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["input_text"] == (
        "SET HEADING OFF;\n"
        "SET LIST OFF;\n"
        "SET ECHO OFF;\n"
        "SELECT CURRENT_USER FROM RDB$DATABASE;\n"
        "QUIT;\n"
    )


def test_execute_does_not_duplicate_semicolon():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout="RESULT",
        )
    )

    client.execute(
        "SELECT CURRENT_USER FROM RDB$DATABASE;"
    )

    kwargs = (
        client.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["input_text"] == (
        "SET HEADING OFF;\n"
        "SET LIST OFF;\n"
        "SET ECHO OFF;\n"
        "SELECT CURRENT_USER FROM RDB$DATABASE;\n"
        "QUIT;\n"
    )


def test_execute_strips_sql_whitespace():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout="RESULT",
        )
    )

    client.execute(
        "  SELECT CURRENT_USER FROM RDB$DATABASE  "
    )

    kwargs = (
        client.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["input_text"] == (
        "SET HEADING OFF;\n"
        "SET LIST OFF;\n"
        "SET ECHO OFF;\n"
        "SELECT CURRENT_USER FROM RDB$DATABASE;\n"
        "QUIT;\n"
    )


# ==========================================================
# EXECUTE - COMMAND
# ==========================================================


def test_execute_builds_correct_command():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout="RESULT",
        )
    )

    client.execute(
        "SELECT CURRENT_USER FROM RDB$DATABASE"
    )

    command = (
        client.runner
        .run
        .call_args.args[0]
    )

    assert command == [
        r"C:\Firebird\isql.exe",
        "-user",
        "SYSDBA",
        "-password",
        "masterkey",
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
    ]


def test_execute_uses_correct_runner_options():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout="RESULT",
        )
    )

    client.execute(
        "SELECT 1 FROM RDB$DATABASE"
    )

    kwargs = (
        client.runner
        .run
        .call_args.kwargs
    )

    assert kwargs["operation"] == "ISQL"
    assert kwargs["log_operation"] is False


# ==========================================================
# EXECUTE - OUTPUT
# ==========================================================


def test_execute_filters_isql_output():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout=(
                "\n"
                "Database: C:\\test\\database.fdb\n"
                "SQL> SELECT CURRENT_USER;\n"
                "CON> something\n"
                "\n"
                "SYSDBA\n"
                "RESULT\n"
            ),
        )
    )

    ok, output = client.execute(
        "SELECT CURRENT_USER"
    )

    assert ok is True

    assert output == (
        "SYSDBA\n"
        "RESULT"
    )


def test_execute_strips_output_lines():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout=(
                "   FIRST   \n"
                "  SECOND  \n"
            ),
        )
    )

    ok, output = client.execute(
        "SELECT TEST"
    )

    assert ok is True
    assert output == (
        "FIRST\n"
        "SECOND"
    )


def test_execute_returns_empty_output_when_no_rows():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=True,
            stdout=(
                "\n"
                "Database: test\n"
                "SQL>\n"
                "CON>\n"
            ),
        )
    )

    ok, output = client.execute(
        "SELECT TEST"
    )

    assert ok is True
    assert output == ""


# ==========================================================
# EXECUTE - FAILURE
# ==========================================================


def test_execute_returns_runner_error():

    client = create_client()

    client.runner.run.return_value = (
        create_process_result(
            success=False,
            stdout="",
            stderr="ISQL ERROR",
        )
    )

    ok, output = client.execute(
        "SELECT TEST"
    )

    assert ok is False
    assert output == "ISQL ERROR"


def test_execute_propagates_runner_exception():

    client = create_client()

    client.runner.run.side_effect = (
        RuntimeError(
            "ProcessRunner ERROR"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="ProcessRunner ERROR",
    ):

        client.execute(
            "SELECT TEST"
        )


# ==========================================================
# FETCH ONE
# ==========================================================


def test_fetch_one_returns_first_row():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            True,
            "FIRST\nSECOND\nTHIRD",
        )
    )

    result = client.fetch_one(
        "SELECT TEST"
    )

    assert result == "FIRST"

    client.execute.assert_called_once_with(
        "SELECT TEST"
    )


def test_fetch_one_returns_none_when_no_rows():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            True,
            "",
        )
    )

    result = client.fetch_one(
        "SELECT TEST"
    )

    assert result is None


def test_fetch_one_raises_on_execute_failure():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            False,
            "ISQL ERROR",
        )
    )

    with pytest.raises(
        RuntimeError,
        match="ISQL ERROR",
    ):

        client.fetch_one(
            "SELECT TEST"
        )


# ==========================================================
# FETCH ALL
# ==========================================================


def test_fetch_all_returns_all_rows():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            True,
            "FIRST\nSECOND\nTHIRD",
        )
    )

    result = client.fetch_all(
        "SELECT TEST"
    )

    assert result == [
        "FIRST",
        "SECOND",
        "THIRD",
    ]

    client.execute.assert_called_once_with(
        "SELECT TEST"
    )


def test_fetch_all_strips_empty_lines():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            True,
            " FIRST \n\n SECOND \n",
        )
    )

    result = client.fetch_all(
        "SELECT TEST"
    )

    assert result == [
        "FIRST",
        "SECOND",
    ]


def test_fetch_all_returns_empty_list_when_no_rows():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            True,
            "",
        )
    )

    result = client.fetch_all(
        "SELECT TEST"
    )

    assert result == []


def test_fetch_all_raises_on_execute_failure():

    client = create_client()

    client.execute = MagicMock(
        return_value=(
            False,
            "ISQL ERROR",
        )
    )

    with pytest.raises(
        RuntimeError,
        match="ISQL ERROR",
    ):

        client.fetch_all(
            "SELECT TEST"
        )