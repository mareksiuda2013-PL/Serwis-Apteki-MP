from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.logger import logger
from core.module_manager import ModuleManager
from gui.log_panel import LogPanel
from gui.sidebar import Sidebar
from gui.statusbar import StatusBar


class MainWindow(QMainWindow):
    """
    Główne okno aplikacji.
    """

    def __init__(self) -> None:
        super().__init__()

        self.module_manager = ModuleManager()

        self.sidebar: Sidebar
        self.stack: QStackedWidget
        self.log_panel: LogPanel

        self._create_ui()
        self._connect_signals()
        self._load_modules()
        self._initialize()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _create_ui(self) -> None:

        self.setWindowTitle("Serwis Apteki MP")
        self.resize(1400, 850)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)

        content_layout = QHBoxLayout()

        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack, 1)

        root_layout.addLayout(content_layout)

        self.log_panel = LogPanel()
        self.log_panel.setMaximumHeight(180)
        root_layout.addWidget(self.log_panel)

        self.setStatusBar(StatusBar())

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:

        self.sidebar.menu.currentRowChanged.connect(
            self._change_page
        )

        logger.set_callback(self.log_panel.add)

    # ------------------------------------------------------------------
    # MODULES
    # ------------------------------------------------------------------

    def _load_modules(self) -> None:

        self.module_manager.load()

        self.sidebar.menu.clear()

        while self.stack.count():

            widget = self.stack.widget(0)

            self.stack.removeWidget(widget)

            widget.deleteLater()

        for module in self.module_manager.modules:

            self.sidebar.menu.addItem(module.name)

            self.stack.addWidget(module.widget)

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------

    def _initialize(self) -> None:

        if self.module_manager.modules:
            self.sidebar.menu.setCurrentRow(0)

        logger.info("Program uruchomiony.")

    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    def _change_page(self, index: int) -> None:

        if index < 0:
            return

        self.stack.setCurrentIndex(index)

        try:
            module = self.module_manager.modules[index]
        except IndexError:
            return

        logger.info(f"Wybrano moduł: {module.name}")