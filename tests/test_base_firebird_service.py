from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.firebird.base_firebird_service import BaseFirebirdService


def installation_mock():
    installation = MagicMock()

    installation.install_path = Path("C:/Firebird")
    installation.gbak = Path("C:/Firebird/bin/gbak.exe")
    installation.gfix = Path("C:/Firebird/bin/gfix.exe")
    installation.gstat = Path("C:/Firebird/bin/gstat.exe")
    installation.isql = Path("C:/Firebird/bin/isql.exe")

    return installation


def test_uses_database_from_config():

    cfg = MagicMock()
    cfg.database = r"C:\KSBAZA\KS-APW\WAPTEKA.FDB"

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ) as runner_cls,
    ):
        installation_cls.return_value.first_installation.return_value = (
            installation_mock()
        )

        service = BaseFirebirdService()

    assert service.cfg is cfg
    assert service.database == Path(cfg.database)
    assert service.runner is runner_cls.return_value


def test_uses_provided_database():

    cfg = MagicMock()
    cfg.database = "ignored.fdb"

    custom_database = Path(r"D:\TEST\CUSTOM.FDB")

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ),
    ):
        installation_cls.return_value.first_installation.return_value = (
            installation_mock()
        )

        service = BaseFirebirdService(
            database=custom_database
        )

    assert service.database == custom_database


def test_stores_installation():

    cfg = MagicMock()
    cfg.database = "db.fdb"

    installation = installation_mock()

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ),
    ):
        installation_cls.return_value.first_installation.return_value = (
            installation
        )

        service = BaseFirebirdService()

    assert service.installation is installation


def test_raises_when_installation_missing():

    cfg = MagicMock()
    cfg.database = "db.fdb"

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
    ):
        installation_cls.return_value.first_installation.return_value = None

        with pytest.raises(RuntimeError) as exc:
            BaseFirebirdService()

    assert str(exc.value) == (
        "Nie znaleziono instalacji Firebird."
    )


def test_creates_process_runner():

    cfg = MagicMock()
    cfg.database = "db.fdb"

    with (
        patch(
            "services.firebird.base_firebird_service.Config",
            return_value=cfg,
        ),
        patch(
            "services.firebird.base_firebird_service.InstallationService"
        ) as installation_cls,
        patch(
            "services.firebird.base_firebird_service.ProcessRunner"
        ) as runner_cls,
    ):
        installation_cls.return_value.first_installation.return_value = (
            installation_mock()
        )

        service = BaseFirebirdService()

    runner_cls.assert_called_once_with()
    assert service.runner is runner_cls.return_value