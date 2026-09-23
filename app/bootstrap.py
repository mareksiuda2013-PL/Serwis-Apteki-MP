import sys

from PySide6.QtWidgets import QApplication

from core.database import initialize_database
from core.logger import logger
from core.settings import settings
from gui.main_window import MainWindow


def run() -> None:
    """Uruchamia aplikacjÄ™."""

    initialize_database()

    if settings.get("theme") is None:
        settings.set("theme", "dark")

    logger.info("Ustawienia zaĹ‚adowane")

    application = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(application.exec())
