from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

from core.secure_storage import (
    decrypt_text,
    encrypt_text,
    SecureStorageError,
)
from core.settings import settings


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = BASE_DIR / "config.ini"


class Config:
    def __init__(
        self,
        path: Path | str | None = None,
        settings_store=None,
    ):
        self.path = (
            Path(path)
            if path is not None
            else DEFAULT_CONFIG_PATH
        )

        self.parser = ConfigParser()

        self.parser.read(
            self.path,
            encoding="utf-8",
        )

        self._password_override: str | None = None

        if settings_store is not None:
            self._settings = settings_store
        elif self._is_default_config():
            self._settings = settings
        else:
            self._settings = None

    def _is_default_config(self) -> bool:
        """Sprawdza, czy używany jest produkcyjny config.ini."""

        try:
            return (
                self.path.resolve()
                == DEFAULT_CONFIG_PATH.resolve()
            )
        except OSError:
            return self.path == DEFAULT_CONFIG_PATH

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
        """
        Zwraca hasło Firebird.

        Kolejność:
        1. wartość ustawiona w pamięci obiektu,
        2. zaszyfrowane hasło w SQLite,
        3. stare hasło z config.ini.

        Stare hasło z produkcyjnego config.ini zostanie
        automatycznie zmigrowane do bezpiecznego magazynu.
        """

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
        """
        Ustawia hasło tylko w pamięci bieżącego obiektu.

        Dzięki temu istniejące testy i usługi mogą nadal
        wykonywać np. config.password = "masterkey",
        bez zapisywania hasła do produkcyjnej bazy ustawień.
        """

        self._password_override = value

    def save_password(self, value: str) -> None:
        """
        Zapisuje hasło w bezpiecznym magazynie Windows DPAPI.

        Jawne hasło z config.ini jest usuwane.
        """

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
        """Zapisuje użytkownika Firebird do config.ini."""

        if not self.parser.has_section("Firebird"):
            self.parser.add_section("Firebird")

        self.parser.set(
            "Firebird",
            "user",
            value,
        )

        self._write_config()

    def _remove_plaintext_password(self) -> None:
        """Usuwa jawne hasło z config.ini."""

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
        """Zapisuje aktualną konfigurację do pliku."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as config_file:
            self.parser.write(config_file)