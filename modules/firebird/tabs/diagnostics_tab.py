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


class DiagnosticsTab(QWidget):
    """
    Zakładka diagnostyki bazy Firebird.

    Pokazuje:
        - aktualny stan diagnostyczny,
        - Health Check,
        - rekomendacje,
        - statystyki bazy.
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

        layout.setSpacing(
            10
        )

        # ==================================================
        # NAGŁÓWEK
        # ==================================================

        title = QLabel(
            "Diagnostyka bazy Firebird"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        # ==================================================
        # STATUS DIAGNOSTYCZNY
        # ==================================================

        self.diagnostic_message = QLabel(
            "-"
        )

        self.diagnostic_message.setWordWrap(
            True
        )

        self.diagnostic_message.setMinimumHeight(
            40
        )

        self.diagnostic_message.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )

        self.set_diagnostic_style(
            "success"
        )

        layout.addWidget(
            self.diagnostic_message
        )

        # ==================================================
        # HEALTH CHECK
        # ==================================================

        health_group = QGroupBox(
            "Health Check"
        )

        health_layout = QVBoxLayout(
            health_group
        )

        health_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        self.lbl_health_summary = QLabel(
            "-"
        )

        self.lbl_health_summary.setWordWrap(
            True
        )

        health_layout.addWidget(
            self.lbl_health_summary
        )

        self.health_form = QFormLayout()

        self.lbl_health_ods = QLabel("-")
        self.lbl_health_page_size = QLabel("-")
        self.lbl_health_sweep = QLabel("-")
        self.lbl_health_transactions = QLabel("-")
        self.lbl_health_active = QLabel("-")
        self.lbl_health_force_write = QLabel("-")
        self.lbl_health_no_reserve = QLabel("-")

        self.health_form.addRow(
            "ODS:",
            self.lbl_health_ods,
        )

        self.health_form.addRow(
            "Page Size:",
            self.lbl_health_page_size,
        )

        self.health_form.addRow(
            "Sweep:",
            self.lbl_health_sweep,
        )

        self.health_form.addRow(
            "Transakcje:",
            self.lbl_health_transactions,
        )

        self.health_form.addRow(
            "Oldest Active:",
            self.lbl_health_active,
        )

        self.health_form.addRow(
            "Force Write:",
            self.lbl_health_force_write,
        )

        self.health_form.addRow(
            "No Reserve:",
            self.lbl_health_no_reserve,
        )

        health_layout.addLayout(
            self.health_form
        )

        layout.addWidget(
            health_group
        )

        # ==================================================
        # REKOMENDACJE
        # ==================================================

        recommendation_group = QGroupBox(
            "Rekomendacje"
        )

        recommendation_layout = QVBoxLayout(
            recommendation_group
        )

        recommendation_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        self.recommendation_message = QLabel(
            "-"
        )

        self.recommendation_message.setWordWrap(
            True
        )

        self.recommendation_message.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        recommendation_layout.addWidget(
            self.recommendation_message
        )

        layout.addWidget(
            recommendation_group
        )

        # ==================================================
        # STATYSTYKI
        # ==================================================

        statistics_group = QGroupBox(
            "Statystyki bazy"
        )

        statistics_layout = QVBoxLayout(
            statistics_group
        )

        statistics_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        self.form = QFormLayout()

        self.lbl_ods = QLabel("-")
        self.lbl_page_size = QLabel("-")
        self.lbl_buffers = QLabel("-")
        self.lbl_sweep = QLabel("-")

        self.lbl_oldest = QLabel("-")
        self.lbl_active = QLabel("-")
        self.lbl_snapshot = QLabel("-")
        self.lbl_next = QLabel("-")

        self.lbl_dialect = QLabel("-")
        self.lbl_generation = QLabel("-")
        self.lbl_force_write = QLabel("-")
        self.lbl_no_reserve = QLabel("-")
        self.lbl_creation = QLabel("-")

        self.form.addRow(
            "ODS:",
            self.lbl_ods,
        )

        self.form.addRow(
            "Page Size:",
            self.lbl_page_size,
        )

        self.form.addRow(
            "Page Buffers:",
            self.lbl_buffers,
        )

        self.form.addRow(
            "Sweep Interval:",
            self.lbl_sweep,
        )

        self.form.addRow(
            "Oldest Transaction:",
            self.lbl_oldest,
        )

        self.form.addRow(
            "Oldest Active:",
            self.lbl_active,
        )

        self.form.addRow(
            "Oldest Snapshot:",
            self.lbl_snapshot,
        )

        self.form.addRow(
            "Next Transaction:",
            self.lbl_next,
        )

        self.form.addRow(
            "Database Dialect:",
            self.lbl_dialect,
        )

        self.form.addRow(
            "Generation:",
            self.lbl_generation,
        )

        self.form.addRow(
            "Force Write:",
            self.lbl_force_write,
        )

        self.form.addRow(
            "No Reserve:",
            self.lbl_no_reserve,
        )

        self.form.addRow(
            "Creation Date:",
            self.lbl_creation,
        )

        statistics_layout.addLayout(
            self.form
        )

        layout.addWidget(
            statistics_group
        )

        # ==================================================
        # PRZYCISK
        # ==================================================

        self.refresh_button = QPushButton(
            "Odśwież diagnostykę"
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

        layout.addStretch(
            1
        )

        # ==================================================
        # START
        # ==================================================

        self.refresh()

    # ======================================================
    # DIAGNOSTIC STYLE
    # ======================================================

    def set_diagnostic_style(
        self,
        status: str,
    ) -> None:

        status = status.lower()

        if status == "error":

            self.diagnostic_message.setStyleSheet(
                """
                QLabel {
                    background-color: #dc3545;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                """
            )

        elif status == "warning":

            self.diagnostic_message.setStyleSheet(
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

            self.diagnostic_message.setStyleSheet(
                """
                QLabel {
                    background-color: #28a745;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 5px;
                }
                """
            )

    # ======================================================
    # HEALTH STYLE
    # ======================================================

    def set_health_style(
        self,
        label: QLabel,
        status: str,
    ) -> None:

        status = status.upper()

        if status == "ERROR":

            label.setStyleSheet(
                """
                QLabel {
                    color: #dc3545;
                    font-weight: bold;
                }
                """
            )

        elif status == "WARNING":

            label.setStyleSheet(
                """
                QLabel {
                    color: #d39e00;
                    font-weight: bold;
                }
                """
            )

        else:

            label.setStyleSheet(
                """
                QLabel {
                    color: #198754;
                    font-weight: bold;
                }
                """
            )

    # ======================================================
    # HEALTH CHECK
    # ======================================================

    def update_health_check(
        self,
        health,
    ) -> None:

        self.lbl_health_summary.setText(
            f"{health.status} — {health.summary}"
        )

        self.set_health_style(
            self.lbl_health_summary,
            health.status,
        )

        labels = {
            "ODS": self.lbl_health_ods,
            "Page Size": self.lbl_health_page_size,
            "Sweep Interval": self.lbl_health_sweep,
            "Transakcje": self.lbl_health_transactions,
            "Oldest Active": self.lbl_health_active,
            "Force Write": self.lbl_health_force_write,
            "No Reserve": self.lbl_health_no_reserve,
        }

        for check in health.checks:

            label = labels.get(
                check.name
            )

            if label is None:
                continue

            label.setText(
                f"{check.value} — {check.status}"
            )

            self.set_health_style(
                label,
                check.status,
            )

    # ======================================================
    # RECOMMENDATIONS
    # ======================================================

    def set_recommendations(
        self,
        recommendations,
    ) -> None:

        if not recommendations:

            self.recommendation_message.setText(
                "Brak dodatkowych rekomendacji."
            )

            return

        lines = []

        for recommendation in recommendations:

            lines.append(
                f"• {recommendation}"
            )

        self.recommendation_message.setText(
            "<br>".join(lines)
        )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        self.refresh_button.setEnabled(
            False
        )

        try:

            stats = (
                self.controller.statistics()
            )

            diagnostic = (
                self.controller.diagnostics()
            )

            health = (
                self.controller.health()
            )

            recommendation_result = (
                self.controller.recommendations(
                    diagnostic
                )
            )

        except Exception as exc:

            self.diagnostic_message.setText(
                f"Błąd diagnostyki: {exc}"
            )

            self.set_diagnostic_style(
                "error"
            )

            self.lbl_health_summary.setText(
                f"ERROR — {exc}"
            )

            self.set_health_style(
                self.lbl_health_summary,
                "ERROR",
            )

            self.recommendation_message.setText(
                "Nie udało się wygenerować rekomendacji."
            )

            self._clear_statistics()

            self.refresh_button.setEnabled(
                True
            )

            return

        # ==================================================
        # DIAGNOSTYKA
        # ==================================================

        self.diagnostic_message.setText(
            diagnostic.message
        )

        self.set_diagnostic_style(
            diagnostic.status
        )

        # ==================================================
        # HEALTH CHECK
        # ==================================================

        self.update_health_check(
            health
        )

        # ==================================================
        # REKOMENDACJE
        # ==================================================

        self.set_recommendations(
            recommendation_result.recommendations
        )

        # ==================================================
        # STATYSTYKI
        # ==================================================

        self.lbl_ods.setText(
            stats.ods or "-"
        )

        self.lbl_page_size.setText(
            str(stats.page_size)
        )

        self.lbl_buffers.setText(
            str(stats.page_buffers)
        )

        self.lbl_sweep.setText(
            str(stats.sweep_interval)
        )

        self.lbl_oldest.setText(
            str(stats.oldest_transaction)
        )

        self.lbl_active.setText(
            str(stats.oldest_active)
        )

        self.lbl_snapshot.setText(
            str(stats.oldest_snapshot)
        )

        self.lbl_next.setText(
            str(stats.next_transaction)
        )

        self.lbl_dialect.setText(
            str(stats.database_dialect)
        )

        self.lbl_generation.setText(
            str(stats.generation)
        )

        self.lbl_force_write.setText(
            "ON"
            if stats.forced_writes
            else "OFF"
        )

        self.lbl_no_reserve.setText(
            "ON"
            if stats.no_reserve
            else "OFF"
        )

        self.lbl_creation.setText(
            stats.creation_date or "-"
        )

        self.refresh_button.setEnabled(
            True
        )

    # ======================================================
    # CLEAR
    # ======================================================

    def _clear_statistics(
        self,
    ) -> None:

        labels = (
            self.lbl_ods,
            self.lbl_page_size,
            self.lbl_buffers,
            self.lbl_sweep,
            self.lbl_oldest,
            self.lbl_active,
            self.lbl_snapshot,
            self.lbl_next,
            self.lbl_dialect,
            self.lbl_generation,
            self.lbl_force_write,
            self.lbl_no_reserve,
            self.lbl_creation,
            self.lbl_health_ods,
            self.lbl_health_page_size,
            self.lbl_health_sweep,
            self.lbl_health_transactions,
            self.lbl_health_active,
            self.lbl_health_force_write,
            self.lbl_health_no_reserve,
        )

        for label in labels:

            label.setText("-")