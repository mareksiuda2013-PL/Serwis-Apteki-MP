from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FirebirdInfo:
    """
    Informacje o instalacji Firebird
    oraz skonfigurowanej bazie danych.
    """

    # ==================================================
    # FIREBIRD
    # ==================================================

    installed: bool = False
    exists: bool = False

    version: str = ""
    architecture: str = ""

    service_name: str = ""
    service_status: str = ""

    install_path: Path | None = None
    bin_path: Path | None = None

    port: int = 3050
    guardian: bool = False

    # ==================================================
    # NARZĘDZIA FIREBIRD
    # ==================================================

    gbak_path: Path | None = None
    gfix_path: Path | None = None
    isql_path: Path | None = None
    fbclient_path: Path | None = None
    firebird_conf: Path | None = None

    gbak_exists: bool = False
    gfix_exists: bool = False
    isql_exists: bool = False
    fbclient_exists: bool = False
    firebird_conf_exists: bool = False

    # ==================================================
    # BAZA DANYCH
    # ==================================================

    database_path: str = ""

    database_exists: bool = False
    database_size_gb: float = 0.0

    database_modified: str = ""

    # ==================================================
    # PARAMETRY BAZY
    # ==================================================

    ods: str = ""
    sql_dialect: int = 0
    page_size: int = 0
    tables: int = 0