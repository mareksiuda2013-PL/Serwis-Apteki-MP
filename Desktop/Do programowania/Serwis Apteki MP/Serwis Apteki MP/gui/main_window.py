from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
)

from gui.sidebar import Sidebar
from gui.dashboard import Dashboard
from gui.page import Page
from gui.statusbar import StatusBar
from gui.log_panel import LogPanel

from modules.database.widget import DatabaseWidget

from core.logger import logger


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Serwis Apteki MP")
        self.resize(1400, 850)

        # Centralny widget
        central = QWidget()
        self.setCentralWidget(central)

        # Główny układ (widoki + logi)
        main_layout = QVBoxLayout(central)

        # Górna część
        top_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = Sidebar()
        top_layout.addWidget(self.sidebar)

        # Obszar roboczy
        self.stack = QStackedWidget()

        self.stack.addWidget(Dashboard())               # 0
        self.stack.addWidget(DatabaseWidget())          # 1
        self.stack.addWidget(Page("Firebird"))          # 2
        self.stack.addWidget(Page("Kamsoft"))           # 3
        self.stack.addWidget(Page("Diagnostyka"))       # 4
        self.stack.addWidget(Page("Narzędzia"))         # 5
        self.stack.addWidget(Page("Raporty"))           # 6
        self.stack.addWidget(Page("Ustawienia"))        # 7

        top_layout.addWidget(self.stack, 1)

        # Dodaj górną część do głównego układu
        main_layout.addLayout(top_layout)

        # Panel logów
        self.log_panel = LogPanel()
        self.log_panel.setMaximumHeight(180)

        main_layout.addWidget(self.log_panel)

        # StatusBar
        self.setStatusBar(StatusBar())

        # Logger
        logger.set_callback(self.log_panel.add)
        logger.info("Program uruchomiony")

        # Przełączanie modułów
        self.sidebar.menu.currentRowChanged.connect(
            self.change_page
        )

    def change_page(self, index):

        self.stack.setCurrentIndex(index)

        pages = [
            "Dashboard",
            "Bazy danych",
            "Firebird",
            "Kamsoft",
            "Diagnostyka",
            "Narzędzia",
            "Raporty",
            "Ustawienia",
        ]

        if 0 <= index < len(pages):
            logger.info(f"Wybrano moduł: {pages[index]}")