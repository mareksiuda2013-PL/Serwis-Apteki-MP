from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from services.printers import PrinterService


class PrintersPage(QWidget):
    def __init__(self):
        super().__init__()

        self.service = PrinterService()

        self._build_ui()
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Drukarki")
        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        description = QLabel(
            "Lista drukarek zainstalowanych w systemie Windows "
            "oraz ich podstawowe informacje."
        )
        description.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(description)

        printers_group = QGroupBox("Drukarki systemowe")
        printers_layout = QVBoxLayout(printers_group)

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "Drukarka",
                "Status",
                "Domyślna",
                "Port",
                "Sterownik",
            ]
        )

        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)

        self.table.setStyleSheet(
            """
            QTableWidget {
                border: 1px solid #d6d9de;
                border-radius: 6px;
                background: white;
                alternate-background-color: #f5f7fa;
                gridline-color: transparent;
                selection-background-color: #dbeafe;
                selection-color: #1f2937;
            }

            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #edf0f2;
            }

            QHeaderView::section {
                background: #eef1f5;
                color: #374151;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #d6d9de;
            }
            """
        )

        header = self.table.horizontalHeader()

        for column in range(5):
            header.setSectionResizeMode(
                column,
                header.ResizeMode.Stretch,
            )

        printers_layout.addWidget(self.table)
        layout.addWidget(printers_group)

        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout(status_group)

        self.status_label = QLabel("Sprawdzanie...")
        self.status_label.setStyleSheet(
            """
            font-weight: bold;
            padding: 4px;
            """
        )

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addWidget(status_group)

        button_layout = QHBoxLayout()

        refresh_button = QPushButton("Odśwież")
        refresh_button.setMinimumWidth(100)
        refresh_button.clicked.connect(self._refresh)

        button_layout.addWidget(refresh_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addStretch()

    def _refresh(self):
        try:
            printers = self.service.list_printers()

            self.table.setRowCount(0)

            for row, printer in enumerate(printers):
                self.table.insertRow(row)

                self._set_item(
                    row,
                    0,
                    printer.name,
                )

                self._set_item(
                    row,
                    1,
                    printer.status,
                )

                self._set_item(
                    row,
                    2,
                    "Tak" if printer.is_default else "Nie",
                )

                self._set_item(
                    row,
                    3,
                    printer.port or "—",
                )

                self._set_item(
                    row,
                    4,
                    printer.driver or "—",
                )

            if printers:
                self.status_label.setText(
                    f"Wykryto drukarek: {len(printers)}"
                )
            else:
                self.status_label.setText(
                    "Nie wykryto żadnych drukarek."
                )

        except Exception as exc:
            self.table.setRowCount(0)
            self.status_label.setText(
                f"Błąd: {exc}"
            )

    def _set_item(
        self,
        row: int,
        column: int,
        text: str,
    ):
        item = QTableWidgetItem(text)

        item.setFlags(
            item.flags()
            & ~Qt.ItemFlag.ItemIsEditable
        )

        item.setToolTip(text)

        if column == 0:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter
                | Qt.AlignmentFlag.AlignLeft
            )
        else:
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

        self.table.setItem(
            row,
            column,
            item,
        )