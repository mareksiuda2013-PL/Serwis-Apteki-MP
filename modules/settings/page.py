from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.config import Config
from core.settings import settings


class SettingsPage(QWidget):
    """Moduł konfiguracji aplikacji Serwis Apteki MP."""

    def __init__(self) -> None:
        super().__init__()

        self.config = Config()

        self._build_ui()
        self._load_settings()

    def _build_ui(self) -> None:
        self.setObjectName("SettingsPage")

        self.setStyleSheet(
            """
            QWidget#SettingsPage {
                background-color: #f2f2f2;
                color: #202020;
            }

            QLabel {
                color: #202020;
            }

            QGroupBox {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                margin-top: 10px;
                padding: 10px;
                font-weight: bold;
                color: #202020;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            QLineEdit {
                background-color: #ffffff;
                color: #202020;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 7px;
            }

            QPushButton {
                background-color: #ffffff;
                color: #202020;
                border: 1px solid #bdbdbd;
                border-radius: 5px;
                padding: 7px 14px;
            }

            QPushButton:hover {
                background-color: #e9e9e9;
            }

            QPushButton:pressed {
                background-color: #dddddd;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Ustawienia")
        title.setStyleSheet(
            """
            font-size: 26px;
            font-weight: bold;
            color: #202020;
            """
        )
        layout.addWidget(title)

        description = QLabel(
            "Konfiguracja programu Serwis Apteki MP."
        )
        description.setStyleSheet(
            """
            font-size: 14px;
            color: #555555;
            """
        )
        layout.addWidget(description)

        kamsoft_group = QGroupBox("Kamsoft / KS-AOW")
        kamsoft_layout = QVBoxLayout(kamsoft_group)

        path_layout = QHBoxLayout()

        self.kamsoft_path_edit = QLineEdit()
        self.kamsoft_path_edit.setPlaceholderText(
            "Wybierz katalog instalacyjny KS-AOW"
        )

        browse_button = QPushButton("Wybierz")
        browse_button.clicked.connect(
            self._choose_kamsoft_directory
        )

        path_layout.addWidget(self.kamsoft_path_edit)
        path_layout.addWidget(browse_button)

        kamsoft_layout.addLayout(path_layout)

        layout.addWidget(kamsoft_group)

        firebird_group = QGroupBox("Firebird")
        firebird_layout = QVBoxLayout(firebird_group)

        database_layout = QHBoxLayout()

        database_label = QLabel("Baza danych:")

        self.database_edit = QLineEdit()
        self.database_edit.setReadOnly(True)

        database_layout.addWidget(database_label)
        database_layout.addWidget(self.database_edit)

        firebird_layout.addLayout(database_layout)

        user_layout = QHBoxLayout()

        user_label = QLabel("Użytkownik:")

        self.user_edit = QLineEdit()

        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_edit)

        firebird_layout.addLayout(user_layout)

        password_layout = QHBoxLayout()

        password_label = QLabel("Hasło:")

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)

        firebird_layout.addLayout(password_layout)

        layout.addWidget(firebird_group)

        buttons_layout = QHBoxLayout()

        self.save_button = QPushButton("Zapisz")
        self.save_button.clicked.connect(
            self._save_settings
        )

        self.refresh_button = QPushButton("Odśwież")
        self.refresh_button.clicked.connect(
            self._load_settings
        )

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        layout.addStretch()

    def _load_settings(self) -> None:
        """Wczytuje zapisane ustawienia."""

        kamsoft_path = settings.get(
            "kamsoft.install_path",
            "",
        )

        self.kamsoft_path_edit.setText(
            str(kamsoft_path)
            if kamsoft_path
            else ""
        )

        try:
            self.database_edit.setText(
                self.config.database
            )
        except Exception:
            self.database_edit.clear()

        try:
            self.user_edit.setText(
                self.config.user
            )
        except Exception:
            self.user_edit.clear()

        try:
            self.password_edit.setText(
                self.config.password
            )
        except Exception:
            self.password_edit.clear()

    def _choose_kamsoft_directory(self) -> None:
        """Otwiera wybór katalogu KS-AOW."""

        current_path = self.kamsoft_path_edit.text().strip()

        start_directory = (
            current_path
            if current_path and Path(current_path).is_dir()
            else ""
        )

        directory = QFileDialog.getExistingDirectory(
            self,
            "Wybierz katalog KS-AOW",
            start_directory,
        )

        if directory:
            self.kamsoft_path_edit.setText(directory)

    def _save_settings(self) -> None:
        """Zapisuje ustawienia aplikacji."""

        kamsoft_path = (
            self.kamsoft_path_edit.text().strip()
        )

        if kamsoft_path:
            settings.set(
                "kamsoft.install_path",
                kamsoft_path,
            )

        user = self.user_edit.text().strip()
        password = self.password_edit.text()

        self.config.save_user(user)
        self.config.save_password(password)

        QMessageBox.information(
            self,
            "Ustawienia",
            "Ustawienia zostały zapisane.",
        )