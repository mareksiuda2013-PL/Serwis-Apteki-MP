from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FirebirdInstallation:
    install_path: Path
    version: str = ""

    fbclient: Path | None = None
    isql: Path | None = None
    gbak: Path | None = None
    gfix: Path | None = None
    gstat: Path | None = None
    firebird_conf: Path | None = None


class InstallationService:

    DEFAULT_ROOTS = (
        Path(r"C:\Program Files\Firebird"),
        Path(r"C:\Program Files (x86)\Firebird"),
    )

    def __init__(
        self,
        roots: tuple[Path, ...] | None = None,
    ) -> None:

        self.roots = (
            roots
            if roots is not None
            else self.DEFAULT_ROOTS
        )

    # ==================================================
    # FIRST INSTALLATION
    # ==================================================

    def first_installation(
        self,
    ) -> FirebirdInstallation | None:

        for root in self.roots:

            if not root.exists():
                continue

            for folder in root.iterdir():

                if not folder.is_dir():
                    continue

                if not folder.name.lower().startswith(
                    "firebird"
                ):
                    continue

                installation = FirebirdInstallation(
                    install_path=folder,
                    version=folder.name,
                )

                installation.fbclient = self.find(
                    folder,
                    "fbclient.dll",
                )

                installation.isql = self.find(
                    folder,
                    "isql",
                    "isql.exe",
                    "isql.com",
                )

                installation.gbak = self.find(
                    folder,
                    "gbak",
                    "gbak.exe",
                )

                installation.gfix = self.find(
                    folder,
                    "gfix",
                    "gfix.exe",
                )

                installation.gstat = self.find(
                    folder,
                    "gstat",
                    "gstat.exe",
                )

                installation.firebird_conf = self.find(
                    folder,
                    "firebird.conf",
                )

                return installation

        return None

    # ==================================================
    # FIND
    # ==================================================

    def find(
        self,
        root: Path,
        *names: str,
    ) -> Path | None:

        wanted = {
            name.lower()
            for name in names
        }

        for file in root.rglob("*"):

            if file.is_file() and (
                file.name.lower() in wanted
            ):
                return file

        return None