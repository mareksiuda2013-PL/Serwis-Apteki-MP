from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from core.database import initialize_database
from core.settings import settings
from core.logger import logger

from gui.main_window import MainWindow


def main() -> None:

    # ==================================================
    # INICJALIZACJA BAZY DANYCH
    # ==================================================

    initialize_database()

    # ==================================================
    # DOMYŚLNE USTAWIENIA
    # ==================================================

    if settings.get("theme") is None:
        settings.set("theme", "dark")

    logger.info("Ustawienia załadowane")

    # ==================================================
    # QT APPLICATION
    # ==================================================

    app = QApplication(sys.argv)

    # ==================================================
    # GLOBALNY STYL
    # ==================================================

    app.setStyleSheet(
        """
        /* ==================================================
           GŁÓWNE OKNO
           ================================================== */

        QMainWindow {
            background-color: #eeeeee;
        }

        QWidget {
            color: #202020;
        }

        QLabel {
            color: #202020;
        }

        /* ==================================================
           STACK / STRONY
           ================================================== */

        QStackedWidget {
            background-color: #eeeeee;
            border: none;
        }

        QStackedWidget > QWidget {
            background-color: #eeeeee;
        }

        /* ==================================================
           LEWE MENU
           ================================================== */

        QListWidget {
            background-color: #2f343a;
            color: #ffffff;
            border: none;
            outline: none;
        }

        QListWidget::item {
            color: #ffffff;
            background-color: transparent;
            padding: 10px 12px;
            border: none;
        }

        QListWidget::item:hover {
            background-color: #454b52;
            color: #ffffff;
        }

        QListWidget::item:selected {
            background-color: #0d6efd;
            color: #ffffff;
        }

        /* ==================================================
           STATUS BAR
           ================================================== */

        QStatusBar {
            background-color: #eeeeee;
            color: #202020;
        }

        /* ==================================================
           PRZYCISKI
           ================================================== */

        QPushButton {
            color: #202020;
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #f0f0f0;
        }

        QPushButton:pressed {
            background-color: #e0e0e0;
        }

        /* ==================================================
           POLA TEKSTOWE
           ================================================== */

        QTextEdit,
        QLineEdit {
            color: #202020;
            background-color: #ffffff;
            border: 1px solid #cccccc;
        }

        /* ==================================================
           TABY FIREBIRD
           ================================================== */

        QTabWidget {
            color: #202020;
        }

        QTabBar::tab {
            color: #202020;
            background-color: #e0e0e0;
            padding: 8px 14px;
            border: 1px solid #cccccc;
        }

        QTabBar::tab:selected {
            color: #202020;
            background-color: #ffffff;
        }

        /* ==================================================
           FORMULARZE
           ================================================== */

        QFormLayout {
            color: #202020;
        }

        /* ==================================================
           OKNA DIALOGOWE
           ================================================== */

        QMessageBox {
            background-color: #eeeeee;
            color: #202020;
        }

        QMessageBox QLabel {
            color: #202020;
            background-color: transparent;
        }

        QMessageBox QPushButton {
            color: #202020;
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 6px 18px;
        }

        QMessageBox QPushButton:hover {
            background-color: #f0f0f0;
        }

        QMessageBox QPushButton:pressed {
            background-color: #e0e0e0;
        }
        """
    )

    # ==================================================
    # MAIN WINDOW
    # ==================================================

    window = MainWindow()

    window.show()

    # ==================================================
    # START QT
    # ==================================================

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()