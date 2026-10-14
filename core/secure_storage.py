from __future__ import annotations

import base64

import win32crypt


class SecureStorageError(RuntimeError):
    """Błąd bezpiecznego przechowywania danych."""


def encrypt_text(value: str) -> str:
    """
    Szyfruje tekst przy użyciu Windows DPAPI.

    Wynik jest kodowany Base64, aby można go było
    bezpiecznie przechowywać jako TEXT w SQLite.
    """

    if not value:
        return ""

    try:
        encrypted = win32crypt.CryptProtectData(
            value.encode("utf-8"),
            "Serwis Apteki MP",
            None,
            None,
            None,
            0,
        )

        return base64.b64encode(encrypted).decode("ascii")

    except Exception as exc:
        raise SecureStorageError(
            "Nie udało się zaszyfrować danych przy użyciu Windows DPAPI."
        ) from exc


def decrypt_text(value: str) -> str:
    """
    Odszyfrowuje tekst zabezpieczony Windows DPAPI.
    """

    if not value:
        return ""

    try:
        encrypted = base64.b64decode(
            value.encode("ascii"),
            validate=True,
        )

        result = win32crypt.CryptUnprotectData(
            encrypted,
            None,
            None,
            None,
            0,
        )

        decrypted = result[1]

        return decrypted.decode("utf-8")

    except Exception as exc:
        raise SecureStorageError(
            "Nie udało się odszyfrować danych przy użyciu Windows DPAPI."
        ) from exc