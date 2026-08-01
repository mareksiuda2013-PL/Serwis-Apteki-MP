from __future__ import annotations

from models import FirebirdInfo

from .database_service import DatabaseService
from .installation_service import InstallationService
from .service_service import ServiceService


class FirebirdService:

    def __init__(self):

        self.installation = InstallationService()
        self.database = DatabaseService()
        self.service = ServiceService()

    def get_info(self) -> FirebirdInfo:

        info = FirebirdInfo()

        fb = self.installation.first_installation()

        if fb is None:
            return info

        info.installed = True
        info.exists = True

        info.version = self.database.version()
        info.ods = self.database.ods()
        info.page_size = self.database.page_size()
        info.sql_dialect = self.database.sql_dialect()
        info.tables = self.database.tables()

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
        info.firebird_conf_exists = fb.firebird_conf is not None

        return info