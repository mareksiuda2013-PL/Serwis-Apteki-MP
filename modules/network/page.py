from __future__ import annotations

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.network import NetworkService


class NetworkPage(QWidget):
    def __init__(self):
        super().__init__()

        self.service = NetworkService()

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Sieć")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")

        description = QLabel(
            "Informacje o lokalnym połączeniu sieciowym i dostępie do Internetu."
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        info_group = QGroupBox("Informacje o sieci")
        info_layout = QVBoxLayout(info_group)

        self.local_ip_label = QLabel("—")
        self.gateway_label = QLabel("—")
        self.internet_label = QLabel("—")

        self._add_row(info_layout, "Adres IP:", self.local_ip_label)
        self._add_row(info_layout, "Brama:", self.gateway_label)
        self._add_row(info_layout, "Internet:", self.internet_label)

        layout.addWidget(info_group)

        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Sprawdzanie...")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_group)

        button_layout = QHBoxLayout()

        refresh_button = QPushButton("Odśwież")
        refresh_button.clicked.connect(self._refresh)

        button_layout.addWidget(refresh_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

    @staticmethod
    def _add_row(layout, name: str, value_label: QLabel):
        row = QHBoxLayout()

        name_label = QLabel(name)
        name_label.setMinimumWidth(100)

        row.addWidget(name_label)
        row.addWidget(value_label)
        row.addStretch()

        layout.addLayout(row)

    def _refresh(self):
        try:
            info = self.service.get_info()

            self.local_ip_label.setText(info.local_ip or "Nie wykryto")
            self.gateway_label.setText(info.gateway or "Nie wykryto")

            if info.internet:
                self.internet_label.setText("Dostępny")
                self.status_label.setText("Połączenie z Internetem działa.")
            else:
                self.internet_label.setText("Brak")
                self.status_label.setText(
                    "Brak potwierdzonego dostępu do Internetu."
                )

        except Exception as exc:
            self.local_ip_label.setText("Błąd")
            self.gateway_label.setText("Błąd")
            self.internet_label.setText("Błąd")
            self.status_label.setText(f"Błąd: {exc}")
