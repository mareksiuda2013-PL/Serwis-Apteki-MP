from __future__ import annotations

from dataclasses import dataclass

import win32print


@dataclass(slots=True)
class PrinterInfo:
    name: str
    status: str
    is_default: bool
    port: str
    driver: str


class PrinterService:
    """Usługa diagnostyki drukarek systemu Windows."""

    def list_printers(self) -> list[PrinterInfo]:
        """Zwraca listę drukarek zainstalowanych w systemie."""

        printers: list[PrinterInfo] = []

        default_printer = self.get_default_printer()

        flags = (
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )

        printer_list = win32print.EnumPrinters(
            flags,
            None,
            2,
        )

        for printer in printer_list:
            printer_name = printer.get("pPrinterName", "")
            status = self._get_status(printer.get("Status", 0))
            port = printer.get("pPortName", "") or ""
            driver = printer.get("pDriverName", "") or ""

            printers.append(
                PrinterInfo(
                    name=printer_name,
                    status=status,
                    is_default=printer_name == default_printer,
                    port=port,
                    driver=driver,
                )
            )

        return printers

    @staticmethod
    def get_default_printer() -> str:
        """Zwraca nazwę domyślnej drukarki."""

        try:
            return win32print.GetDefaultPrinter()
        except Exception:
            return ""

    @staticmethod
    def printer_exists(name: str) -> bool:
        """Sprawdza, czy drukarka istnieje w systemie."""

        if not name:
            return False

        try:
            handle = win32print.OpenPrinter(name)
            win32print.ClosePrinter(handle)
            return True
        except Exception:
            return False

    @staticmethod
    def _get_status(status: int) -> str:
        """Tłumaczy status drukarki na czytelny opis."""

        if status == 0:
            return "Gotowa"

        status_map = {
            0x00000001: "Inicjalizacja",
            0x00000002: "Błąd",
            0x00000004: "Usuwanie",
            0x00000008: "Offline",
            0x00000010: "Papier zacięty",
            0x00000020: "Brak papieru",
            0x00000040: "Ręczne podawanie",
            0x00000080: "Papier zablokowany",
            0x00000100: "Drukowanie",
            0x00000200: "Sprawdzanie",
            0x00000400: "Oczekiwanie",
            0x00000800: "Przetwarzanie",
            0x00001000: "Brak tonera",
            0x00002000: "Brak miejsca",
            0x00004000: "Brak pamięci",
            0x00008000: "Pokrywa otwarta",
            0x00010000: "Serwer offline",
            0x00020000: "Nieprawidłowy toner",
        }

        messages = [
            message
            for flag, message in status_map.items()
            if status & flag
        ]

        if messages:
            return ", ".join(messages)

        return f"Nieznany status ({status})"