from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from gui.cards import DashboardCard

from .controller import DashboardController


class DashboardPage(QWidget):
    """
    Główny Dashboard aplikacji.
    """

    def __init__(self) -> None:

        super().__init__()

        self.controller = DashboardController()

        # ==================================================
        # TŁO
        # ==================================================

        self.setObjectName(
            "DashboardPage"
        )

        self.setStyleSheet(
            """
            QWidget#DashboardPage {
                background-color: #eeeeee;
            }

            QLabel#UptimeTitle {
                color: #202020;
                font-weight: bold;
            }

            QLabel#UptimeValue {
                color: #202020;
                font-weight: normal;
            }
            """
        )

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QGridLayout(
            self
        )

        layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        layout.setHorizontalSpacing(
            16
        )

        layout.setVerticalSpacing(
            16
        )

        # ==================================================
        # SYSTEM
        # ==================================================

        self.system_card = DashboardCard(
            title="System",
            icon="💻",
        )

        layout.addWidget(
            self.system_card,
            0,
            0,
        )

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.firebird_card = DashboardCard(
            title="Firebird",
            icon="🔥",
        )

        layout.addWidget(
            self.firebird_card,
            0,
            1,
        )

        # ==================================================
        # SIEĆ
        # ==================================================

        self.network_card = DashboardCard(
            title="Sieć",
            icon="🌐",
        )

        layout.addWidget(
            self.network_card,
            1,
            0,
        )

        # ==================================================
        # DYSKI
        # ==================================================

        self.disk_card = DashboardCard(
            title="Dyski",
            icon="💾",
        )

        layout.addWidget(
            self.disk_card,
            1,
            1,
        )

        # ==================================================
        # ROZMIARY
        # ==================================================

        layout.setRowStretch(
            0,
            1,
        )

        layout.setRowStretch(
            1,
            1,
        )

        layout.setColumnStretch(
            0,
            1,
        )

        layout.setColumnStretch(
            1,
            1,
        )

        # ==================================================
        # TIMER
        # ==================================================

        self.timer = QTimer(
            self
        )

        self.timer.timeout.connect(
            self.refresh
        )

        self.timer.start(
            10000
        )

        # ==================================================
        # PIERWSZE ŁADOWANIE
        # ==================================================

        self.refresh()

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        self.refresh_system()
        self.refresh_firebird()
        self.refresh_disks()
        self.refresh_network()

    # ======================================================
    # SYSTEM
    # ======================================================

    def refresh_system(self) -> None:

        try:

            info = self.controller.system_info()

            self.system_card.clear()

            self.system_card.set_status(
                "Online",
                "success",
            )

            # --------------------------------------------------
            # KOMPUTER
            # --------------------------------------------------

            self.system_card.set_line(
                "Komputer",
                info.computer_name or "-",
            )

            # --------------------------------------------------
            # UŻYTKOWNIK
            # --------------------------------------------------

            self.system_card.set_line(
                "Użytkownik",
                info.user or "-",
            )

            # --------------------------------------------------
            # WINDOWS
            # --------------------------------------------------

            self.system_card.set_line(
                "Windows",
                f"{info.windows} {info.windows_version}",
            )

            # --------------------------------------------------
            # PROCESOR
            # --------------------------------------------------

            self.system_card.set_line(
                "Procesor",
                info.cpu_name or "-",
            )

            # --------------------------------------------------
            # PAMIĘĆ
            # --------------------------------------------------

            self.system_card.set_line(
                "Pamięć",
                (
                    f"{info.ram_used_gb:.1f} / "
                    f"{info.ram_total_gb:.1f} GB"
                ),
            )

            # --------------------------------------------------
            # CPU
            # --------------------------------------------------

            self.system_card.set_progress(
                "CPU",
                int(info.cpu_usage),
            )

            # --------------------------------------------------
            # RAM
            # --------------------------------------------------

            self.system_card.set_progress(
                "RAM",
                int(info.ram_percent),
            )

            # --------------------------------------------------
            # UPTIME
            # --------------------------------------------------
            #
            # Uptime jest dodawany jako zwykła informacja,
            # ale z bezpiecznym, jednoznacznym tekstem.
            #

            uptime_text = str(
                info.uptime or "-"
            ).strip()

            self.system_card.set_line(
                "Uptime",
                uptime_text,
            )

        except Exception as exc:

            self.system_card.clear()

            self.system_card.set_status(
                "Błąd",
                "error",
            )

            self.system_card.set_line(
                "Informacja",
                str(exc),
            )

    # ======================================================
    # FIREBIRD
    # ======================================================

    def refresh_firebird(self) -> None:

        try:

            info = self.controller.firebird_info()

            self.firebird_card.clear()

            # --------------------------------------------------
            # BRAK FIREBIRD
            # --------------------------------------------------

            if not info.installed:

                self.firebird_card.set_status(
                    "Nie znaleziono",
                    "error",
                )

                return

            # --------------------------------------------------
            # STATUS USŁUGI
            # --------------------------------------------------

            if info.service_status == "Running":

                self.firebird_card.set_status(
                    "Online",
                    "success",
                )

            elif info.service_status == "Stopped":

                self.firebird_card.set_status(
                    "Zatrzymany",
                    "warning",
                )

            else:

                self.firebird_card.set_status(
                    info.service_status or "Nieznany",
                    "warning",
                )

            # --------------------------------------------------
            # WERSJA
            # --------------------------------------------------

            self.firebird_card.set_line(
                "Wersja",
                info.version or "-",
            )

            # --------------------------------------------------
            # ODS
            # --------------------------------------------------

            self.firebird_card.set_line(
                "ODS",
                info.ods or "-",
            )

            # --------------------------------------------------
            # USŁUGA
            # --------------------------------------------------

            self.firebird_card.set_line(
                "Usługa",
                info.service_name or "-",
            )

            # --------------------------------------------------
            # BAZA
            # --------------------------------------------------

            database_name = "-"

            if info.database_path:

                database_name = (
                    info.database_path
                    .replace("/", "\\")
                    .split("\\")[-1]
                )

            self.firebird_card.set_line(
                "Baza",
                database_name,
            )

            # --------------------------------------------------
            # PLIK
            # --------------------------------------------------

            if info.database_exists:

                self.firebird_card.set_line(
                    "Plik",
                    "OK",
                )

                self.firebird_card.set_line(
                    "Rozmiar",
                    f"{info.database_size_gb:.2f} GB",
                )

            else:

                self.firebird_card.set_line(
                    "Plik",
                    "BRAK",
                )

                self.firebird_card.set_line(
                    "Rozmiar",
                    "-",
                )

            # --------------------------------------------------
            # TABELE
            # --------------------------------------------------

            self.firebird_card.set_line(
                "Tabele",
                str(info.tables),
            )

            # --------------------------------------------------
            # PAGE SIZE
            # --------------------------------------------------

            self.firebird_card.set_line(
                "Page size",
                str(info.page_size),
            )

            # --------------------------------------------------
            # DIALECT
            # --------------------------------------------------

            self.firebird_card.set_line(
                "Dialect",
                str(info.sql_dialect),
            )

        except Exception as exc:

            self.firebird_card.clear()

            self.firebird_card.set_status(
                "Błąd",
                "error",
            )

            self.firebird_card.set_line(
                "Informacja",
                str(exc),
            )

    # ======================================================
    # DYSKI
    # ======================================================

    def refresh_disks(self) -> None:

        try:

            disks = self.controller.disk_info()

            self.disk_card.clear()

            if not disks:

                self.disk_card.set_status(
                    "Brak danych",
                    "warning",
                )

                return

            critical = False
            warning = False

            # --------------------------------------------------
            # OCENA STANU
            # --------------------------------------------------

            for disk in disks:

                if disk.percent >= 90:

                    critical = True

                elif disk.percent >= 80:

                    warning = True

            # --------------------------------------------------
            # STATUS
            # --------------------------------------------------

            if critical:

                self.disk_card.set_status(
                    "Mało miejsca",
                    "error",
                )

            elif warning:

                self.disk_card.set_status(
                    "Uwaga",
                    "warning",
                )

            else:

                self.disk_card.set_status(
                    "OK",
                    "success",
                )

            # --------------------------------------------------
            # DYSKI
            # --------------------------------------------------

            for disk in disks:

                self.disk_card.set_line(
                    disk.drive,
                    (
                        f"{disk.used_gb:.1f} / "
                        f"{disk.total_gb:.1f} GB "
                        f"({disk.percent}%)"
                    ),
                )

                self.disk_card.set_progress(
                    disk.drive,
                    disk.percent,
                )

        except Exception as exc:

            self.disk_card.clear()

            self.disk_card.set_status(
                "Błąd",
                "error",
            )

            self.disk_card.set_line(
                "Informacja",
                str(exc),
            )

    # ======================================================
    # SIEĆ
    # ======================================================

    def refresh_network(self) -> None:

        try:

            info = self.controller.network_info()

            self.network_card.clear()

            # --------------------------------------------------
            # INTERNET
            # --------------------------------------------------

            if info.internet:

                self.network_card.set_status(
                    "Internet OK",
                    "success",
                )

            else:

                self.network_card.set_status(
                    "Brak Internetu",
                    "error",
                )

            # --------------------------------------------------
            # ADRES IP
            # --------------------------------------------------

            self.network_card.set_line(
                "Adres IP",
                info.local_ip or "-",
            )

            # --------------------------------------------------
            # BRAMA
            # --------------------------------------------------

            self.network_card.set_line(
                "Brama",
                info.gateway or "-",
            )

            # --------------------------------------------------
            # INTERNET
            # --------------------------------------------------

            self.network_card.set_line(
                "Internet",
                (
                    "Dostępny"
                    if info.internet
                    else "Brak dostępu"
                ),
            )

        except Exception as exc:

            self.network_card.clear()

            self.network_card.set_status(
                "Błąd",
                "error",
            )

            self.network_card.set_line(
                "Informacja",
                str(exc),
            )