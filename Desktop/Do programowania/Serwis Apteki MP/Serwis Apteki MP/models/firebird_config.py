from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FirebirdConfig:
    """
    Konfiguracja odczytana z pliku firebird.conf.
    """

    path: Path | None = None

    exists: bool = False

    remote_service_port: int = 3050

    guardian: bool = False

    root_directory: str = ""

    temp_directories: str = ""

    raw: dict[str, str] | None = None