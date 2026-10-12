from __future__ import annotations

from pathlib import Path

from config.config import Config


def test_config_reads_firebird_settings(tmp_path: Path):
    config_path = tmp_path / "config.ini"

    config_path.write_text(
        """
[Firebird]
database = C:\\KSBAZA\\KS-APW\\WAPTEKA.FDB
user = SYSDBA
password = masterkey
""".strip(),
        encoding="utf-8",
    )

    config = Config(config_path)

    assert config.database == (
        r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"
    )
    assert config.user == "SYSDBA"
    assert config.password == "masterkey"


def test_config_uses_default_path():
    config = Config()

    assert config.path.name == "config.ini"


def test_config_path_can_be_customized(tmp_path: Path):
    config_path = tmp_path / "custom.ini"

    config_path.write_text(
        """
[Firebird]
database = test.fdb
user = TEST
password = secret
""".strip(),
        encoding="utf-8",
    )

    config = Config(config_path)

    assert config.path == config_path
    assert config.database == "test.fdb"
    assert config.user == "TEST"
    assert config.password == "secret"