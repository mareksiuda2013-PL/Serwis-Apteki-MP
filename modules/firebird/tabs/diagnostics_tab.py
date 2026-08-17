from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
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

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        layout.setSpacing(
            14
        )

        # ==================================================
        # NAGŁÓWEK
        # ==================================================

        header_layout = QHBoxLayout()

        title = QLabel(
            "Diagnostyka bazy Firebird"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        header_layout.addWidget(
            title
        )

        header_layout.addStretch()

        self.refresh_button = QPushButton(
            "Odśwież diagnostykę"
        )

        self.refresh_button.setMinimumWidth(
            180
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        header_layout.addWidget(
            self.refresh_button
        )

        layout.addLayout(
            header_layout
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = QLabel(
            "Sprawdzanie..."
        )

        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status_label.setMinimumHeight(
            38
        )

        self.status_label.setStyleSheet(
            """
            QLabel {
                background: #6c757d;
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            self.status_label
        )

        # ==================================================
        # INFORMACJE TECHNICZNE
        # ==================================================

        technical_group = QGroupBox(
            "Informacje techniczne"
        )

        technical_form = QFormLayout(
            technical_group
        )

        technical_form.setHorizontalSpacing(
            30
        )

        technical_form.setVerticalSpacing(
            8
        )

        self.lbl_database = self._create_value_label()
        self.lbl_ods = self._create_value_label()
        self.lbl_page_size = self._create_value_label()
        self.lbl_buffers = self._create_value_label()
        self.lbl_dialect = self._create_value_label()
        self.lbl_generation = self._create_value_label()
        self.lbl_creation = self._create_value_label()

        technical_form.addRow(
            "Baza:",
            self.lbl_database,
        )

        technical_form.addRow(
            "ODS:",
            self.lbl_ods,
        )

        technical_form.addRow(
            "Page Size:",
            self.lbl_page_size,
        )

        technical_form.addRow(
            "Page Buffers:",
            self.lbl_buffers,
        )

        technical_form.addRow(
            "Dialect:",
            self.lbl_dialect,
        )

        technical_form.addRow(
            "Generation:",
            self.lbl_generation,
        )

        technical_form.addRow(
            "Creation Date:",
            self.lbl_creation,
        )

        layout.addWidget(
            technical_group
        )

        # ==================================================
        # TRANSAKCJE
        # ==================================================

        transactions_group = QGroupBox(
            "Transakcje"
        )

        transactions_form = QFormLayout(
            transactions_group
        )

        transactions_form.setHorizontalSpacing(
            30
        )

        transactions_form.setVerticalSpacing(
            8
        )

        self.lbl_oldest = self._create_value_label()
        self.lbl_active = self._create_value_label()
        self.lbl_snapshot = self._create_value_label()
        self.lbl_next = self._create_value_label()

        transactions_form.addRow(
            "Oldest Transaction:",
            self.lbl_oldest,
        )

        transactions_form.addRow(
            "Oldest Active:",
            self.lbl_active,
        )

        transactions_form.addRow(
            "Oldest Snapshot:",
            self.lbl_snapshot,
        )

        transactions_form.addRow(
            "Next Transaction:",
            self.lbl_next,
        )

        layout.addWidget(
            transactions_group
        )

        # ==================================================
        # KONFIGURACJA BAZY
        # ==================================================

        config_group = QGroupBox(
            "Konfiguracja bazy"
        )

        config_form = QFormLayout(
            config_group
        )

        config_form.setHorizontalSpacing(
            30
        )

        config_form.setVerticalSpacing(
            8
        )

        self.lbl_sweep = self._create_value_label()
        self.lbl_force_write = self._create_value_label()
        self.lbl_no_reserve = self._create_value_label()

        config_form.addRow(
            "Sweep Interval:",
            self.lbl_sweep,
        )

        config_form.addRow(
            "Force Write:",
            self.lbl_force_write,
        )

        config_form.addRow(
            "No Reserve:",
            self.lbl_no_reserve,
        )

        layout.addWidget(
            config_group
        )

        # ==================================================
        # ROZPYCHACZ
        # ==================================================

        layout.addStretch()

        # ==================================================
        # PIERWSZE ŁADOWANIE
        # ==================================================

        self.refresh()

    # ======================================================
    # TWORZENIE LABELA
    # ======================================================

    def _create_value_label(self) -> QLabel:

        label = QLabel(
            "-"
        )

        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        label.setStyleSheet(
            """
            QLabel {
                color: #202020;
                font-weight: normal;
            }
            """
        )

        return label

    # ======================================================
    # KOLOROWANIE WARTOŚCI
    # ======================================================

    def _set_value(
        self,
        label: QLabel,
        value: str,
        color: str | None = None,
    ) -> None:

        label.setText(
            str(value)
        )

        if color:

            label.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    font-weight: bold;
                }}
                """
            )

        else:

            label.setStyleSheet(
                """
                QLabel {
                    color: #202020;
                    font-weight: normal;
                }
                """
            )

    # ======================================================
    # STATUS
    # ======================================================

    def _set_status(
        self,
        text: str,
        color: str,
    ) -> None:

        self.status_label.setText(
            text
        )

        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                background: {color};
                color: white;
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }}
            """
        )

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        self.refresh_button.setEnabled(
            False
        )

        try:

            # --------------------------------------------------
            # POBIERAMY STATYSTYKI
            # --------------------------------------------------

            stats = self.controller.statistics()

            # --------------------------------------------------
            # BAZA
            # --------------------------------------------------

            try:

                database = self.controller.database()

            except Exception:

                database = "-"

            self._set_value(
                self.lbl_database,
                database,
            )

            # --------------------------------------------------
            # INFORMACJE TECHNICZNE
            # --------------------------------------------------

            self._set_value(
                self.lbl_ods,
                stats.ods or "-",
            )

            self._set_value(
                self.lbl_page_size,
                stats.page_size,
            )

            self._set_value(
                self.lbl_buffers,
                stats.page_buffers,
            )

            self._set_value(
                self.lbl_dialect,
                stats.database_dialect,
            )

            self._set_value(
                self.lbl_generation,
                stats.generation,
            )

            self._set_value(
                self.lbl_creation,
                stats.creation_date or "-",
            )

            # --------------------------------------------------
            # TRANSAKCJE
            # --------------------------------------------------

            self._set_value(
                self.lbl_oldest,
                stats.oldest_transaction,
            )

            self._set_value(
                self.lbl_active,
                stats.oldest_active,
            )

            self._set_value(
                self.lbl_snapshot,
                stats.oldest_snapshot,
            )

            self._set_value(
                self.lbl_next,
                stats.next_transaction,
            )

            # --------------------------------------------------
            # SWEEP
            # --------------------------------------------------

            self._set_value(
                self.lbl_sweep,
                stats.sweep_interval,
            )

            # --------------------------------------------------
            # FORCE WRITE
            # --------------------------------------------------

            if stats.forced_writes:

                self._set_value(
                    self.lbl_force_write,
                    "ON",
                    "#28a745",
                )

            else:

                self._set_value(
                    self.lbl_force_write,
                    "OFF",
                    "#dc3545",
                )

            # --------------------------------------------------
            # NO RESERVE
            # --------------------------------------------------

            if stats.no_reserve:

                self._set_value(
                    self.lbl_no_reserve,
                    "ON",
                    "#28a745",
                )

            else:

                self._set_value(
                    self.lbl_no_reserve,
                    "OFF",
                    "#dc3545",
                )

            # --------------------------------------------------
            # STATUS
            # --------------------------------------------------

            self._set_status(
                "BAZA ZDROWA",
                "#28a745",
            )

        except Exception as exc:

            self._set_status(
                "BŁĄD DIAGNOSTYKI",
                "#dc3545",
            )

            error_text = str(
                exc
            )

            self._set_value(
                self.lbl_database,
                error_text,
                "#dc3545",
            )

        finally:

            self.refresh_button.setEnabled(
                True
            )