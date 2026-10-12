from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    def __init__(self, path: Path | str | None = None):
        self.path = (
            Path(path)
            if path is not None
            else BASE_DIR / "config.ini"
        )

        self.parser = ConfigParser()

        self.parser.read(
            self.path,
            encoding="utf-8",
        )

    @property
    def database(self) -> str:
        return self.parser.get(
            "Firebird",
            "database",
        )

    @property
    def user(self) -> str:
        return self.parser.get(
            "Firebird",
            "user",
        )

    @property
    def password(self) -> str:
        return self.parser.get(
            "Firebird",
            "password",
        )