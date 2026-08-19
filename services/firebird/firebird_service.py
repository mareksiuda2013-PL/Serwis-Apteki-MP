from __future__ import annotations

from config import Config
from core.logger import logger
from models import FirebirdInfo

from .database_service import DatabaseService
from .discovery.installation_service import InstallationService
from .service_service import ServiceService
from .statistics_service import StatisticsService


class FirebirdService:
    """
    Główny serwis odpowiedzialny za informacje
    dotyczące instalacji Firebird oraz bazy danych.
    """

    def __init__(self):

        self.cfg = Config()

        self.installation = InstallationService()
        self.database = DatabaseService()
        self.statistics = StatisticsService()
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

        info.version = fb.version or "-"

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

        info.database_exists = (
            self.database.exists(database_path)
        )

        info.database_size_gb = (
            self.database.size_gb(database_path)
        )

        # ==================================================
        # STATYSTYKI GSTAT
        # ==================================================

        if info.database_exists:

            try:

                stats = (
                    StatisticsService(
                        database=database_path
                    ).statistics()
                )

                info.statistics = stats

                # ------------------------------------------
                # Dane podstawowe
                # ------------------------------------------

                info.ods = stats.ods
                info.page_size = stats.page_size

                info.sql_dialect = (
                    stats.database_dialect
                )

                # ------------------------------------------
                # LOG GSTAT
                # ------------------------------------------

                logger.info(
                    f"GSTAT | "
                    f"ODS={stats.ods} | "
                    f"page_size={stats.page_size} | "
                    f"buffers={stats.page_buffers} | "
                    f"sweep={stats.sweep_interval} | "
                    f"forced_writes={stats.forced_writes}"
                )

            except Exception as exc:

                logger.error(
                    f"GSTAT | nie udało się pobrać "
                    f"statystyk: {exc}"
                )

        # ==================================================
        # INFORMACJE Z DATABASE SERVICE
        # ==================================================

        if info.database_exists:

            try:

                info.tables = (
                    self.database.tables()
                    or 0
                )

            except Exception as exc:

                logger.error(
                    f"FirebirdService | "
                    f"nie udało się pobrać liczby tabel: "
                    f"{exc}"
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
                self.service.status(
                    service_name
                )
            )

        # ==================================================
        # LOG INFORMACJI
        # ==================================================

        logger.info(
            f"Firebird INFO | "
            f"baza={info.database_path} | "
            f"istnieje={info.database_exists} | "
            f"rozmiar={info.database_size_gb:.2f} GB | "
            f"ODS={info.ods} | "
            f"page_size={info.page_size} | "
            f"dialect={info.sql_dialect} | "
            f"tabele={info.tables}"
        )

        return info