from __future__ import annotations

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "SerwisMP.db"


class Settings:
    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = Path(db_path)

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings
            (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        self.connection.commit()

    def get(self, key: str, default=None):
        self.cursor.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        return default

    def set(self, key: str, value) -> None:
        self.cursor.execute(
            """
            INSERT INTO settings(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
            """,
            (key, str(value)),
        )

        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


settings = Settings()