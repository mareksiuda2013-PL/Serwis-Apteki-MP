from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
)

from modules.firebird.controller import FirebirdController


class InformationTab(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = FirebirdController()

        layout = QVBoxLayout(self)

        self.form = QFormLayout()

        self.lbl_installed = QLabel("-")
        self.lbl_version = QLabel("-")
        self.lbl_service = QLabel("-")
        self.lbl_status = QLabel("-")
        self.lbl_install = QLabel("-")
        self.lbl_bin = QLabel("-")
        self.lbl_port = QLabel("-")

        self.form.addRow("Zainstalowany:", self.lbl_installed)
        self.form.addRow("Wersja:", self.lbl_version)
        self.form.addRow("Usługa:", self.lbl_service)
        self.form.addRow("Status:", self.lbl_status)
        self.form.addRow("Instalacja:", self.lbl_install)
        self.form.addRow("BIN:", self.lbl_bin)
        self.form.addRow("Port:", self.lbl_port)

        layout.addLayout(self.form)

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.clicked.connect(self.refresh)

        layout.addWidget(self.refresh_button)
        layout.addStretch()

        self.refresh()

    def refresh(self):

        info = self.controller.info()

        self.lbl_installed.setText("TAK" if info.installed else "NIE")
        self.lbl_version.setText(info.version or "-")
        self.lbl_service.setText(info.service_name or "-")
        self.lbl_status.setText(info.service_status or "-")
        self.lbl_install.setText(str(info.install_path) if info.install_path else "-")
        self.lbl_bin.setText(str(info.bin_path) if info.bin_path else "-")
        self.lbl_port.setText(str(info.port))