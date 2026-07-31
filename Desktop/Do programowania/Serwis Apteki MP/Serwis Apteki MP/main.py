import sys

from PySide6.QtWidgets import QApplication

from core.database import initialize_database
from core.settings import settings
from core.logger import logger

from gui.main_window import MainWindow


def main():
    # Inicjalizacja bazy danych
    initialize_database()

    # Domyślne ustawienia
    if settings.get("theme") is None:
        settings.set("theme", "dark")

    logger.info("Ustawienia załadowane")

    # Uruchomienie aplikacji
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()