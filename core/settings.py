import sqlite3
from pathlib import Path


DB_PATH = Path("data") / "SerwisMP.db"


class Settings:

    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings
            (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.connection.commit()

    def get(self, key, default=None):

        self.cursor.execute(
            "SELECT value FROM settings WHERE key=?",
            (key,)
        )

        row = self.cursor.fetchone()

        if row:
            return row[0]

        return default

    def set(self, key, value):

        self.cursor.execute("""
            INSERT INTO settings(key,value)
            VALUES(?,?)
            ON CONFLICT(key)
            DO UPDATE SET value=excluded.value
        """, (key, value))

        self.connection.commit()


settings = Settings()
