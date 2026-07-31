from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)


class DashboardCard(QFrame):
    """
    Uniwersalna karta Dashboardu.
    """

    STATUS_COLORS = {
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#0d6efd",
        "gray": "#6c757d",
    }

    def __init__(self, title: str, icon: str = "") -> None:
        super().__init__()

        self._rows: dict[str, QLabel] = {}

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("DashboardCard")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.setStyleSheet("""
        QFrame#DashboardCard {
            border: 1px solid #D8D8D8;
            border-radius: 8px;
            background: white;
        }

        QLabel {
            font-size: 10pt;
        }
        """)

        layout = QVBoxLayout(self)

        self.title_label = QLabel(f"{icon}  {title}")
        self.title_label.setStyleSheet("""
            font-size:15px;
            font-weight:bold;
        """)

        layout.addWidget(self.title_label)

        self.status_label = QLabel("Brak danych")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(28)
        self.status_label.setStyleSheet("""
            border-radius:4px;
            color:white;
            background:#6c757d;
            font-weight:bold;
        """)

        layout.addWidget(self.status_label)

        self.grid = QGridLayout()
        layout.addLayout(self.grid)

        layout.addStretch()

    # ---------------------------------------------------------

    def set_status(self, text: str, color: str = "gray") -> None:

        background = self.STATUS_COLORS.get(color, "#6c757d")

        self.status_label.setText(text)

        self.status_label.setStyleSheet(f"""
            border-radius:4px;
            padding:4px;
            color:white;
            background:{background};
            font-weight:bold;
        """)

    # ---------------------------------------------------------

    def set_line(self, name: str, value: str) -> None:

        if name in self._rows:

            self._rows[name].setText(value)
            return

        row = len(self._rows)

        key = QLabel(name + ":")

        key.setStyleSheet("""
            font-weight:bold;
        """)

        val = QLabel(value)

        self.grid.addWidget(key, row, 0)
        self.grid.addWidget(val, row, 1)

        self._rows[name] = val

    # ---------------------------------------------------------

    def clear(self) -> None:

        for value in self._rows.values():
            value.setText("-")