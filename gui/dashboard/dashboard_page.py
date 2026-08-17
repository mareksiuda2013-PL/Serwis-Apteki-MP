from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QPushButton,
)

from controllers.dashboard_controller import DashboardController


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = DashboardController()

        layout = QVBoxLayout(self)

        self.form = QFormLayout()

        self.lbl_computer = QLabel("-")
        self.lbl_system = QLabel("-")
        self.lbl_architecture = QLabel("-")
        self.lbl_python = QLabel("-")
        self.lbl_admin = QLabel("-")

        self.form.addRow(
            "Komputer:",
            self.lbl_computer,
        )

        self.form.addRow(
            "System:",
            self.lbl_system,
        )

        self.form.addRow(
            "Architektura:",
            self.lbl_architecture,
        )

        self.form.addRow(
            "Python:",
            self.lbl_python,
        )

        self.form.addRow(
            "Uprawnienia:",
            self.lbl_admin,
        )

        layout.addLayout(self.form)

        self.refresh_button = QPushButton(
            "Odśwież"
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        layout.addWidget(
            self.refresh_button
        )

        layout.addStretch()

        self.refresh()

    def refresh(self):

        info = self.controller.system_info()

        self.lbl_computer.setText(
            info["computer"]
        )

        self.lbl_system.setText(
            f'{info["system"]} {info["release"]}'
        )

        self.lbl_architecture.setText(
            info["architecture"]
        )

        self.lbl_python.setText(
            info["python"]
        )

        if info["admin"]:

            self.lbl_admin.setText(
                "ADMINISTRATOR ✓"
            )

        else:

            self.lbl_admin.setText(
                "BRAK UPRAWNIEŃ ADMINISTRATORA ⚠"
            )