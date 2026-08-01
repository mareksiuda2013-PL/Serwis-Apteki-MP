from __future__ import annotations

from datetime import datetime
from pathlib import Path

from models import DatabaseInfo


class DatabaseService:

    def inspect(self, database: str | Path) -> DatabaseInfo:

        info = DatabaseInfo()

        path = Path(database)

        info.path = path

        if not path.exists():
            return info

        info.exists = True

        stat = path.stat()

        info.size_bytes = stat.st_size
        info.size_mb = round(stat.st_size / 1024 / 1024, 2)
        info.size_gb = round(stat.st_size / 1024 / 1024 / 1024, 2)

        info.modified = datetime.fromtimestamp(
            stat.st_mtime
        )

        return info