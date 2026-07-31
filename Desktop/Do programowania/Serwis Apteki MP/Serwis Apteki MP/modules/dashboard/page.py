from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
)

from gui.cards import DashboardCard

from .controller import DashboardController


class DashboardPage(QWidget):

    def __init__(self) -> None:

        super().__init__()

        self.controller = DashboardController()

        layout = QGridLayout(self)

        self.system_card = DashboardCard(
            title="System",
            icon="💻",
        )

        layout.addWidget(
            self.system_card,
            0,
            0,
        )

        self.firebird_card = DashboardCard(
            title="Firebird",
            icon="🔥",
        )

        layout.addWidget(
            self.firebird_card,
            0,
            1,
        )

        self.network_card = DashboardCard(
            title="Sieć",
            icon="🌐",
        )

        layout.addWidget(
            self.network_card,
            1,
            0,
        )

        self.disk_card = DashboardCard(
            title="Dyski",
            icon="💾",
        )

        layout.addWidget(
            self.disk_card,
            1,
            1,
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

        self.refresh()

    # ----------------------------------------------------------

    def refresh(self):

        info = self.controller.system_info()

        self.system_card.clear()

        self.system_card.set_status(
            "Online",
            "success",
        )

        self.system_card.set_line(
            "Komputer",
            info.computer_name,
        )

        self.system_card.set_line(
            "Użytkownik",
            info.user,
        )

        self.system_card.set_line(
            "Windows",
            f"{info.windows} {info.windows_version}",
        )

        self.system_card.set_line(
            "CPU",
            f"{info.cpu_usage:.1f} %",
        )

        self.system_card.set_line(
            "RAM",
            f"{info.ram_used_gb:.1f} / {info.ram_total_gb:.1f} GB",
        )

        self.system_card.set_line(
            "Uptime",
            info.uptime,
        )

        #
        # Placeholdery - uzupełnimy w kolejnych sprintach
        #

        self.firebird_card.set_status(
            "Brak danych",
            "warning",
        )

        self.network_card.set_status(
            "Brak danych",
            "warning",
        )

        self.disk_card.set_status(
            "Brak danych",
            "warning",
        )