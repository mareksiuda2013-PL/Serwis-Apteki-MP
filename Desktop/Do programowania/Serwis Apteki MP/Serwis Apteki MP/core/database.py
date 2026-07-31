import sqlite3
import os


DATABASE_PATH = "data/SerwisMP.db"


def initialize_database():

    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT
        )
    """)

    conn.commit()

    conn.close()