from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from models.system_report import (
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
)
from services.system_report_service import SystemReportService


def create_service(
    system_info=None,
    network_info=None,
    printers=None,
    default_printer="",
    kamsoft_result=None,
):
    system_service = MagicMock()
    network_service = MagicMock()
    printer_service = MagicMock()
    kamsoft_service = MagicMock()

    system_service.get_info.return_value = system_info
    network_service.get_info.return_value = network_info
    printer_service.list_printers.return_value = printers or []
    printer_service.get_default_printer.return_value = default_printer
    kamsoft_service.diagnostic_result.return_value = (
        kamsoft_result
        if kamsoft_result is not None
        else {
            "status": "OK",
            "errors": [],
            "warnings": [],
        }
    )

    return SystemReportService(
        system_service=system_service,
        network_service=network_service,
        printer_service=printer_service,
        kamsoft_service=kamsoft_service,
    )


def test_build_report_contains_all_sections():
    service = create_service(
        system_info=SimpleNamespace(
            computer_name="TEST-PC",
            user="marek",
        ),
        network_info=SimpleNamespace(
            local_ip="192.168.1.10",
            gateway="192.168.1.1",
            internet=True,
        ),
        printers=[
            SimpleNamespace(
                name="Drukarka",
                status="Gotowa",
            ),
        ],
        default_printer="Drukarka",
    )

    report = service.build_report()

    assert len(report.items) == 4
    assert [item.name for item in report.items] == [
        "Windows",
        "Sieć",
        "Drukarki",
        "Kamsoft",
    ]


def test_build_report_is_ok_when_everything_is_ok():
    service = create_service(
        system_info=SimpleNamespace(
            computer_name="TEST-PC",
            user="marek",
        ),
        network_info=SimpleNamespace(
            local_ip="192.168.1.10",
            gateway="192.168.1.1",
            internet=True,
        ),
        printers=[
            SimpleNamespace(
                name="Drukarka",
                status="Gotowa",
            ),
        ],
        default_printer="Drukarka",
    )

    report = service.build_report()

    assert report.status == STATUS_OK
    assert report.has_errors is False
    assert report.has_warnings is False


def test_network_without_internet_is_warning():
    service = create_service(
        system_info=SimpleNamespace(
            computer_name="TEST-PC",
            user="marek",
        ),
        network_info=SimpleNamespace(
            local_ip="192.168.1.10",
            gateway="192.168.1.1",
            internet=False,
        ),
        printers=[
            SimpleNamespace(
                name="Drukarka",
                status="Gotowa",
            ),
        ],
        default_printer="Drukarka",
    )

    report = service.build_report()

    network_item = next(
        item
        for item in report.items
        if item.name == "Sieć"
    )

    assert network_item.status == STATUS_WARNING
    assert "brak dostępu do Internetu" in network_item.message
    assert report.status == STATUS_WARNING


def test_printer_problem_is_warning():
    service = create_service(
        system_info=SimpleNamespace(
            computer_name="TEST-PC",
            user="marek",
        ),
        network_info=SimpleNamespace(
            local_ip="192.168.1.10",
            gateway="192.168.1.1",
            internet=True,
        ),
        printers=[
            SimpleNamespace(
                name="HP",
                status="Offline",
            ),
        ],
        default_printer="HP",
    )

    report = service.build_report()

    printer_item = next(
        item
        for item in report.items
        if item.name == "Drukarki"
    )

    assert printer_item.status == STATUS_WARNING
    assert "HP" in printer_item.message
    assert report.status == STATUS_WARNING


def test_kamsoft_error_makes_report_error():
    service = create_service(
        system_info=SimpleNamespace(
            computer_name="TEST-PC",
            user="marek",
        ),
        network_info=SimpleNamespace(
            local_ip="192.168.1.10",
            gateway="192.168.1.1",
            internet=True,
        ),
        printers=[
            SimpleNamespace(
                name="Drukarka",
                status="Gotowa",
            ),
        ],
        default_printer="Drukarka",
        kamsoft_result={
            "status": "ERROR",
            "errors": ["Brak APMAN.EXE"],
            "warnings": [],
        },
    )

    report = service.build_report()

    kamsoft_item = next(
        item
        for item in report.items
        if item.name == "Kamsoft"
    )

    assert kamsoft_item.status == STATUS_ERROR
    assert "Brak APMAN.EXE" in kamsoft_item.message
    assert report.status == STATUS_ERROR


def test_system_exception_becomes_error():
    system_service = MagicMock()
    system_service.get_info.side_effect = RuntimeError(
        "test error"
    )

    network_service = MagicMock()
    network_service.get_info.return_value = SimpleNamespace(
        local_ip="192.168.1.10",
        gateway="192.168.1.1",
        internet=True,
    )

    printer_service = MagicMock()
    printer_service.list_printers.return_value = [
        SimpleNamespace(
            name="Drukarka",
            status="Gotowa",
        )
    ]
    printer_service.get_default_printer.return_value = "Drukarka"

    kamsoft_service = MagicMock()
    kamsoft_service.diagnostic_result.return_value = {
        "status": "OK",
        "errors": [],
        "warnings": [],
    }

    service = SystemReportService(
        system_service=system_service,
        network_service=network_service,
        printer_service=printer_service,
        kamsoft_service=kamsoft_service,
    )

    report = service.build_report()

    windows_item = next(
        item
        for item in report.items
        if item.name == "Windows"
    )

    assert windows_item.status == STATUS_ERROR
    assert "test error" in windows_item.message
    assert report.status == STATUS_ERROR
