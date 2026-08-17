from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.firebird.controller import FirebirdController


class DiagnosticsTab(QWidget):

    def __init__(
        self,
        controller: FirebirdController,
    ) -> None:

        super().__init__()

        self.controller = controller

        layout = QVBoxLayout(self)

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

        layout.addLayout(
            self.form
        )

        self.refresh_button = QPushButton(
            "Odśwież diagnostykę"
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        layout.addWidget(
            self.refresh_button
        )

        layout.addStretch()

        self.refresh()

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        try:

            stats = self.controller.statistics()

        except Exception as exc:

            self.lbl_ods.setText(
                f"Błąd: {exc}"
            )

            return

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