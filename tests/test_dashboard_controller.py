from __future__ import annotations

from unittest.mock import MagicMock, patch

from modules.dashboard.controller import (
    DashboardController,
)


def test_system_info_returns_service_result():

    expected = MagicMock(
        computer_name="TEST-PC",
        user="TEST",
    )

    with patch(
        "modules.dashboard.controller.SystemService"
    ) as service_class:

        service = service_class.return_value
        service.get_info.return_value = expected

        controller = DashboardController()

        result = controller.system_info()

    assert result is expected

    service_class.assert_called_once_with()
    service.get_info.assert_called_once_with()


def test_controller_creates_system_service():

    with patch(
        "modules.dashboard.controller.SystemService"
    ) as service_class:

        controller = DashboardController()

    service_class.assert_called_once_with()

    assert (
        controller.system_service
        is service_class.return_value
    )