from __future__ import annotations

from unittest.mock import patch

from services.disk.disk_service import (
    DiskInfo,
    DiskService,
)


def test_get_disks_returns_disk_info():

    service = DiskService()

    def fake_disk_usage(path):

        if path == "C:\\":
            return (
                100 * 1024**3,
                60 * 1024**3,
                40 * 1024**3,
            )

        raise OSError()

    with patch(
        "services.disk.disk_service.shutil.disk_usage",
        side_effect=fake_disk_usage,
    ):

        result = service.get_disks()

    assert len(result) == 1

    disk = result[0]

    assert isinstance(disk, DiskInfo)
    assert disk.drive == "C:"
    assert disk.total_gb == 100
    assert disk.used_gb == 60
    assert disk.free_gb == 40
    assert disk.percent == 60


def test_get_disks_ignores_unavailable_drives():

    service = DiskService()

    def fake_disk_usage(path):

        if path == "C:\\":
            return (
                100 * 1024**3,
                25 * 1024**3,
                75 * 1024**3,
            )

        raise OSError()

    with patch(
        "services.disk.disk_service.shutil.disk_usage",
        side_effect=fake_disk_usage,
    ):

        result = service.get_disks()

    assert len(result) == 1
    assert result[0].drive == "C:"


def test_get_disks_calculates_percentage():

    service = DiskService()

    def fake_disk_usage(path):

        if path == "D:\\":
            return (
                200 * 1024**3,
                50 * 1024**3,
                150 * 1024**3,
            )

        raise OSError()

    with patch(
        "services.disk.disk_service.shutil.disk_usage",
        side_effect=fake_disk_usage,
    ):

        result = service.get_disks()

    assert len(result) == 1

    disk = result[0]

    assert disk.drive == "D:"
    assert disk.total_gb == 200
    assert disk.used_gb == 50
    assert disk.free_gb == 150
    assert disk.percent == 25


def test_get_disks_handles_zero_total():

    service = DiskService()

    def fake_disk_usage(path):

        if path == "E:\\":
            return (
                0,
                0,
                0,
            )

        raise OSError()

    with patch(
        "services.disk.disk_service.shutil.disk_usage",
        side_effect=fake_disk_usage,
    ):

        result = service.get_disks()

    assert len(result) == 1

    disk = result[0]

    assert disk.drive == "E:"
    assert disk.total_gb == 0
    assert disk.used_gb == 0
    assert disk.free_gb == 0
    assert disk.percent == 0


def test_get_disks_returns_empty_list_when_no_drives():

    service = DiskService()

    with patch(
        "services.disk.disk_service.shutil.disk_usage",
        side_effect=OSError(),
    ):

        result = service.get_disks()

    assert result == []