from __future__ import annotations

from config.config import Config
from core.settings import Settings


def test_password_is_saved_encrypted_and_not_in_config(
    tmp_path,
) -> None:
    config_path = tmp_path / "config.ini"
    database_path = tmp_path / "settings.db"

    config_path.write_text(
        "[Firebird]\n"
        "database=C:\\KSBAZA\\WAPTEKA.FDB\n"
        "user=SYSDBA\n"
        "password=StareHaslo123!\n",
        encoding="utf-8",
    )

    store = Settings(database_path)

    config = Config(
        config_path,
        settings_store=store,
    )

    assert config.password == "StareHaslo123!"

    stored_value = store.get(
        "firebird.password",
        "",
    )

    assert stored_value
    assert stored_value != "StareHaslo123!"

    config_content = config_path.read_text(
        encoding="utf-8",
    )

    assert "StareHaslo123!" not in config_content

    config2 = Config(
        config_path,
        settings_store=store,
    )

    assert config2.password == "StareHaslo123!"

    store.close()


def test_password_can_be_changed(
    tmp_path,
) -> None:
    config_path = tmp_path / "config.ini"
    database_path = tmp_path / "settings.db"

    config_path.write_text(
        "[Firebird]\n"
        "database=C:\\KSBAZA\\WAPTEKA.FDB\n"
        "user=SYSDBA\n"
        "password=\n",
        encoding="utf-8",
    )

    store = Settings(database_path)

    config = Config(
        config_path,
        settings_store=store,
    )

    config.save_password("NoweHaslo456!")

    assert config.password == "NoweHaslo456!"

    config2 = Config(
        config_path,
        settings_store=store,
    )

    assert config2.password == "NoweHaslo456!"

    config_content = config_path.read_text(
        encoding="utf-8",
    )

    assert "NoweHaslo456!" not in config_content

    store.close()