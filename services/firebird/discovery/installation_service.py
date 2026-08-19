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

    def first_installation(self) -> FirebirdInstallation | None:

        roots = [
            Path(r"C:\Program Files\Firebird"),
            Path(r"C:\Program Files (x86)\Firebird"),
        ]

        for root in roots:

            if not root.exists():
                continue

            for folder in root.iterdir():

                if not folder.is_dir():
                    continue

                if not folder.name.lower().startswith("firebird"):
                    continue

                fb = FirebirdInstallation(
                    install_path=folder,
                    version=folder.name,
                )

                fb.fbclient = self.find(folder, "fbclient.dll")
                fb.isql = self.find(folder, "isql", "isql.exe", "isql.com")
                fb.gbak = self.find(folder, "gbak", "gbak.exe")
                fb.gfix = self.find(folder, "gfix", "gfix.exe")
                fb.gstat = self.find(folder, "gstat", "gstat.exe")
                fb.firebird_conf = self.find(folder, "firebird.conf")

                return fb

        return None

    def find(self, root: Path, *names: str) -> Path | None:

        wanted = {name.lower() for name in names}

        for file in root.rglob("*"):

            if file.name.lower() in wanted:
                return file

        return None

