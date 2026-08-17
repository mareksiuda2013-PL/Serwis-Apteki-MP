from __future__ import annotations

from pathlib import Path

from services.firebird.restore_service import RestoreService


def test_restore_missing_backup(tmp_path):
    """
    Restore powinien zwrócić błąd,
    jeżeli plik FBK nie istnieje.
    """

    service = RestoreService()

    backup_file = tmp_path / "brak.fbk"
    database_file = tmp_path / "test.fdb"

    ok, message = service.restore(
        backup_file,
        database_file,
    )

    assert ok is False
    assert "Nie znaleziono backupu" in message


def test_restore_existing_database_without_replace(tmp_path):
    """
    Restore nie powinien nadpisywać istniejącej bazy,
    gdy replace=False.
    """

    service = RestoreService()

    backup_file = tmp_path / "backup.fbk"
    database_file = tmp_path / "test.fdb"

    backup_file.write_text(
        "test",
        encoding="utf-8",
    )

    database_file.write_text(
        "existing",
        encoding="utf-8",
    )

    ok, message = service.restore(
        backup_file,
        database_file,
        replace=False,
    )

    assert ok is False
    assert "Baza już istnieje" in message


def test_restore_missing_backup_does_not_create_database(tmp_path):
    """
    Brak backupu nie powinien powodować
    utworzenia bazy docelowej.
    """

    service = RestoreService()

    backup_file = tmp_path / "brak.fbk"
    database_file = tmp_path / "test.fdb"

    ok, message = service.restore(
        backup_file,
        database_file,
        replace=True,
    )

    assert ok is False
    assert not database_file.exists()