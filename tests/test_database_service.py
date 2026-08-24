from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from services.firebird.database_service import DatabaseService


def create_service() -> DatabaseService:
    """
    Tworzy DatabaseService bez wykrywania
    prawdziwej instalacji Firebird.
    """

    installation = MagicMock()

    with patch(
        "services.firebird.database_service.InstallationService"
    ) as installation_service:

        installation_service.return_value.first_installation.return_value = (
            installation
        )

        service = DatabaseService()

    return service


# ============================================================
# EXISTS
# ============================================================


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


# ============================================================
# SIZE
# ============================================================


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


# ============================================================
# VERSION
# ============================================================


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


# ============================================================
# SQL DIALECT
# ============================================================


def test_sql_dialect():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "3"

    result = service.sql_dialect()

    assert result == 3


# ============================================================
# PAGE SIZE
# ============================================================


def test_page_size():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "8192"

    result = service.page_size()

    assert result == 8192


# ============================================================
# ODS
# ============================================================


def test_ods():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = [
        "13",
        "0",
    ]

    result = service.ods()

    assert result == "13.0"


# ============================================================
# TABLES
# ============================================================


def test_tables():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.return_value = "47"

    result = service.tables()

    assert result == 47


# ============================================================
# SQL CLIENT ERROR
# ============================================================


def test_version_propagates_client_error():

    service = create_service()

    service.client = MagicMock()

    service.client.fetch_one.side_effect = (
        RuntimeError("ISQL ERROR")
    )

    try:

        service.version()

    except RuntimeError as exc:

        assert str(exc) == "ISQL ERROR"

    else:

        raise AssertionError(
            "Oczekiwano RuntimeError."
        )