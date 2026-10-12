from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.system.admin_service import AdminService
from services.system.system_service import SystemService


class WindowsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.service = SystemService()

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Windows")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        description = QLabel(
            "Informacje o systemie Windows, sprzęcie i środowisku pracy."
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        computer_group = QGroupBox("Komputer i system")
        computer_layout = QGridLayout(computer_group)

        self.computer_name_label = QLabel("—")
        self.user_label = QLabel("—")
        self.windows_label = QLabel("—")
        self.windows_version_label = QLabel("—")
        self.windows_architecture_label = QLabel("—")
        self.python_version_label = QLabel("—")
        self.admin_label = QLabel("—")

        self._add_row(
            computer_layout, 0, "Komputer:", self.computer_name_label
        )
        self._add_row(
            computer_layout, 1, "Użytkownik:", self.user_label
        )
        self._add_row(
            computer_layout, 2, "Windows:", self.windows_label
        )
        self._add_row(
            computer_layout, 3, "Wersja:", self.windows_version_label
        )
        self._add_row(
            computer_layout, 4, "Architektura:", self.windows_architecture_label
        )
        self._add_row(
            computer_layout, 5, "Python:", self.python_version_label
        )
        self._add_row(
            computer_layout, 6, "Uprawnienia:", self.admin_label
        )

        layout.addWidget(computer_group)

        cpu_group = QGroupBox("Procesor")
        cpu_layout = QGridLayout(cpu_group)

        self.cpu_name_label = QLabel("—")
        self.cpu_usage_label = QLabel("—")
        self.cpu_cores_label = QLabel("—")
        self.cpu_threads_label = QLabel("—")
        self.cpu_frequency_label = QLabel("—")

        self._add_row(
            cpu_layout, 0, "Procesor:", self.cpu_name_label
        )
        self._add_row(
            cpu_layout, 1, "Użycie CPU:", self.cpu_usage_label
        )
        self._add_row(
            cpu_layout, 2, "Rdzenie:", self.cpu_cores_label
        )
        self._add_row(
            cpu_layout, 3, "Wątki:", self.cpu_threads_label
        )
        self._add_row(
            cpu_layout, 4, "Częstotliwość:", self.cpu_frequency_label
        )

        layout.addWidget(cpu_group)

        ram_group = QGroupBox("Pamięć RAM")
        ram_layout = QGridLayout(ram_group)

        self.ram_total_label = QLabel("—")
        self.ram_used_label = QLabel("—")
        self.ram_percent_label = QLabel("—")

        self._add_row(
            ram_layout, 0, "Pamięć całkowita:", self.ram_total_label
        )
        self._add_row(
            ram_layout, 1, "Pamięć użyta:", self.ram_used_label
        )
        self._add_row(
            ram_layout, 2, "Wykorzystanie:", self.ram_percent_label
        )

        layout.addWidget(ram_group)

        status_group = QGroupBox("Stan systemu")
        status_layout = QGridLayout(status_group)

        self.uptime_label = QLabel("—")
        self.boot_time_label = QLabel("—")

        self._add_row(
            status_layout, 0, "Czas pracy:", self.uptime_label
        )
        self._add_row(
            status_layout, 1, "Uruchomienie:", self.boot_time_label
        )

        layout.addWidget(status_group)

        refresh_button = QPushButton("Odśwież")
        refresh_button.clicked.connect(self._refresh)

        layout.addWidget(refresh_button)
        layout.addStretch()

    @staticmethod
    def _add_row(
        layout: QGridLayout,
        row: int,
        name: str,
        value_label: QLabel,
    ):
        name_label = QLabel(name)
        name_label.setMinimumWidth(150)

        layout.addWidget(name_label, row, 0)
        layout.addWidget(value_label, row, 1)

    def _refresh(self):
        try:
            info = self.service.get_info()

            self.computer_name_label.setText(
                info.computer_name or "Nie wykryto"
            )
            self.user_label.setText(
                info.user or "Nie wykryto"
            )
            self.windows_label.setText(
                info.windows or "Nie wykryto"
            )
            self.windows_version_label.setText(
                info.windows_version or "Nie wykryto"
            )
            self.windows_architecture_label.setText(
                info.windows_architecture or "Nie wykryto"
            )
            self.python_version_label.setText(
                info.python_version or "Nie wykryto"
            )
            self.admin_label.setText(
                AdminService.status()
            )

            self.cpu_name_label.setText(
                info.cpu_name or "Nie wykryto"
            )
            self.cpu_usage_label.setText(
                f"{info.cpu_usage:.1f}%"
            )
            self.cpu_cores_label.setText(
                str(info.cpu_cores)
            )
            self.cpu_threads_label.setText(
                str(info.cpu_threads)
            )
            self.cpu_frequency_label.setText(
                f"{info.cpu_frequency_mhz:.0f} MHz"
            )

            self.ram_total_label.setText(
                f"{info.ram_total_gb:.2f} GB"
            )
            self.ram_used_label.setText(
                f"{info.ram_used_gb:.2f} GB"
            )
            self.ram_percent_label.setText(
                f"{info.ram_percent}%"
            )

            self.uptime_label.setText(
                info.uptime or "Nie wykryto"
            )
            self.boot_time_label.setText(
                info.boot_time or "Nie wykryto"
            )

        except Exception as exc:
            self._show_error(str(exc))

    def _show_error(self, message: str):
        error_text = f"Błąd: {message}"

        self.computer_name_label.setText(error_text)
        self.user_label.setText(error_text)
        self.windows_label.setText(error_text)
        self.windows_version_label.setText(error_text)
        self.windows_architecture_label.setText(error_text)
        self.python_version_label.setText(error_text)
        self.admin_label.setText(error_text)

        self.cpu_name_label.setText(error_text)
        self.cpu_usage_label.setText(error_text)
        self.cpu_cores_label.setText(error_text)
        self.cpu_threads_label.setText(error_text)
        self.cpu_frequency_label.setText(error_text)

        self.ram_total_label.setText(error_text)
        self.ram_used_label.setText(error_text)
        self.ram_percent_label.setText(error_text)

        self.uptime_label.setText(error_text)
        self.boot_time_label.setText(error_text)