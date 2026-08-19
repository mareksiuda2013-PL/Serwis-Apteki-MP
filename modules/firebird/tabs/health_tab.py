from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.firebird.firebird_controller import (
    FirebirdController,
)


class HealthTab(QWidget):
    """
    Zakładka kontroli zdrowia bazy Firebird.
    """

    def __init__(
        self,
        controller: FirebirdController,
    ) -> None:

        super().__init__()

        self.controller = controller

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        layout.setSpacing(10)

        # ==================================================
        # NAGŁÓWEK
        # ==================================================

        title = QLabel(
            "Stan bazy Firebird"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(title)

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "SPRAWDZANIE..."
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setMinimumHeight(
            42
        )

        layout.addWidget(
            self.status_label
        )

        # ==================================================
        # PODSUMOWANIE
        # ==================================================

        self.summary_label = QLabel(
            "-"
        )

        self.summary_label.setWordWrap(
            True
        )

        layout.addWidget(
            self.summary_label
        )

        # ==================================================
        # KONTROLE
        # ==================================================

        checks_group = QGroupBox(
            "Kontrole"
        )

        checks_layout = QVBoxLayout(
            checks_group
        )

        checks_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        self.form = QFormLayout()

        self.lbl_transactions = QLabel("-")
        self.lbl_force_write = QLabel("-")
        self.lbl_no_reserve = QLabel("-")

        self.form.addRow(
            "Transakcje:",
            self.lbl_transactions,
        )

        self.form.addRow(
            "Force Write:",
            self.lbl_force_write,
        )

        self.form.addRow(
            "No Reserve:",
            self.lbl_no_reserve,
        )

        checks_layout.addLayout(
            self.form
        )

        layout.addWidget(
            checks_group
        )

        # ==================================================
        # PRZYCISK
        # ==================================================

        self.refresh_button = QPushButton(
            "Sprawdź bazę"
        )

        self.refresh_button.setMinimumHeight(
            36
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        layout.addWidget(
            self.refresh_button
        )

        layout.addStretch(1)

        # ==================================================
        # START
        # ==================================================

        self.refresh()

    # ======================================================
    # STATUS STYLE
    # ======================================================

    def set_status_style(
        self,
        status: str,
    ) -> None:

        if status == "ERROR":

            self.status_label.setStyleSheet(
                """
                QLabel {
                    background-color: #dc3545;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                """
            )

        elif status == "WARNING":

            self.status_label.setStyleSheet(
                """
                QLabel {
                    background-color: #ffc107;
                    color: #202020;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                """
            )

        else:

            self.status_label.setStyleSheet(
                """
                QLabel {
                    background-color: #28a745;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                """
            )

    # ======================================================
    # CHECK STATUS
    # ======================================================

    def format_check(
        self,
        check,
    ) -> str:

        return (
            f"{check.status} | "
            f"{check.value} | "
            f"{check.message}"
        )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        self.refresh_button.setEnabled(
            False
        )

        try:

            health = (
                self.controller.health()
            )

        except Exception as exc:

            self.status_label.setText(
                "ERROR"
            )

            self.set_status_style(
                "ERROR"
            )

            self.summary_label.setText(
                f"Błąd kontroli bazy: {exc}"
            )

            self._clear()

            self.refresh_button.setEnabled(
                True
            )

            return

        # ==================================================
        # STATUS GŁÓWNY
        # ==================================================

        self.status_label.setText(
            health.status
        )

        self.set_status_style(
            health.status
        )

        self.summary_label.setText(
            health.summary or "-"
        )

        # ==================================================
        # KONTROLE
        # ==================================================

        for check in health.checks:

            if check.name == "Transakcje":

                self.lbl_transactions.setText(
                    self.format_check(check)
                )

            elif check.name == "Force Write":

                self.lbl_force_write.setText(
                    self.format_check(check)
                )

            elif check.name == "No Reserve":

                self.lbl_no_reserve.setText(
                    self.format_check(check)
                )

        self.refresh_button.setEnabled(
            True
        )

    # ======================================================
    # CLEAR
    # ======================================================

    def _clear(self) -> None:

        self.lbl_transactions.setText("-")
        self.lbl_force_write.setText("-")
        self.lbl_no_reserve.setText("-")