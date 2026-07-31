from __future__ import annotations

from pathlib import Path
import winreg

from models.firebird_installation import FirebirdInstallation


class InstallationService:
    """
    Wyszukuje wszystkie zainstalowane wersje Firebird.
    """

    REGISTRY_KEYS = (
        r"SOFTWARE\Firebird Project\Firebird Server\Instances",
        r"SOFTWARE\WOW6432Node\Firebird Project\Firebird Server\Instances",
    )

    def find_installations(self) -> list[FirebirdInstallation]:

        installations: list[FirebirdInstallation] = []

        for registry_key in self.REGISTRY_KEYS:

            try:
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    registry_key,
                ) as key:

                    count = winreg.QueryInfoKey(key)[1]

                    for index in range(count):

                        name, value, _ = winreg.EnumValue(key, index)

                        path = Path(value)

                        installations.append(
                            FirebirdInstallation(
                                version=name,
                                install_path=path,
                                bin_path=path / "bin",
                                firebird_exe=path / "bin" / "firebird.exe",
                                fbclient_path=path / "fbclient.dll",
                                service_name=f"FirebirdServer{name.replace('.', '')}",
                            )
                        )

            except FileNotFoundError:
                continue

        return installations

    def first_installation(self) -> FirebirdInstallation | None:
        """
        Zwraca pierwszą znalezioną instalację Firebird lub None.
        """

        installations = self.find_installations()

        if not installations:
            return None

        return installations[0]