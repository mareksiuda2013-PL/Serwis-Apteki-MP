from __future__ import annotations

from unittest.mock import patch

from services.printers import PrinterService


def test_get_default_printer_returns_name():
    with patch(
        "services.printers.printer_service.win32print.GetDefaultPrinter",
        return_value="Test Printer",
    ):
        result = PrinterService.get_default_printer()

    assert result == "Test Printer"


def test_get_default_printer_returns_empty_when_error():
    with patch(
        "services.printers.printer_service.win32print.GetDefaultPrinter",
        side_effect=Exception("Printer error"),
    ):
        result = PrinterService.get_default_printer()

    assert result == ""


def test_printer_exists_returns_true():
    fake_handle = object()

    with patch(
        "services.printers.printer_service.win32print.OpenPrinter",
        return_value=fake_handle,
    ) as open_printer, patch(
        "services.printers.printer_service.win32print.ClosePrinter",
    ) as close_printer:
        result = PrinterService.printer_exists("Test Printer")

    assert result is True
    open_printer.assert_called_once_with("Test Printer")
    close_printer.assert_called_once_with(fake_handle)


def test_printer_exists_returns_false_for_empty_name():
    result = PrinterService.printer_exists("")

    assert result is False


def test_printer_exists_returns_false_when_error():
    with patch(
        "services.printers.printer_service.win32print.OpenPrinter",
        side_effect=Exception("Printer error"),
    ):
        result = PrinterService.printer_exists("Test Printer")

    assert result is False


def test_get_status_returns_ready_for_zero():
    result = PrinterService._get_status(0)

    assert result == "Gotowa"


def test_get_status_returns_known_status():
    result = PrinterService._get_status(0x00000008)

    assert result == "Offline"


def test_get_status_returns_multiple_statuses():
    result = PrinterService._get_status(
        0x00000008 | 0x00000020
    )

    assert result == "Offline, Brak papieru"


def test_get_status_returns_unknown_status():
    result = PrinterService._get_status(0x80000000)

    assert result == "Nieznany status (2147483648)"


def test_list_printers_returns_printer_info():
    printers = [
        {
            "pPrinterName": "Printer A",
            "Status": 0,
            "pPortName": "USB001",
            "pDriverName": "Driver A",
        },
        {
            "pPrinterName": "Printer B",
            "Status": 0x00000008,
            "pPortName": "IP_192.168.1.10",
            "pDriverName": "Driver B",
        },
    ]

    with patch(
        "services.printers.printer_service.win32print.GetDefaultPrinter",
        return_value="Printer A",
    ), patch(
        "services.printers.printer_service.win32print.EnumPrinters",
        return_value=printers,
    ):
        result = PrinterService().list_printers()

    assert len(result) == 2

    assert result[0].name == "Printer A"
    assert result[0].status == "Gotowa"
    assert result[0].is_default is True
    assert result[0].port == "USB001"
    assert result[0].driver == "Driver A"

    assert result[1].name == "Printer B"
    assert result[1].status == "Offline"
    assert result[1].is_default is False
    assert result[1].port == "IP_192.168.1.10"
    assert result[1].driver == "Driver B"