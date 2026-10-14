from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from models.system_report import (
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
    SystemReport,
)
from services.system_report_service import SystemReportService


class ReportsPage(QWidget):
    """Moduł zbiorczej diagnostyki stanowiska."""

    def __init__(
        self,
        service: SystemReportService | None = None,
    ) -> None:
        super().__init__()

        self.service = (
            service
            if service is not None
            else SystemReportService()
        )

        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("ReportsPage")

        self.setStyleSheet(
            """
            QWidget#ReportsPage {
                background-color: #f2f2f2;
                color: #202020;
            }

            QLabel {
                color: #202020;
            }

            QFrame {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }

            QPushButton {
                background-color: #ffffff;
                color: #202020;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 7px 14px;
            }

            QPushButton:hover {
                background-color: #e9e9e9;
            }

            QPushButton:pressed {
                background-color: #dddddd;
            }

            QPushButton:disabled {
                color: #888888;
                background-color: #eeeeee;
            }

            QScrollArea {
                background-color: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Raporty")
        title.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            color: #202020;
            """
        )
        layout.addWidget(title)

        description = QLabel(
            "Zbiorcza diagnostyka stanowiska."
        )
        description.setStyleSheet(
            """
            font-size: 14px;
            color: #555555;
            """
        )
        layout.addWidget(description)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.run_button = QPushButton("Wykonaj raport")
        self.run_button.clicked.connect(self._run_report)

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.clicked.connect(self._run_report)

        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.refresh_button)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        self.status_frame = QFrame()
        self.status_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        status_layout = QVBoxLayout(self.status_frame)
        status_layout.setContentsMargins(12, 10, 12, 10)
        status_layout.setSpacing(4)

        self.status_title = QLabel("Status stanowiska")
        self.status_title.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #202020;
            """
        )

        self.status_value = QLabel("Nie wykonano raportu")
        self.status_value.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.status_value.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            color: #555555;
            """
        )

        status_layout.addWidget(self.status_title)
        status_layout.addWidget(self.status_value)

        layout.addWidget(self.status_frame)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.results_widget = QWidget()
        self.results_widget.setObjectName(
            "ReportsResultsWidget"
        )
        self.results_widget.setStyleSheet(
            """
            QWidget#ReportsResultsWidget {
                background-color: transparent;
            }
            """
        )

        self.results_layout = QVBoxLayout(
            self.results_widget
        )
        self.results_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.results_layout.setSpacing(8)

        scroll.setWidget(self.results_widget)

        layout.addWidget(scroll)

    def _run_report(self) -> None:
        self.run_button.setEnabled(False)
        self.refresh_button.setEnabled(False)

        try:
            report = self.service.build_report()
            self._display_report(report)

        finally:
            self.run_button.setEnabled(True)
            self.refresh_button.setEnabled(True)

    def _display_report(
        self,
        report: SystemReport,
    ) -> None:
        self.status_value.setText(
            self._status_text(report.status)
        )

        self.status_value.setStyleSheet(
            self._status_style(report.status)
        )

        self._clear_results()

        for item in report.items:
            self._add_result_item(
                item.name,
                item.status,
                item.message,
            )

        self.results_layout.addStretch()

    def _clear_results(self) -> None:
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def _add_result_item(
        self,
        name: str,
        status: str,
        message: str,
    ) -> None:
        frame = QFrame()
        frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        header = QHBoxLayout()

        name_label = QLabel(name)
        name_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            color: #202020;
            """
        )

        status_label = QLabel(
            self._status_text(status)
        )
        status_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )
        status_label.setStyleSheet(
            self._status_style(status)
        )

        header.addWidget(name_label)
        header.addStretch()
        header.addWidget(status_label)

        message_label = QLabel(message or "-")
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            """
            font-size: 14px;
            color: #404040;
            """
        )

        layout.addLayout(header)
        layout.addWidget(message_label)

        self.results_layout.addWidget(frame)

    @staticmethod
    def _status_text(status: str) -> str:
        if status == STATUS_OK:
            return "OK"

        if status == STATUS_WARNING:
            return "OSTRZEŻENIE"

        if status == STATUS_ERROR:
            return "BŁĄD"

        return status

    @staticmethod
    def _status_style(status: str) -> str:
        if status == STATUS_OK:
            return (
                "font-size: 18px;"
                "font-weight: bold;"
                "color: #198754;"
            )

        if status == STATUS_WARNING:
            return (
                "font-size: 18px;"
                "font-weight: bold;"
                "color: #b8860b;"
            )

        if status == STATUS_ERROR:
            return (
                "font-size: 18px;"
                "font-weight: bold;"
                "color: #dc3545;"
            )

        return (
            "font-size: 18px;"
            "font-weight: bold;"
            "color: #202020;"
        )