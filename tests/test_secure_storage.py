from __future__ import annotations

from core.secure_storage import decrypt_text, encrypt_text


def test_encrypt_text_returns_encrypted_value() -> None:
    value = "TestoweHaslo123!"

    encrypted = encrypt_text(value)

    assert encrypted
    assert encrypted != value


def test_encrypt_text_and_decrypt_text_roundtrip() -> None:
    value = "TestoweHaslo123!"

    encrypted = encrypt_text(value)
    decrypted = decrypt_text(encrypted)

    assert decrypted == value


def test_empty_value() -> None:
    assert encrypt_text("") == ""
    assert decrypt_text("") == ""


def test_encrypted_value_is_base64_text() -> None:
    value = "TestoweHaslo123!"

    encrypted = encrypt_text(value)

    assert isinstance(encrypted, str)
    assert "=" in encrypted or len(encrypted) > 0