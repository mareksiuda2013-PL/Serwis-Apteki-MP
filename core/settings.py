from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path


# ==========================================================
# ŚCIEŻKI
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


def get_application_data_dir() -> Path:
    """
    Zwraca katalog na dane użytkownika aplikacji.

    Tryb źródłowy:
        katalog projektu / data

    Tryb EXE:
        %LOCALAPPDATA% / SerwisAptekiMP
    """

    if getattr(sys, "frozen", False):

        local_app_data = os.environ.get(
            "LOCALAPPDATA"
        )

        if local_app_data:

            return (
                Path(local_app_data)
                / "SerwisAptekiMP"
            )

        return (
            Path.home()
            / "AppData"
            / "Local"
            / "SerwisAptekiMP"
        )

    return BASE_DIR / "data"


DB_PATH = (
    get_application_data_dir()
    / "SerwisMP.db"
)


# ==========================================================
# SETTINGS
# ==========================================================

class Settings:

    def __init__(
        self,
        db_path: Path | str = DB_PATH,
    ) -> None:

        self.db_path = Path(
            db_path
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.db_path
        )

        self.cursor = (
            self.connection.cursor()
        )

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

    # ======================================================
    # GET
    # ======================================================

    def get(
        self,
        key: str,
        default=None,
    ):

        self.cursor.execute(
            """
            SELECT value
            FROM settings
            WHERE key=?
            """,
            (key,),
        )

        row = self.cursor.fetchone()

        if row is not None:
            return row[0]

        return default

    # ======================================================
    # SET
    # ======================================================

    def set(
        self,
        key: str,
        value,
    ) -> None:

        self.cursor.execute(
            """
            INSERT INTO settings(key, value)
            VALUES(?, ?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
            """,
            (
                key,
                str(value),
            ),
        )

        self.connection.commit()

    # ======================================================
    # CLOSE
    # ======================================================

    def close(self) -> None:

        self.connection.close()


# ==========================================================
# GLOBAL SETTINGS
# ==========================================================

settings = Settings()