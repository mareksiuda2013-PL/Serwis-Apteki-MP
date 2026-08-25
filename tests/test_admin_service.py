from __future__ import annotations

from unittest.mock import patch

from services.system.admin_service import AdminService


# ==========================================================
# IS ADMIN
# ==========================================================


def test_is_admin_returns_true():

    with patch(
        "services.system.admin_service.ctypes.windll.shell32.IsUserAnAdmin",
        return_value=1,
    ):

        assert AdminService.is_admin() is True


def test_is_admin_returns_false():

    with patch(
        "services.system.admin_service.ctypes.windll.shell32.IsUserAnAdmin",
        return_value=0,
    ):

        assert AdminService.is_admin() is False


def test_is_admin_handles_exception():

    with patch(
        "services.system.admin_service.ctypes.windll.shell32.IsUserAnAdmin",
        side_effect=RuntimeError(
            "TEST ERROR"
        ),
    ):

        assert AdminService.is_admin() is False


# ==========================================================
# STATUS
# ==========================================================


def test_status_returns_administrator():

    with patch.object(
        AdminService,
        "is_admin",
        return_value=True,
    ):

        assert (
            AdminService.status()
            == "Administrator"
        )


def test_status_returns_standard_user():

    with patch.object(
        AdminService,
        "is_admin",
        return_value=False,
    ):

        assert (
            AdminService.status()
            == "Standardowy użytkownik"
        )