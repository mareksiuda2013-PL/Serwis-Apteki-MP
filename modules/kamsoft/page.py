from __future__ import annotations

import subprocess

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.settings import settings
from services.kamsoft import KamsoftService


class KamsoftPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.service = KamsoftService()

        saved_path = settings.get("kamsoft.install_path")

        if saved_path:
            self.service.set_install_path(saved_path)

        self._build_ui()
        self._refresh_status()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Kamsoft")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        description = QLabel(
            "Konfiguracja i diagnostyka instalacji KS-AOW."
        )
        layout.addWidget(description)

        config_group = QGroupBox("Konfiguracja KS-AOW")
        config_layout = QVBoxLayout(config_group)

        path_layout = QHBoxLayout()

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText(
            "Wybierz katalog instalacyjny KS-AOW"
        )

        browse_button = QPushButton("Wybierz")
        browse_button.clicked.connect(self._choose_directory)

        check_button = QPushButton("Sprawdź")
        check_button.clicked.connect(self._check_path)

        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)
        path_layout.addWidget(check_button)

        config_layout.addLayout(path_layout)
        layout.addWidget(config_group)

        info_group = QGroupBox("Informacje")
        info_layout = QVBoxLayout(info_group)

        self.ks_status = QLabel()
        self.access_status = QLabel()
        self.apman_status = QLabel()
        self.apman_ini_status = QLabel()
        self.version_status = QLabel()
        self.size_status = QLabel()

        info_layout.addWidget(self.ks_status)
        info_layout.addWidget(self.access_status)
        info_layout.addWidget(self.apman_status)
        info_layout.addWidget(self.apman_ini_status)
        info_layout.addWidget(self.version_status)
        info_layout.addWidget(self.size_status)

        layout.addWidget(info_group)

        diagnostic_group = QGroupBox("Diagnostyka")
        diagnostic_layout = QVBoxLayout(diagnostic_group)

        self.diagnostic_status = QLabel(
            "Wynik diagnostyki: nie wykonano"
        )
        self.diagnostic_status.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        self.diagnostic_details = QTextEdit()
        self.diagnostic_details.setReadOnly(True)
        self.diagnostic_details.setMinimumHeight(120)

        diagnostic_button = QPushButton(
            "Uruchom diagnostykę"
        )
        diagnostic_button.clicked.connect(
            self._run_diagnostics
        )

        diagnostic_layout.addWidget(self.diagnostic_status)
        diagnostic_layout.addWidget(self.diagnostic_details)
        diagnostic_layout.addWidget(diagnostic_button)

        layout.addWidget(diagnostic_group)

        tools_group = QGroupBox("Narzędzia")
        tools_layout = QHBoxLayout(tools_group)

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.clicked.connect(
            self._refresh_status
        )

        self.apman_button = QPushButton("Uruchom APMAN")
        self.apman_button.clicked.connect(
            self._run_apman
        )

        tools_layout.addWidget(self.refresh_button)
        tools_layout.addWidget(self.apman_button)

        layout.addWidget(tools_group)

        layout.addStretch()

    def _choose_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Wybierz katalog KS-AOW",
        )

        if not directory:
            return

        self.service.set_install_path(directory)
        settings.set(
            "kamsoft.install_path",
            directory,
        )

        self._refresh_status()
        self._reset_diagnostics()

    def _check_path(self) -> None:
        path = self.path_edit.text().strip()

        if not path:
            QMessageBox.warning(
                self,
                "Kamsoft",
                "Wybierz katalog KS-AOW.",
            )
            return

        self.service.set_install_path(path)
        settings.set(
            "kamsoft.install_path",
            path,
        )

        self._refresh_status()
        self._reset_diagnostics()

    def _refresh_status(self) -> None:
        path = self.service.install_path

        if path is None:
            self.path_edit.clear()

            self.ks_status.setText(
                "Katalog KS-AOW: nie skonfigurowano"
            )
            self.access_status.setText(
                "Dostęp do katalogu: —"
            )
            self.apman_status.setText(
                "APMAN.EXE: —"
            )
            self.apman_ini_status.setText(
                "APMAN.INI: —"
            )
            self.version_status.setText(
                "Wersja APMAN: —"
            )
            self.size_status.setText(
                "Rozmiar APMAN: —"
            )

            self.apman_button.setEnabled(False)
            return

        self.path_edit.setText(str(path))

        diagnostics = self.service.diagnostics()

        if diagnostics["path_exists"]:
            self.ks_status.setText(
                "Katalog KS-AOW: OK"
            )
        else:
            self.ks_status.setText(
                "Katalog KS-AOW: NIE ZNALEZIONO"
            )

        if diagnostics["accessible"]:
            self.access_status.setText(
                "Dostęp do katalogu: OK"
            )
        else:
            self.access_status.setText(
                "Dostęp do katalogu: BRAK"
            )

        if diagnostics["apman_exists"]:
            self.apman_status.setText(
                "APMAN.EXE: OK"
            )
            self.apman_button.setEnabled(True)
        else:
            self.apman_status.setText(
                "APMAN.EXE: NIE ZNALEZIONO"
            )
            self.apman_button.setEnabled(False)

        if diagnostics["apman_ini_exists"]:
            self.apman_ini_status.setText(
                "APMAN.INI: OK"
            )
        else:
            self.apman_ini_status.setText(
                "APMAN.INI: NIE ZNALEZIONO"
            )

        version = self.service.version()

        if version:
            self.version_status.setText(
                f"Wersja APMAN: {version}"
            )
        else:
            self.version_status.setText(
                "Wersja APMAN: nieznana"
            )

        size = diagnostics["apman_size"]

        if size is not None:
            formatted_size = f"{size:,}".replace(",", " ")
            self.size_status.setText(
                f"Rozmiar APMAN: {formatted_size} B"
            )
        else:
            self.size_status.setText(
                "Rozmiar APMAN: —"
            )

    def _run_diagnostics(self) -> None:
        result = self.service.diagnostic_result()

        status = result["status"]

        self.diagnostic_status.setText(
            f"Wynik diagnostyki: {status}"
        )

        details: list[str] = []

        errors = result["errors"]
        warnings = result["warnings"]

        if errors:
            details.append("BŁĘDY:")
            details.extend(
                f"• {error}"
                for error in errors
            )

        if warnings:
            if details:
                details.append("")

            details.append("OSTRZEŻENIA:")
            details.extend(
                f"• {warning}"
                for warning in warnings
            )

        if not errors and not warnings:
            details.append(
                "• Wszystkie sprawdzane elementy są prawidłowe."
            )

        self.diagnostic_details.setPlainText(
            "\n".join(details)
        )

    def _reset_diagnostics(self) -> None:
        self.diagnostic_status.setText(
            "Wynik diagnostyki: nie wykonano"
        )
        self.diagnostic_details.clear()

    def _run_apman(self) -> None:
        apman = self.service.apman_path()

        if apman is None or not apman.is_file():
            QMessageBox.warning(
                self,
                "Kamsoft",
                "Nie znaleziono APMAN.EXE.",
            )
            return

        try:
            subprocess.Popen(
                [str(apman)],
                cwd=str(apman.parent),
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                "Kamsoft",
                f"Nie udało się uruchomić APMAN.EXE:\n{exc}",
            )