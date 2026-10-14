from __future__ import annotations

import os
import sys
from configparser import ConfigParser
from pathlib import Path

from core.secure_storage import (
    SecureStorageError,
    decrypt_text,
    encrypt_text,
)
from core.settings import settings


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.ini"


def get_application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return BASE_DIR.parent


def get_application_data_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        return Path(local_app_data) / "SerwisAptekiMP"

    return Path.home() / "AppData" / "Local" / "SerwisAptekiMP"


def get_config_path() -> Path:
    if getattr(sys, "frozen", False):
        return get_application_data_dir() / "config.ini"

    return DEFAULT_CONFIG_PATH


class Config:
    def __init__(
        self,
        path: Path | str | None = None,
        settings_store=None,
    ):
        self.path = Path(path) if path is not None else get_config_path()
        self.parser = ConfigParser()
        self._password_override: str | None = None

        if settings_store is not None:
            self._settings = settings_store
        elif self._is_default_config():
            self._settings = settings
        else:
            self._settings = None

        if not self.path.exists():
            self._migrate_old_frozen_config()

        if not self.path.exists():
            self._create_default_config()

        self.parser.read(self.path, encoding="utf-8")

    def _is_default_config(self) -> bool:
        try:
            return self.path.resolve() == DEFAULT_CONFIG_PATH.resolve()
        except OSError:
            return self.path == DEFAULT_CONFIG_PATH

    def _migrate_old_frozen_config(self) -> None:
        if not getattr(sys, "frozen", False):
            return

        old_config = (
            get_application_dir()
            / "config"
            / "config.ini"
        )

        if not old_config.exists():
            return

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.path.write_text(
            old_config.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def _create_default_config(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        parser = ConfigParser()

        parser["Firebird"] = {
            "database": r"C:\KSBAZA\KS-APW\WAPTEKA.FDB",
            "user": "SYSDBA",
            "password": "",
        }

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as config_file:
            parser.write(config_file)

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

    @user.setter
    def user(self, value: str) -> None:
        self.save_user(value)

    @property
    def password(self) -> str:
        if self._password_override is not None:
            return self._password_override

        if self._settings is not None:
            encrypted = self._settings.get(
                "firebird.password",
                "",
            )

            if encrypted:
                try:
                    return decrypt_text(encrypted)
                except SecureStorageError:
                    raise

        legacy_password = self.parser.get(
            "Firebird",
            "password",
            fallback="",
        )

        if legacy_password:
            if self._settings is not None:
                self.save_password(legacy_password)

            return legacy_password

        return ""

    @password.setter
    def password(self, value: str) -> None:
        self._password_override = value

    def save_password(self, value: str) -> None:
        if self._settings is None:
            raise RuntimeError(
                "Bezpieczny magazyn ustawień nie jest dostępny "
                "dla tego pliku konfiguracji."
            )

        if value:
            encrypted = encrypt_text(value)
            self._settings.set(
                "firebird.password",
                encrypted,
            )
        else:
            self._settings.set(
                "firebird.password",
                "",
            )

        self._password_override = value
        self._remove_plaintext_password()

    def save_user(self, value: str) -> None:
        if not self.parser.has_section("Firebird"):
            self.parser.add_section("Firebird")

        self.parser.set(
            "Firebird",
            "user",
            value,
        )

        self._write_config()

    def _remove_plaintext_password(self) -> None:
        if not self.parser.has_section("Firebird"):
            return

        if not self.parser.has_option(
            "Firebird",
            "password",
        ):
            return

        self.parser.set(
            "Firebird",
            "password",
            "",
        )

        self._write_config()

    def _write_config(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as config_file:
            self.parser.write(config_file)