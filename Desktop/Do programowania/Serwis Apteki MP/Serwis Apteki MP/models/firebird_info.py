from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FirebirdInfo:
    """
    Informacje o zainstalowanym Firebirdzie.
    """

    installed: bool = False

    version: str = ""
    architecture: str = ""

    service_name: str = ""
    service_status: str = ""

    install_path: Path | None = None
    bin_path: Path | None = None

    gbak_path: Path | None = None
    gfix_path: Path | None = None
    isql_path: Path | None = None
    fbclient_path: Path | None = None

    firebird_conf: Path | None = None

    port: int = 3050

    guardian: bool = False