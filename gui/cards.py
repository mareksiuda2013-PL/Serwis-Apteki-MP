from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
)


class DashboardCard(QFrame):
    """
    Karta Dashboardu.

    Każda linia danych oraz każdy pasek
    posiada własny poziomy layout.
    Dzięki temu elementy nie nakładają się
    na siebie.
    """

    STATUS_COLORS = {
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#0d6efd",
        "gray": "#6c757d",
    }

    def __init__(
        self,
        title: str,
        icon: str = "",
    ) -> None:

        super().__init__()

        # ==================================================
        # ELEMENTY
        # ==================================================

        self._elements: dict[str, dict] = {}

        # ==================================================
        # KARTA
        # ==================================================

        self.setObjectName(
            "DashboardCard"
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.setMinimumSize(
            0,
            260,
        )

        self.setStyleSheet(
            """
            QFrame#DashboardCard {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 10px;
            }
            """
        )

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        self.layout_main = QVBoxLayout(
            self
        )

        self.layout_main.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        self.layout_main.setSpacing(
            8
        )

        # ==================================================
        # TYTUŁ
        # ==================================================

        self.title_label = QLabel(
            f"{icon}  {title}"
        )

        self.title_label.setMinimumHeight(
            28
        )

        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.title_label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
            """
        )

        self.layout_main.addWidget(
            self.title_label
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "Brak danych"
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setMinimumHeight(
            28
        )

        self.status_label.setMaximumHeight(
            32
        )

        self.status_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.layout_main.addWidget(
            self.status_label
        )

        self.set_status(
            "Brak danych",
            "gray",
        )

        # ==================================================
        # OBSZAR DANYCH
        # ==================================================

        self.data_layout = QVBoxLayout()

        self.data_layout.setContentsMargins(
            0,
            4,
            0,
            0,
        )

        self.data_layout.setSpacing(
            6
        )

        self.layout_main.addLayout(
            self.data_layout
        )

        # ==================================================
        # ROZPYCHACZ
        # ==================================================

        self.layout_main.addStretch(
            1
        )

    # ======================================================
    # STATUS
    # ======================================================

    def set_status(
        self,
        text: str,
        color: str = "gray",
    ) -> None:

        background = self.STATUS_COLORS.get(
            color,
            self.STATUS_COLORS["gray"],
        )

        self.status_label.setText(
            str(text)
        )

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {background};
                color: white;
                border-radius: 5px;
                padding: 4px;
                font-weight: bold;
            }}
            """
        )

    # ======================================================
    # ZWYKŁA LINIA
    # ======================================================

    def set_line(
        self,
        name: str,
        value: str,
    ) -> None:

        value = str(value)

        # --------------------------------------------------
        # ISTNIEJĄCY ELEMENT
        # --------------------------------------------------

        if name in self._elements:

            element = self._elements[name]

            if element["type"] == "line":

                element["key"].setText(
                    f"{name}:"
                )

                element["value"].setText(
                    value
                )

                return

            self._remove_element(
                name
            )

        # --------------------------------------------------
        # WIERSZ
        # --------------------------------------------------

        row_layout = QHBoxLayout()

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.setSpacing(
            10
        )

        row_layout.setSizeConstraint(
            QHBoxLayout.SizeConstraint.SetMinimumSize
        )

        # --------------------------------------------------
        # NAZWA
        # --------------------------------------------------

        key_label = QLabel(
            f"{name}:"
        )

        key_label.setMinimumWidth(
            85
        )

        key_label.setMinimumHeight(
            26
        )

        key_label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        key_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        key_label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                font-weight: bold;
                background: transparent;
            }
            """
        )

        # --------------------------------------------------
        # WARTOŚĆ
        # --------------------------------------------------

        value_label = QLabel(
            value
        )

        value_label.setMinimumHeight(
            26
        )

        value_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        value_label.setWordWrap(
            False
        )

        value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        value_label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                background: transparent;
            }
            """
        )

        # --------------------------------------------------
        # DODANIE
        # --------------------------------------------------

        row_layout.addWidget(
            key_label
        )

        row_layout.addWidget(
            value_label,
            1,
        )

        self.data_layout.addLayout(
            row_layout
        )

        self._elements[name] = {
            "type": "line",
            "layout": row_layout,
            "key": key_label,
            "value": value_label,
        }

    # ======================================================
    # PASEK POSTĘPU
    # ======================================================

    def set_progress(
        self,
        name: str,
        value: int,
    ) -> None:

        value = max(
            0,
            min(
                100,
                int(value),
            ),
        )

        # --------------------------------------------------
        # ISTNIEJĄCY ELEMENT
        # --------------------------------------------------

        if name in self._elements:

            element = self._elements[name]

            if element["type"] == "progress":

                progress = element["progress"]

                progress.setValue(
                    value
                )

                self._set_progress_color(
                    progress,
                    value,
                )

                return

            self._remove_element(
                name
            )

        # --------------------------------------------------
        # WIERSZ
        # --------------------------------------------------

        row_layout = QHBoxLayout()

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.setSpacing(
            10
        )

        # --------------------------------------------------
        # NAZWA
        # --------------------------------------------------

        label = QLabel(
            f"{name}:"
        )

        label.setMinimumWidth(
            85
        )

        label.setMinimumHeight(
            26
        )

        label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                font-weight: bold;
                background: transparent;
            }
            """
        )

        # --------------------------------------------------
        # PASEK
        # --------------------------------------------------

        progress = QProgressBar()

        progress.setRange(
            0,
            100,
        )

        progress.setValue(
            value
        )

        progress.setTextVisible(
            True
        )

        progress.setFormat(
            "%p%"
        )

        progress.setMinimumHeight(
            22
        )

        progress.setMaximumHeight(
            22
        )

        progress.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self._set_progress_color(
            progress,
            value,
        )

        # --------------------------------------------------
        # DODANIE
        # --------------------------------------------------

        row_layout.addWidget(
            label
        )

        row_layout.addWidget(
            progress,
            1,
        )

        self.data_layout.addLayout(
            row_layout
        )

        self._elements[name] = {
            "type": "progress",
            "layout": row_layout,
            "label": label,
            "progress": progress,
        }

    # ======================================================
    # KOLOR PASKA
    # ======================================================

    def _set_progress_color(
        self,
        progress: QProgressBar,
        value: int,
    ) -> None:

        if value >= 90:

            color = "#dc3545"

        elif value >= 70:

            color = "#ffc107"

        else:

            color = "#28a745"

        progress.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #c8c8c8;
                border-radius: 5px;
                background-color: #eeeeee;
                color: #202020;
                text-align: center;
                height: 22px;
            }}

            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
            """
        )

    # ======================================================
    # USUWANIE ELEMENTU
    # ======================================================

    def _remove_element(
        self,
        name: str,
    ) -> None:

        element = self._elements.get(
            name
        )

        if element is None:
            return

        row_layout = element["layout"]

        # --------------------------------------------------
        # USUNIĘCIE WIDGETÓW
        # --------------------------------------------------

        while row_layout.count():

            item = row_layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        # --------------------------------------------------
        # USUNIĘCIE LAYOUTU
        # --------------------------------------------------

        self.data_layout.removeItem(
            row_layout
        )

        # --------------------------------------------------
        # USUNIĘCIE Z REJESTRU
        # --------------------------------------------------

        del self._elements[name]

    # ======================================================
    # CZYSZCZENIE
    # ======================================================

    def clear(self) -> None:

        # --------------------------------------------------
        # USUWAMY WSZYSTKIE WIERSZE
        # --------------------------------------------------

        for name in list(
            self._elements.keys()
        ):

            self._remove_element(
                name
            )

        # --------------------------------------------------
        # STATUS
        # --------------------------------------------------

        self.set_status(
            "Brak danych",
            "gray",
        )

        # --------------------------------------------------
        # ODŚWIEŻENIE GEOMETRII
        # --------------------------------------------------

        self.data_layout.invalidate()
        self.layout_main.invalidate()

        self.updateGeometry()
        self.adjustSize()