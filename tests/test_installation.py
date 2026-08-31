from __future__ import annotations

from pathlib import Path

from services.firebird.discovery.installation_service import (
    FirebirdInstallation,
    InstallationService,
)


# ==========================================================
# HELPERS
# ==========================================================


def create_firebird_installation(
    root: Path,
) -> Path:

    firebird = root / "Firebird_5_0"

    bin_path = firebird / "bin"

    bin_path.mkdir(
        parents=True
    )

    (bin_path / "fbclient.dll").touch()
    (bin_path / "isql.exe").touch()
    (bin_path / "gbak.exe").touch()
    (bin_path / "gfix.exe").touch()
    (bin_path / "gstat.exe").touch()

    (firebird / "firebird.conf").touch()

    return firebird


# ==========================================================
# FIREBIRD INSTALLATION
# ==========================================================


def test_firebird_installation_defaults():

    path = Path(
        r"C:\Firebird\Firebird_5_0"
    )

    installation = FirebirdInstallation(
        install_path=path
    )

    assert installation.install_path == path
    assert installation.version == ""

    assert installation.fbclient is None
    assert installation.isql is None
    assert installation.gbak is None
    assert installation.gfix is None
    assert installation.gstat is None
    assert installation.firebird_conf is None


# ==========================================================
# FIND
# ==========================================================


def test_find_returns_matching_file(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    target = root / "gstat.exe"

    target.touch()

    service = InstallationService()

    result = service.find(
        root,
        "gstat.exe",
    )

    assert result == target


def test_find_is_case_insensitive(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    target = root / "GSTAT.EXE"

    target.touch()

    service = InstallationService()

    result = service.find(
        root,
        "gstat.exe",
    )

    assert result == target


def test_find_accepts_multiple_names(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    target = root / "isql.com"

    target.touch()

    service = InstallationService()

    result = service.find(
        root,
        "isql",
        "isql.exe",
        "isql.com",
    )

    assert result == target


def test_find_returns_none_when_missing(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    service = InstallationService()

    result = service.find(
        root,
        "gfix.exe",
    )

    assert result is None


def test_find_ignores_directories_with_matching_name(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    directory = root / "gstat.exe"

    directory.mkdir()

    service = InstallationService()

    result = service.find(
        root,
        "gstat.exe",
    )

    assert result is None


# ==========================================================
# FIRST INSTALLATION
# ==========================================================


def test_first_installation_returns_none_when_root_missing(
    tmp_path: Path,
):

    root = tmp_path / "missing"

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is None


def test_first_installation_returns_none_when_no_firebird_folder(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    (root / "OtherSoftware").mkdir()

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is None


def test_first_installation_finds_firebird(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    firebird = create_firebird_installation(
        root
    )

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is not None

    assert result.install_path == firebird

    assert result.version == "Firebird_5_0"


def test_first_installation_finds_all_tools(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    firebird = create_firebird_installation(
        root
    )

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is not None

    assert result.fbclient == (
        firebird
        / "bin"
        / "fbclient.dll"
    )

    assert result.isql == (
        firebird
        / "bin"
        / "isql.exe"
    )

    assert result.gbak == (
        firebird
        / "bin"
        / "gbak.exe"
    )

    assert result.gfix == (
        firebird
        / "bin"
        / "gfix.exe"
    )

    assert result.gstat == (
        firebird
        / "bin"
        / "gstat.exe"
    )

    assert result.firebird_conf == (
        firebird
        / "firebird.conf"
    )


def test_first_installation_ignores_non_directories(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    (root / "Firebird_5_0").touch()

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is None


def test_first_installation_ignores_non_firebird_directories(
    tmp_path: Path,
):

    root = tmp_path / "Firebird"

    root.mkdir()

    (root / "SomethingElse").mkdir()

    service = InstallationService(
        roots=(root,)
    )

    result = service.first_installation()

    assert result is None


# ==========================================================
# ROOT ORDER
# ==========================================================


def test_first_installation_uses_first_matching_root(
    tmp_path: Path,
):

    root_one = tmp_path / "root_one"
    root_two = tmp_path / "root_two"

    root_one.mkdir()
    root_two.mkdir()

    first = create_firebird_installation(
        root_one
    )

    create_firebird_installation(
        root_two
    )

    service = InstallationService(
        roots=(
            root_one,
            root_two,
        )
    )

    result = service.first_installation()

    assert result is not None
    assert result.install_path == first