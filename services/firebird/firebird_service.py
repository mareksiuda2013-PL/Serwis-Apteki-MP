from __future__ import annotations

from config import Config
from models import FirebirdInfo

from .database_service import DatabaseService
from .installation_service import InstallationService
from .service_service import ServiceService


class FirebirdService:
    """
    Główny serwis odpowiedzialny za informacje
    dotyczące instalacji Firebird oraz bazy danych.
    """

    def __init__(self):

        self.cfg = Config()

        self.installation = InstallationService()
        self.database = DatabaseService()
        self.service = ServiceService()

    # ==================================================
    # FIREBIRD INFO
    # ==================================================

    def get_info(
        self,
        database: str | None = None,
    ) -> FirebirdInfo:

        info = FirebirdInfo()

        # ==================================================
        # INSTALACJA FIREBIRD
        # ==================================================

        fb = self.installation.first_installation()

        if fb is None:
            return info

        info.installed = True
        info.exists = True

        info.install_path = fb.install_path
        info.bin_path = fb.install_path

        info.gbak_path = fb.gbak
        info.gfix_path = fb.gfix
        info.isql_path = fb.isql

        info.fbclient_path = fb.fbclient
        info.firebird_conf = fb.firebird_conf

        info.gbak_exists = fb.gbak is not None
        info.gfix_exists = fb.gfix is not None
        info.isql_exists = fb.isql is not None
        info.fbclient_exists = fb.fbclient is not None
        info.firebird_conf_exists = (
            fb.firebird_conf is not None
        )

        # ==================================================
        # BAZA DANYCH
        # ==================================================

        database_path = (
            database
            if database
            else self.cfg.database
        )

        info.database_path = database_path

        # --------------------------------------------------
        # PLIK BAZY
        # --------------------------------------------------

        info.database_exists = (
            self.database.exists(database_path)
        )

        info.database_size_gb = (
            self.database.size_gb(database_path)
        )

        # --------------------------------------------------
        # INFORMACJE Z FIREBIRD
        # --------------------------------------------------

        try:

            info.version = self.database.version()
            info.ods = self.database.ods()
            info.page_size = self.database.page_size()
            info.sql_dialect = self.database.sql_dialect()
            info.tables = self.database.tables()

        except Exception as exc:

            print(
                "FirebirdService: "
                f"nie udało się pobrać informacji z bazy: {exc}"
            )

        # ==================================================
        # USŁUGA FIREBIRD
        # ==================================================

        service_name = (
            self.service.find_firebird_service()
        )

        if service_name:

            info.service_name = service_name

            info.service_status = (
                self.service.status(service_name)
            )

        # ==================================================
        # DEBUG
        # ==================================================

        print(
            "FirebirdService DATABASE:",
            info.database_path,
        )

        print(
            "FirebirdService EXISTS:",
            info.database_exists,
        )

        print(
            "FirebirdService SIZE:",
            info.database_size_gb,
        )

        return info