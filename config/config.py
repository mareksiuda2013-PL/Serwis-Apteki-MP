from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path


class Config:

    def __init__(self):

        self.path = Path(__file__).resolve().parent / "config.ini"


        self.parser = ConfigParser()

        self.parser.read(self.path, encoding="utf-8")


    @property
    def database(self) -> str:
        return self.parser.get("Firebird", "database")

    @property
    def user(self) -> str:
        return self.parser.get("Firebird", "user")

    @property
    def password(self) -> str:
        return self.parser.get("Firebird", "password")