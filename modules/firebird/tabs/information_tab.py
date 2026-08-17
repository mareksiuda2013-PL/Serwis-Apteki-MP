from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.firebird.controller import FirebirdController


class InformationTab(QWidget):

    def __init__(
        self,
        controller: FirebirdController,
    ) -> None:

        super().__init__()

        self.controller = controller

        self.selected_database: str | None = None

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        # ==================================================
        # FORMULARZ
        # ==================================================

        self.form = QFormLayout()

        self.form.setHorizontalSpacing(20)
        self.form.setVerticalSpacing(7)

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.lbl_installed = QLabel("-")
        self.lbl_version = QLabel("-")
        self.lbl_ods = QLabel("-")
        self.lbl_dialect = QLabel("-")
        self.lbl_page_size = QLabel("-")
        self.lbl_tables = QLabel("-")

        # ==================================================
        # USŁUGA
        # ==================================================

        self.lbl_service = QLabel("-")
        self.lbl_status = QLabel("-")

        # ==================================================
        # INSTALACJA
        # ==================================================

        self.lbl_install = QLabel("-")
        self.lbl_bin = QLabel("-")
        self.lbl_port = QLabel("-")

        # ==================================================
        # NARZĘDZIA
        # ==================================================

        self.lbl_gbak = QLabel("-")
        self.lbl_gfix = QLabel("-")
        self.lbl_isql = QLabel("-")
        self.lbl_fbclient = QLabel("-")

        # ==================================================
        # BAZA
        # ==================================================

        self.lbl_database = QLabel("-")
        self.lbl_db_file = QLabel("-")
        self.lbl_db_size = QLabel("-")
        self.lbl_db_date = QLabel("-")

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.form.addRow(
            "Zainstalowany:",
            self.lbl_installed,
        )

        self.form.addRow(
            "Wersja Firebird:",
            self.lbl_version,
        )

        self.form.addRow(
            "ODS:",
            self.lbl_ods,
        )

        self.form.addRow(
            "SQL Dialect:",
            self.lbl_dialect,
        )

        self.form.addRow(
            "Page Size:",
            self.lbl_page_size,
        )

        self.form.addRow(
            "Liczba tabel:",
            self.lbl_tables,
        )

        # ==================================================
        # USŁUGA
        # ==================================================

        self.form.addRow(
            "Usługa:",
            self.lbl_service,
        )

        self.form.addRow(
            "Status:",
            self.lbl_status,
        )

        # ==================================================
        # INSTALACJA
        # ==================================================

        self.form.addRow(
            "Instalacja:",
            self.lbl_install,
        )

        self.form.addRow(
            "BIN:",
            self.lbl_bin,
        )

        self.form.addRow(
            "Port:",
            self.lbl_port,
        )

        # ==================================================
        # NARZĘDZIA
        # ==================================================

        self.form.addRow(
            "gbak.exe:",
            self.lbl_gbak,
        )

        self.form.addRow(
            "gfix.exe:",
            self.lbl_gfix,
        )

        self.form.addRow(
            "isql.exe:",
            self.lbl_isql,
        )

        self.form.addRow(
            "fbclient.dll:",
            self.lbl_fbclient,
        )

        # ==================================================
        # BAZA
        # ==================================================

        self.form.addRow(
            "Baza:",
            self.lbl_database,
        )

        self.form.addRow(
            "Plik:",
            self.lbl_db_file,
        )

        self.form.addRow(
            "Rozmiar:",
            self.lbl_db_size,
        )

        self.form.addRow(
            "Data modyfikacji:",
            self.lbl_db_date,
        )

        layout.addLayout(
            self.form
        )

        # ==================================================
        # PRZYCISKI
        # ==================================================

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton(
            "Odśwież"
        )

        self.database_button = QPushButton(
            "Wybierz bazę"
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addWidget(
            self.database_button
        )

        buttons.addStretch()

        layout.addLayout(
            buttons
        )

        layout.addStretch()

        # ==================================================
        # SIGNALS
        # ==================================================

        self.refresh_button.clicked.connect(
            self.refresh
        )

        self.database_button.clicked.connect(
            self.select_database
        )

        # ==================================================
        # START
        # ==================================================

        self.refresh()

    # ======================================================
    # REFRESH
    # ======================================================

    def refresh(self) -> None:

        try:

            info = self.controller.info(
                database=self.selected_database
            )

        except Exception as exc:

            self.lbl_installed.setText(
                "BŁĄD"
            )

            self.lbl_version.setText(
                str(exc)
            )

            return

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.lbl_installed.setText(
            "TAK"
            if info.installed
            else "NIE"
        )

        self.lbl_version.setText(
            info.version or "-"
        )

        self.lbl_ods.setText(
            info.ods or "-"
        )

        self.lbl_dialect.setText(
            str(info.sql_dialect)
        )

        self.lbl_page_size.setText(
            str(info.page_size)
        )

        self.lbl_tables.setText(
            str(info.tables)
        )

        # ==================================================
        # USŁUGA
        # ==================================================

        self.lbl_service.setText(
            info.service_name or "-"
        )

        self.lbl_status.setText(
            info.service_status or "-"
        )

        # ==================================================
        # INSTALACJA
        # ==================================================

        self.lbl_install.setText(
            str(info.install_path)
            if info.install_path
            else "-"
        )

        self.lbl_bin.setText(
            str(info.bin_path)
            if info.bin_path
            else "-"
        )

        self.lbl_port.setText(
            str(info.port)
        )

        # ==================================================
        # NARZĘDZIA
        # ==================================================

        self.lbl_gbak.setText(
            "✔"
            if info.gbak_exists
            else "✖"
        )

        self.lbl_gfix.setText(
            "✔"
            if info.gfix_exists
            else "✖"
        )

        self.lbl_isql.setText(
            "✔"
            if info.isql_exists
            else "✖"
        )

        self.lbl_fbclient.setText(
            "✔"
            if info.fbclient_exists
            else "✖"
        )

        # ==================================================
        # BAZA
        # ==================================================

        database_path = (
            info.database_path
            or ""
        )

        if database_path:

            database_name = Path(
                database_path
            ).name

            self.lbl_database.setText(
                database_name
            )

        else:

            self.lbl_database.setText(
                "-"
            )

        # ==================================================
        # PLIK
        # ==================================================

        if info.database_exists:

            self.lbl_db_file.setText(
                "OK"
            )

            self.lbl_db_size.setText(
                f"{info.database_size_gb:.2f} GB"
            )

            try:

                modified = Path(
                    database_path
                ).stat().st_mtime

                from datetime import datetime

                date = datetime.fromtimestamp(
                    modified
                )

                self.lbl_db_date.setText(
                    date.strftime(
                        "%Y-%m-%d %H:%M"
                    )
                )

            except (
                OSError,
                ValueError,
            ):

                self.lbl_db_date.setText(
                    "-"
                )

        else:

            self.lbl_db_file.setText(
                "BRAK"
            )

            self.lbl_db_size.setText(
                "-"
            )

            self.lbl_db_date.setText(
                "-"
            )

    # ======================================================
    # SELECT DATABASE
    # ======================================================

    def select_database(self) -> None:

        file_name, _ = (
            QFileDialog.getOpenFileName(
                self,
                "Wybierz bazę Firebird",
                "",
                "Firebird (*.fdb *.gdb);;Wszystkie pliki (*.*)",
            )
        )

        if not file_name:
            return

        self.selected_database = file_name

        self.refresh()