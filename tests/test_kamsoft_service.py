from pathlib import Path

from services.kamsoft import KamsoftService


def test_empty_service():
    service = KamsoftService()

    assert service.install_path is None
    assert service.exists() is False
    assert service.apman_path() is None
    assert service.apman_exists() is False
    assert service.apman_ini_path() is None
    assert service.apman_ini_exists() is False
    assert service.version() is None


def test_install_path(tmp_path):
    service = KamsoftService(tmp_path)

    assert service.install_path == Path(tmp_path)
    assert service.exists() is True


def test_set_install_path(tmp_path):
    service = KamsoftService()

    service.set_install_path(tmp_path)

    assert service.install_path == Path(tmp_path)
    assert service.exists() is True


def test_apman(tmp_path):
    apman = tmp_path / "APMAN.EXE"
    apman.write_text("test")

    service = KamsoftService(tmp_path)

    assert service.apman_path() == apman
    assert service.apman_exists() is True


def test_apman_missing(tmp_path):
    service = KamsoftService(tmp_path)

    assert service.apman_exists() is False


def test_apman_ini(tmp_path):
    apman_ini = tmp_path / "APMAN.INI"
    apman_ini.write_text("test")

    service = KamsoftService(tmp_path)

    assert service.apman_ini_path() == apman_ini
    assert service.apman_ini_exists() is True


def test_apman_ini_missing(tmp_path):
    service = KamsoftService(tmp_path)

    assert service.apman_ini_exists() is False


def test_information(tmp_path):
    service = KamsoftService(tmp_path)

    information = service.information()

    assert information["install_path"] == str(tmp_path)
    assert information["exists"] is True
    assert information["apman"] == str(tmp_path / "APMAN.EXE")
    assert information["apman_exists"] is False
    assert information["version"] is None


def test_diagnostics(tmp_path):
    apman = tmp_path / "APMAN.EXE"
    apman_ini = tmp_path / "APMAN.INI"

    apman.write_text("test")
    apman_ini.write_text("test")

    service = KamsoftService(tmp_path)

    diagnostics = service.diagnostics()

    assert diagnostics["path_exists"] is True
    assert diagnostics["accessible"] is True
    assert diagnostics["apman_exists"] is True
    assert diagnostics["apman_ini_exists"] is True
    assert diagnostics["apman_size"] == 4
    assert diagnostics["apman_modified"] is not None


def test_diagnostics_without_path():
    service = KamsoftService()

    diagnostics = service.diagnostics()

    assert diagnostics["path_exists"] is False
    assert diagnostics["accessible"] is False
    assert diagnostics["apman_exists"] is False
    assert diagnostics["apman_ini_exists"] is False


def test_diagnostic_result_ok(tmp_path):
    (tmp_path / "APMAN.EXE").write_text("test")
    (tmp_path / "APMAN.INI").write_text("test")

    service = KamsoftService(tmp_path)

    result = service.diagnostic_result()

    assert result["status"] == "OK"
    assert result["errors"] == []
    assert result["warnings"] == []


def test_diagnostic_result_warning(tmp_path):
    (tmp_path / "APMAN.EXE").write_text("test")

    service = KamsoftService(tmp_path)

    result = service.diagnostic_result()

    assert result["status"] == "OSTRZEŻENIE"
    assert result["errors"] == []
    assert "Nie znaleziono APMAN.INI." in result["warnings"]


def test_diagnostic_result_error(tmp_path):
    service = KamsoftService(tmp_path)

    result = service.diagnostic_result()

    assert result["status"] == "BŁĄD"
    assert "Nie znaleziono APMAN.EXE." in result["errors"]