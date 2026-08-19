from __future__ import annotations

from pathlib import Path

from services.firebird.client import FirebirdClient
from services.firebird.discovery.installation_service import InstallationService


class DatabaseService:

    def __init__(self):

        installation = InstallationService().first_installation()

        if installation is None:
            raise RuntimeError(
                "Nie znaleziono instalacji Firebird."
            )

        self.client = FirebirdClient(installation)

    # ==================================================
    # DATABASE FILE
    # ==================================================

    def exists(self, database_path: str) -> bool:

        if not database_path:
            return False

        return Path(database_path).exists()

    # --------------------------------------------------

    def size_gb(self, database_path: str) -> float:

        if not database_path:
            return 0.0

        path = Path(database_path)

        if not path.exists():
            return 0.0

        try:

            size_bytes = path.stat().st_size

            return size_bytes / (1024 ** 3)

        except OSError:

            return 0.0

    # ==================================================
    # FIREBIRD INFORMATION
    # ==================================================

    def version(self) -> str:

        return self.client.fetch_one(
            """
            SELECT
                rdb$get_context(
                    'SYSTEM',
                    'ENGINE_VERSION'
                )
            FROM rdb$database;
            """
        ) or ""

    # --------------------------------------------------

    def sql_dialect(self) -> int:

        value = self.client.fetch_one(
            """
            SELECT MON$SQL_DIALECT
            FROM MON$DATABASE;
            """
        )

        return int(value)

    # --------------------------------------------------

    def page_size(self) -> int:

        value = self.client.fetch_one(
            """
            SELECT MON$PAGE_SIZE
            FROM MON$DATABASE;
            """
        )

        return int(value)

    # --------------------------------------------------

    def ods(self) -> str:

        major = self.client.fetch_one(
            """
            SELECT MON$ODS_MAJOR
            FROM MON$DATABASE;
            """
        )

        minor = self.client.fetch_one(
            """
            SELECT MON$ODS_MINOR
            FROM MON$DATABASE;
            """
        )

        return f"{major}.{minor}"

    # --------------------------------------------------

    def tables(self) -> int:

        value = self.client.fetch_one(
            """
            SELECT COUNT(*)
            FROM RDB$RELATIONS
            WHERE RDB$SYSTEM_FLAG = 0;
            """
        )

        return int(value)