from __future__ import annotations

from services.firebird.client import FirebirdClient
from services.firebird.installation_service import InstallationService


class DatabaseService:

    def __init__(self):

        installation = InstallationService().first_installation()

        if installation is None:
            raise RuntimeError("Nie znaleziono instalacji Firebird.")

        self.client = FirebirdClient(installation)

    def version(self) -> str:

        return self.client.fetch_one(
            "SELECT rdb$get_context('SYSTEM','ENGINE_VERSION') FROM rdb$database;"
        ) or ""

    def sql_dialect(self) -> int:

        value = self.client.fetch_one(
            "SELECT MON$SQL_DIALECT FROM MON$DATABASE;"
        )

        return int(value)

    def page_size(self) -> int:

        value = self.client.fetch_one(
            "SELECT MON$PAGE_SIZE FROM MON$DATABASE;"
        )

        return int(value)

    def ods(self) -> str:

        major = self.client.fetch_one(
            "SELECT MON$ODS_MAJOR FROM MON$DATABASE;"
        )

        minor = self.client.fetch_one(
            "SELECT MON$ODS_MINOR FROM MON$DATABASE;"
        )

        return f"{major}.{minor}"

    def tables(self) -> int:

        value = self.client.fetch_one(
            """
            SELECT COUNT(*)
            FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0;
            """
        )

        return int(value)