from __future__ import annotations

from unittest.mock import MagicMock, patch

from modules.dashboard.controller import (
    DashboardController,
)


def test_controller_creates_all_services():

    with (
        patch(
            "modules.dashboard.controller.SystemService"
        ) as system_cls,
        patch(
            "modules.dashboard.controller.FirebirdService"
        ) as firebird_cls,
        patch(
            "modules.dashboard.controller.DiskService"
        ) as disk_cls,
        patch(
            "modules.dashboard.controller.NetworkService"
        ) as network_cls,
    ):

        controller = DashboardController()

    assert controller.system_service is (
        system_cls.return_value
    )

    assert controller.firebird_service is (
        firebird_cls.return_value
    )

    assert controller.disk_service is (
        disk_cls.return_value
    )

    assert controller.network_service is (
        network_cls.return_value
    )


def test_system_info():

    system_info = MagicMock()

    with patch(
        "modules.dashboard.controller.SystemService"
    ) as service_class:

        service_class.return_value.get_info.return_value = (
            system_info
        )

        controller = DashboardController()

        result = controller.system_info()

    assert result is system_info

    service_class.return_value.get_info.assert_called_once()


def test_firebird_info():

    firebird_info = MagicMock()

    with patch(
        "modules.dashboard.controller.FirebirdService"
    ) as service_class:

        service_class.return_value.get_info.return_value = (
            firebird_info
        )

        controller = DashboardController()

        result = controller.firebird_info()

    assert result is firebird_info

    service_class.return_value.get_info.assert_called_once()


def test_disk_info():

    disks = [
        MagicMock(),
        MagicMock(),
    ]

    with patch(
        "modules.dashboard.controller.DiskService"
    ) as service_class:

        service_class.return_value.get_disks.return_value = (
            disks
        )

        controller = DashboardController()

        result = controller.disk_info()

    assert result is disks

    service_class.return_value.get_disks.assert_called_once()


def test_network_info():

    network_info = MagicMock()

    with patch(
        "modules.dashboard.controller.NetworkService"
    ) as service_class:

        service_class.return_value.get_info.return_value = (
            network_info
        )

        controller = DashboardController()

        result = controller.network_info()

    assert result is network_info

    service_class.return_value.get_info.assert_called_once()