from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
)


class DashboardCard(QFrame):
    """
    Uniwersalna karta Dashboardu.

    Każdy element karty zajmuje własny wiersz.
    Linie oraz paski korzystają ze wspólnego
    systemu numerowania wierszy.
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

        self._rows: dict[str, tuple[QLabel, QLabel]] = {}
        self._progress_bars: dict[str, QProgressBar] = {}

        # ==================================================
        # KARTA
        # ==================================================

        self.setObjectName(
            "DashboardCard"
        )

        self.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.setStyleSheet(
            """
            QFrame#DashboardCard {
                border: 1px solid #D8D8D8;
                border-radius: 8px;
                background: white;
            }

            QLabel {
                font-size: 10pt;
            }
            """
        )

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        layout.setSpacing(
            8
        )

        # ==================================================
        # TYTUŁ
        # ==================================================

        self.title_label = QLabel(
            f"{icon}  {title}"
        )

        self.title_label.setMinimumHeight(
            26
        )

        self.title_label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                font-size: 15px;
                font-weight: bold;
                background: transparent;
            }
            """
        )

        layout.addWidget(
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

        layout.addWidget(
            self.status_label
        )

        self.set_status(
            "Brak danych",
            "gray",
        )

        # ==================================================
        # GRID
        # ==================================================

        self.grid = QGridLayout()

        self.grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.grid.setHorizontalSpacing(
            12
        )

        self.grid.setVerticalSpacing(
            7
        )

        self.grid.setColumnMinimumWidth(
            0,
            85,
        )

        self.grid.setColumnStretch(
            1,
            1,
        )

        layout.addLayout(
            self.grid
        )

        layout.addStretch(
            1
        )

    # ======================================================
    # NUMER NASTĘPNEGO WIERSZA
    # ======================================================

    def _next_row(self) -> int:
        """
        Zwraca pierwszy wolny numer wiersza.

        Linie i paski korzystają z tego samego
        mechanizmu, więc nie mogą wejść na siebie.
        """

        used_rows: list[int] = []

        for key_label, value_label in self._rows.values():

            position = self.grid.getItemPosition(
                self.grid.indexOf(key_label)
            )

            used_rows.append(
                position[0]
            )

        for progress in self._progress_bars.values():

            position = self.grid.getItemPosition(
                self.grid.indexOf(progress)
            )

            used_rows.append(
                position[0]
            )

        row = 0

        while row in used_rows:

            row += 1

        return row

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
                border-radius: 4px;
                padding: 4px;
                color: white;
                background: {background};
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
        # ISTNIEJĄCA LINIA
        # --------------------------------------------------

        if name in self._rows:

            key_label, value_label = self._rows[name]

            key_label.setText(
                f"{name}:"
            )

            value_label.setText(
                value
            )

            return

        # --------------------------------------------------
        # JEŻELI ISTNIEJE PASEK O TEJ SAMEJ NAZWIE
        # --------------------------------------------------

        if name in self._progress_bars:

            self._remove_progress(
                name
            )

        # --------------------------------------------------
        # NOWY WIERSZ
        # --------------------------------------------------

        row = self._next_row()

        key_label = QLabel(
            f"{name}:"
        )

        key_label.setMinimumHeight(
            24
        )

        key_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
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

        value_label = QLabel(
            value
        )

        value_label.setMinimumHeight(
            24
        )

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )

        # --------------------------------------------------
        # WAŻNE:
        # Uptime i inne wartości nie zawijają się.
        # --------------------------------------------------

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

        self.grid.addWidget(
            key_label,
            row,
            0,
        )

        self.grid.addWidget(
            value_label,
            row,
            1,
        )

        self._rows[name] = (
            key_label,
            value_label,
        )

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
        # ISTNIEJĄCY PASEK
        # --------------------------------------------------

        if name in self._progress_bars:

            progress = self._progress_bars[name]

            progress.setValue(
                value
            )

            self._set_progress_color(
                progress,
                value,
            )

            return

        # --------------------------------------------------
        # JEŻELI ISTNIEJE ZWYKŁA LINIA O TEJ SAMEJ NAZWIE
        # --------------------------------------------------

        if name in self._rows:

            self._remove_line(
                name
            )

        # --------------------------------------------------
        # NOWY WIERSZ
        # --------------------------------------------------

        row = self._next_row()

        label = QLabel(
            f"{name}:"
        )

        label.setMinimumHeight(
            22
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
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
            20
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

        self.grid.addWidget(
            label,
            row,
            0,
        )

        self.grid.addWidget(
            progress,
            row,
            1,
        )

        self._progress_bars[name] = progress

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
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background: #EEEEEE;
                text-align: center;
                color: #202020;
                height: 18px;
            }}

            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
            """
        )

    # ======================================================
    # USUWANIE ZWYKŁEJ LINII
    # ======================================================

    def _remove_line(
        self,
        name: str,
    ) -> None:

        if name not in self._rows:
            return

        key_label, value_label = self._rows[name]

        self.grid.removeWidget(
            key_label
        )

        self.grid.removeWidget(
            value_label
        )

        key_label.deleteLater()
        value_label.deleteLater()

        del self._rows[name]

    # ======================================================
    # USUWANIE PASKA
    # ======================================================

    def _remove_progress(
        self,
        name: str,
    ) -> None:

        if name not in self._progress_bars:
            return

        progress = self._progress_bars[name]

        # Etykieta jest w tej samej pozycji
        # kolumny 0.
        index = self.grid.indexOf(
            progress
        )

        if index >= 0:

            row, column, row_span, column_span = (
                self.grid.getItemPosition(index)
            )

            item = self.grid.itemAtPosition(
                row,
                0,
            )

            if item is not None:

                label = item.widget()

                if label is not None:

                    self.grid.removeWidget(
                        label
                    )

                    label.deleteLater()

        self.grid.removeWidget(
            progress
        )

        progress.deleteLater()

        del self._progress_bars[name]

    # ======================================================
    # CZYSZCZENIE
    # ======================================================

    def clear(self) -> None:

        # --------------------------------------------------
        # USUWAMY ZWYKŁE LINIE
        # --------------------------------------------------

        for name in list(
            self._rows.keys()
        ):

            self._remove_line(
                name
            )

        # --------------------------------------------------
        # USUWAMY PASKI
        # --------------------------------------------------

        for name in list(
            self._progress_bars.keys()
        ):

            self._remove_progress(
                name
            )

        # --------------------------------------------------
        # RESET
        # --------------------------------------------------

        self.grid.invalidate()
        self.grid.activate()

        self.set_status(
            "Brak danych",
            "gray",
        )

        self.updateGeometry()