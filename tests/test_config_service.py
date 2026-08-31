from __future__ import annotations

from pathlib import Path

from services.firebird.config_service import ConfigService


def test_load_none_path():

    service = ConfigService()

    result = service.load(None)

    assert result.path is None
    assert result.exists is False
    assert result.raw == {}
    assert result.remote_service_port == 3050
    assert result.guardian is False
    assert result.root_directory == ""
    assert result.temp_directories == ""


def test_load_missing_file(tmp_path: Path):

    service = ConfigService()

    config_path = tmp_path / "missing.conf"

    result = service.load(config_path)

    assert result.path == config_path
    assert result.exists is False
    assert result.raw == {}


def test_load_empty_file(tmp_path: Path):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"
    config_path.write_text(
        "",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.path == config_path
    assert result.exists is True
    assert result.raw == {}


def test_load_parses_raw_values(tmp_path: Path):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"

    config_path.write_text(
        """
RemoteServicePort = 3055
Guardian = true
RootDirectory = C:\\Firebird
TempDirectories = C:\\Temp
""",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.raw == {
        "RemoteServicePort": "3055",
        "Guardian": "true",
        "RootDirectory": r"C:\Firebird",
        "TempDirectories": r"C:\Temp",
    }


def test_load_parses_remote_service_port(tmp_path: Path):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"

    config_path.write_text(
        "RemoteServicePort = 3055\n",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.remote_service_port == 3055


def test_invalid_remote_service_port_keeps_default(
    tmp_path: Path,
):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"

    config_path.write_text(
        "RemoteServicePort = abc\n",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.remote_service_port == 3050
    assert result.raw["RemoteServicePort"] == "abc"


def test_load_parses_guardian_values(tmp_path: Path):

    service = ConfigService()

    values = (
        "1",
        "true",
        "yes",
        "on",
    )

    for value in values:

        config_path = tmp_path / f"{value}.conf"

        config_path.write_text(
            f"Guardian = {value}\n",
            encoding="utf-8",
        )

        result = service.load(config_path)

        assert result.guardian is True


def test_load_guardian_false_for_other_values(
    tmp_path: Path,
):

    service = ConfigService()

    values = (
        "0",
        "false",
        "no",
        "off",
        "anything",
    )

    for value in values:

        config_path = tmp_path / f"{value}.conf"

        config_path.write_text(
            f"Guardian = {value}\n",
            encoding="utf-8",
        )

        result = service.load(config_path)

        assert result.guardian is False


def test_load_parses_directories(tmp_path: Path):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"

    config_path.write_text(
        """
RootDirectory = C:\\Firebird
TempDirectories = C:\\Temp;D:\\Temp
""",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.root_directory == r"C:\Firebird"
    assert result.temp_directories == r"C:\Temp;D:\Temp"


def test_load_ignores_empty_comments_and_invalid_lines(
    tmp_path: Path,
):

    service = ConfigService()

    config_path = tmp_path / "firebird.conf"

    config_path.write_text(
        """
        
# comment

This line has no equals sign

RemoteServicePort = 3055

# another comment

Guardian = yes
""",
        encoding="utf-8",
    )

    result = service.load(config_path)

    assert result.raw == {
        "RemoteServicePort": "3055",
        "Guardian": "yes",
    }

    assert result.remote_service_port == 3055
    assert result.guardian is True