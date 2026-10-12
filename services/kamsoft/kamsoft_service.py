from __future__ import annotations

from pathlib import Path


class KamsoftService:
    def __init__(self, install_path: str | Path | None = None) -> None:
        self._install_path = Path(install_path) if install_path else None

    @property
    def install_path(self) -> Path | None:
        return self._install_path

    def set_install_path(self, path: str | Path) -> None:
        self._install_path = Path(path)

    def exists(self) -> bool:
        return self._install_path is not None and self._install_path.is_dir()

    def apman_path(self) -> Path | None:
        if self._install_path is None:
            return None

        return self._install_path / "APMAN.EXE"

    def apman_exists(self) -> bool:
        path = self.apman_path()

        return path is not None and path.is_file()

    def apman_ini_path(self) -> Path | None:
        if self._install_path is None:
            return None

        return self._install_path / "APMAN.INI"

    def apman_ini_exists(self) -> bool:
        path = self.apman_ini_path()

        return path is not None and path.is_file()

    def version(self) -> str | None:
        path = self.apman_path()

        if path is None or not path.is_file():
            return None

        try:
            import win32api

            info = win32api.GetFileVersionInfo(str(path), "\\")

            ms = info["FileVersionMS"]
            ls = info["FileVersionLS"]

            return (
                f"{ms >> 16}."
                f"{ms & 0xFFFF}."
                f"{ls >> 16}."
                f"{ls & 0xFFFF}"
            )
        except Exception:
            return None

    def diagnostics(self) -> dict[str, object]:
        if self._install_path is None:
            return {
                "path_exists": False,
                "accessible": False,
                "apman_exists": False,
                "apman_ini_exists": False,
                "apman_size": None,
                "apman_modified": None,
            }

        path_exists = self._install_path.is_dir()

        if not path_exists:
            return {
                "path_exists": False,
                "accessible": False,
                "apman_exists": False,
                "apman_ini_exists": False,
                "apman_size": None,
                "apman_modified": None,
            }

        try:
            accessible = self._install_path.exists()

            apman = self.apman_path()
            apman_ini = self.apman_ini_path()

            apman_exists = apman is not None and apman.is_file()
            apman_ini_exists = (
                apman_ini is not None and apman_ini.is_file()
            )

            return {
                "path_exists": True,
                "accessible": accessible,
                "apman_exists": apman_exists,
                "apman_ini_exists": apman_ini_exists,
                "apman_size": (
                    apman.stat().st_size
                    if apman_exists
                    else None
                ),
                "apman_modified": (
                    apman.stat().st_mtime
                    if apman_exists
                    else None
                ),
            }

        except OSError:
            return {
                "path_exists": True,
                "accessible": False,
                "apman_exists": False,
                "apman_ini_exists": False,
                "apman_size": None,
                "apman_modified": None,
            }

    def diagnostic_result(self) -> dict[str, object]:
        diagnostics = self.diagnostics()

        errors: list[str] = []
        warnings: list[str] = []

        if not diagnostics["path_exists"]:
            errors.append("Nie znaleziono katalogu KS-AOW.")

        elif not diagnostics["accessible"]:
            errors.append("Brak dostępu do katalogu KS-AOW.")

        if not diagnostics["apman_exists"]:
            errors.append("Nie znaleziono APMAN.EXE.")

        if not diagnostics["apman_ini_exists"]:
            warnings.append("Nie znaleziono APMAN.INI.")

        if errors:
            status = "BŁĄD"
        elif warnings:
            status = "OSTRZEŻENIE"
        else:
            status = "OK"

        return {
            "status": status,
            "errors": errors,
            "warnings": warnings,
            "diagnostics": diagnostics,
        }

    def information(self) -> dict[str, object]:
        return {
            "install_path": (
                str(self._install_path)
                if self._install_path
                else None
            ),
            "exists": self.exists(),
            "apman": (
                str(self.apman_path())
                if self.apman_path()
                else None
            ),
            "apman_exists": self.apman_exists(),
            "version": self.version(),
        }