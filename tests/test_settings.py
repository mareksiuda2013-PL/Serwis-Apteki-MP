from __future__ import annotations

from pathlib import Path

from core.settings import Settings


def test_settings_creates_database(tmp_path: Path):
    db_path = tmp_path / "test.db"

    settings = Settings(db_path)

    assert db_path.exists()

    settings.close()


def test_get_returns_default_when_key_does_not_exist(
    tmp_path: Path,
):
    db_path = tmp_path / "test.db"

    settings = Settings(db_path)

    result = settings.get(
        "missing_key",
        "default_value",
    )

    assert result == "default_value"

    settings.close()


def test_set_and_get_value(tmp_path: Path):
    db_path = tmp_path / "test.db"

    settings = Settings(db_path)

    settings.set(
        "test_key",
        "test_value",
    )

    result = settings.get("test_key")

    assert result == "test_value"

    settings.close()


def test_set_updates_existing_value(tmp_path: Path):
    db_path = tmp_path / "test.db"

    settings = Settings(db_path)

    settings.set(
        "test_key",
        "value_1",
    )

    settings.set(
        "test_key",
        "value_2",
    )

    result = settings.get("test_key")

    assert result == "value_2"

    settings.close()


def test_set_converts_value_to_string(tmp_path: Path):
    db_path = tmp_path / "test.db"

    settings = Settings(db_path)

    settings.set(
        "number",
        123,
    )

    result = settings.get("number")

    assert result == "123"

    settings.close()


def test_settings_are_persistent(tmp_path: Path):
    db_path = tmp_path / "test.db"

    first = Settings(db_path)

    first.set(
        "persistent",
        "saved",
    )

    first.close()

    second = Settings(db_path)

    result = second.get("persistent")

    assert result == "saved"

    second.close()