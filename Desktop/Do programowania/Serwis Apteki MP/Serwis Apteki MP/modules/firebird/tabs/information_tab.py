from __future__ import annotations

from PySide6.QtWidgets import (
    QFileDialog,
    QWidget,
    QLabel,
    QPushButton,
    QFormLayout,
    QVBoxLayout,
)

from modules.firebird.controller import FirebirdController


class InformationTab(QWidget):

    def __init__(self):
        super().__init__()

        self.controller = FirebirdController()

        layout = QVBoxLayout(self)

        self.form = QFormLayout()

        self.lbl_installed = QLabel("-")
        self.lbl_version = QLabel("-")
        self.lbl_ods = QLabel("-")
        self.lbl_dialect = QLabel("-")
        self.lbl_page_size = QLabel("-")
        self.lbl_tables = QLabel("-")

        self.lbl_service = QLabel("-")
        self.lbl_status = QLabel("-")
        self.lbl_install = QLabel("-")
        self.lbl_bin = QLabel("-")
        self.lbl_port = QLabel("-")

        self.lbl_gbak = QLabel("-")
        self.lbl_gfix = QLabel("-")
        self.lbl_isql = QLabel("-")
        self.lbl_fbclient = QLabel("-")

        self.lbl_db_size = QLabel("-")
        self.lbl_db_date = QLabel("-")

        self.form.addRow("Zainstalowany:", self.lbl_installed)
        self.form.addRow("Wersja Firebird:", self.lbl_version)
        self.form.addRow("ODS:", self.lbl_ods)
        self.form.addRow("SQL Dialect:", self.lbl_dialect)
        self.form.addRow("Page Size:", self.lbl_page_size)
        self.form.addRow("Liczba tabel:", self.lbl_tables)

        self.form.addRow("Usługa:", self.lbl_service)
        self.form.addRow("Status:", self.lbl_status)
        self.form.addRow("Instalacja:", self.lbl_install)
        self.form.addRow("BIN:", self.lbl_bin)
        self.form.addRow("Port:", self.lbl_port)

        self.form.addRow("gbak.exe:", self.lbl_gbak)
        self.form.addRow("gfix.exe:", self.lbl_gfix)
        self.form.addRow("isql.exe:", self.lbl_isql)
        self.form.addRow("fbclient.dll:", self.lbl_fbclient)

        self.form.addRow("Rozmiar bazy:", self.lbl_db_size)
        self.form.addRow("Data modyfikacji:", self.lbl_db_date)

        layout.addLayout(self.form)

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_button)

        self.database_button = QPushButton("Wybierz bazę")
        self.database_button.clicked.connect(self.select_database)
        layout.addWidget(self.database_button)

        layout.addStretch()

        self.refresh()

    def refresh(self):

        info = self.controller.info()

        self.lbl_installed.setText("TAK" if info.installed else "NIE")

        self.lbl_version.setText(info.version or "-")
        self.lbl_ods.setText(info.ods or "-")
        self.lbl_dialect.setText(str(info.sql_dialect))
        self.lbl_page_size.setText(str(info.page_size))
        self.lbl_tables.setText(str(info.tables))

        self.lbl_service.setText(info.service_name or "-")
        self.lbl_status.setText(info.service_status or "-")
        self.lbl_install.setText(str(info.install_path) if info.install_path else "-")
        self.lbl_bin.setText(str(info.bin_path) if info.bin_path else "-")
        self.lbl_port.setText(str(info.port))

        self.lbl_gbak.setText("✔" if info.gbak_exists else "✖")
        self.lbl_gfix.setText("✔" if info.gfix_exists else "✖")
        self.lbl_isql.setText("✔" if info.isql_exists else "✖")
        self.lbl_fbclient.setText("✔" if info.fbclient_exists else "✖")

    def select_database(self):

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz bazę Firebird",
            "",
            "Firebird (*.fdb *.gdb)",
        )

        if not file_name:
            return

        info = self.controller.inspect_database(file_name)

        self.lbl_db_size.setText(f"{info.size_gb:.2f} GB")

        if info.modified:
            self.lbl_db_date.setText(
                info.modified.strftime("%Y-%m-%d %H:%M")
            )
        else:
            self.lbl_db_date.setText("-")