from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.database_service import DatabaseService


def create_service() -> DatabaseService:

    installation = MagicMock()

    with patch(
        "services.firebird.database_service.InstallationService"
    ) as installation_service:

        installation_service.return_value.first_installation.return_value = (
            installation
        )

        service = DatabaseService()

    return service


# ==========================================================
# INITIALIZATION
# ==========================================================


def test_init_creates_firebird_client():

    installation = MagicMock()

    with patch(
        "services.firebird.database_service.InstallationService"
    ) as installation_service, patch(
        "services.firebird.database_service.FirebirdClient"
    ) as client_class:

        installation_service.return_value.first_installation.return_value = (
            installation
        )

        service = DatabaseService()

    installation_service.return_value.first_installation.assert_called_once_with()

    client_class.assert_called_once_with(
        installation
    )

    assert service.client is (
        client_class.return_value
    )


def test_init_raises_when_firebird_not_found():

    with patch(
        "services.firebird.database_service.InstallationService"
    ) as installation_service:

        installation_service.return_value.first_installation.return_value = (
            None
        )

        with pytest.raises(
            RuntimeError,
            match="Nie znaleziono instalacji Firebird.",
        ):

            DatabaseService()


# ==========================================================
# EXISTS
# ==========================================================


def test_exists_returns_true_for_existing_file(
    tmp_path: Path,
):

    database = tmp_path / "test.fdb"

    database.touch()

    service = create_service()

    assert service.exists(
        str(database)
    ) is True


def test_exists_returns_false_for_missing_file(
    tmp_path: Path,
):

    database = tmp_path / "missing.fdb"

    service = create_service()

    assert service.exists(
        str(database)
    ) is False


def test_exists_returns_false_for_empty_path():

    service = create_service()

    assert service.exists("") is False


def test_exists_returns_false_for_none():

    service = create_service()

    assert service.exists(None) is False


def test_exists_accepts_path_object(
    tmp_path: Path,
):

    database = tmp_path / "test.fdb"

    database.touch()

    service = create_service()

    assert service.exists(
        database
    ) is True


# ==========================================================
# SIZE
# ==========================================================


def test_size_gb_returns_zero_for_missing_file(
    tmp_path: Path,
):

    database = tmp_path / "missing.fdb"

    service = create_service()

    assert service.size_gb(
        str(database)
    ) == 0.0


def test_size_gb_returns_zero_for_empty_path():

    service = create_service()

    assert service.size_gb("") == 0.0


def test_size_gb_returns_zero_for_none():

    service = create_service()

    assert service.size_gb(None) == 0.0


def test_size_gb_returns_file_size(
    tmp_path: Path,
):

    database = tmp_path / "test.fdb"

    database.write_bytes(
        b"x" * 1024
    )

    service = create_service()

    result = service.size_gb(
        str(database)
    )

    assert result > 0.0


def test_size_gb_calculates_exact_size(
    tmp_path: Path,
):

    database = tmp_path / "test.fdb"

    database.write_bytes(
        b"x" * (1024 ** 3)
    )

    service = create_service()

    result = service.size_gb(
        database
    )

    assert result == 1.0


def test_size_gb_returns_zero_when_stat_raises(
    tmp_path: Path,
):

    database = tmp_path / "test.fdb"

    database.touch()

    service = create_service()

    with patch.object(
        Path,
        "stat",
        side_effect=OSError("STAT ERROR"),
    ):

        result = service.size_gb(
            database
        )

    assert result == 0.0


# ==========================================================
# VERSION
# ==========================================================


def test_version():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = (
        "WI-V3.0.10.32395 Firebird 3.0"
    )

    result = service.version()

    assert result == (
        "WI-V3.0.10.32395 Firebird 3.0"
    )

    service.client.fetch_one.assert_called_once()


def test_version_returns_empty_string_when_result_is_none():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = None

    result = service.version()

    assert result == ""


def test_version_returns_empty_string_when_result_is_empty():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = ""

    result = service.version()

    assert result == ""


def test_version_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("ISQL ERROR")
    )

    with pytest.raises(
        RuntimeError,
        match="ISQL ERROR",
    ):

        service.version()


# ==========================================================
# SQL DIALECT
# ==========================================================


def test_sql_dialect():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "3"

    result = service.sql_dialect()

    assert result == 3

    service.client.fetch_one.assert_called_once()


def test_sql_dialect_converts_integer_string():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "1"

    result = service.sql_dialect()

    assert result == 1


def test_sql_dialect_raises_for_invalid_value():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = (
        "INVALID"
    )

    with pytest.raises(
        ValueError
    ):

        service.sql_dialect()


# ==========================================================
# PAGE SIZE
# ==========================================================


def test_page_size():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "8192"

    result = service.page_size()

    assert result == 8192

    service.client.fetch_one.assert_called_once()


def test_page_size_raises_for_invalid_value():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = (
        "INVALID"
    )

    with pytest.raises(
        ValueError
    ):

        service.page_size()


# ==========================================================
# ODS
# ==========================================================


def test_ods():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = [
        "13",
        "0",
    ]

    result = service.ods()

    assert result == "13.0"

    assert service.client.fetch_one.call_count == 2


def test_ods_reads_major_before_minor():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = [
        "12",
        "5",
    ]

    result = service.ods()

    assert result == "12.5"

    calls = (
        service.client.fetch_one.call_args_list
    )

    assert len(calls) == 2


def test_ods_handles_none_values():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = [
        None,
        None,
    ]

    result = service.ods()

    assert result == "None.None"


def test_ods_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("ISQL ERROR")
    )

    with pytest.raises(
        RuntimeError,
        match="ISQL ERROR",
    ):

        service.ods()


# ==========================================================
# TABLES
# ==========================================================


def test_tables():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "47"

    result = service.tables()

    assert result == 47

    service.client.fetch_one.assert_called_once()


def test_tables_returns_zero_for_zero():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "0"

    result = service.tables()

    assert result == 0


def test_tables_raises_for_invalid_value():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = (
        "INVALID"
    )

    with pytest.raises(
        ValueError
    ):

        service.tables()


# ==========================================================
# CLIENT ERROR PROPAGATION
# ==========================================================


def test_sql_dialect_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("DIALECT ERROR")
    )

    with pytest.raises(
        RuntimeError,
        match="DIALECT ERROR",
    ):

        service.sql_dialect()


def test_page_size_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("PAGE SIZE ERROR")
    )

    with pytest.raises(
        RuntimeError,
        match="PAGE SIZE ERROR",
    ):

        service.page_size()


def test_tables_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("TABLE ERROR")
    )

    with pytest.raises(
        RuntimeError,
        match="TABLE ERROR",
    ):

        service.tables()


# ==========================================================
# SQL CONTENT
# ==========================================================


def test_version_uses_engine_version_query():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = (
        "Firebird 5.0"
    )

    service.version()

    query = (
        service.client
        .fetch_one
        .call_args.args[0]
    )

    assert "ENGINE_VERSION" in query
    assert "RDB$GET_CONTEXT" in query.upper()
    assert "RDB$DATABASE" in query.upper()


def test_sql_dialect_uses_monitor_query():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "3"

    service.sql_dialect()

    query = (
        service.client
        .fetch_one
        .call_args.args[0]
    )

    assert "MON$SQL_DIALECT" in query
    assert "MON$DATABASE" in query


def test_page_size_uses_monitor_query():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "8192"

    service.page_size()

    query = (
        service.client
        .fetch_one
        .call_args.args[0]
    )

    assert "MON$PAGE_SIZE" in query
    assert "MON$DATABASE" in query


def test_ods_uses_major_and_minor_queries():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = [
        "13",
        "0",
    ]

    service.ods()

    calls = (
        service.client
        .fetch_one
        .call_args_list
    )

    assert len(calls) == 2

    assert "MON$ODS_MAJOR" in (
        calls[0].args[0]
    )

    assert "MON$ODS_MINOR" in (
        calls[1].args[0]
    )


def test_tables_uses_system_relations_query():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "47"

    service.tables()

    query = (
        service.client
        .fetch_one
        .call_args.args[0]
    )

    assert "COUNT(*)" in query.upper()
    assert "RDB$RELATIONS" in query.upper()
    assert "RDB$SYSTEM_FLAG" in query.upper()