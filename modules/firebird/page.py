from __future__ import annotations

from PySide6.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .controller import FirebirdController
from .tabs.diagnostics_tab import DiagnosticsTab
from .tabs.information_tab import InformationTab
from .tabs.operations_tab import OperationsTab


class FirebirdPage(QWidget):

    def __init__(self) -> None:

        super().__init__()

        # ==================================================
        # CONTROLLER
        # ==================================================

        self.controller = FirebirdController()

        # ==================================================
        # LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        # ==================================================
        # TABS
        # ==================================================

        self.tabs = QTabWidget()

        # --------------------------------------------------
        # INFORMACJE
        # --------------------------------------------------

        self.information_tab = InformationTab(
            self.controller
        )

        self.tabs.addTab(
            self.information_tab,
            "Informacje",
        )

        # --------------------------------------------------
        # DIAGNOSTYKA
        # --------------------------------------------------

        self.diagnostics_tab = DiagnosticsTab(
            self.controller
        )

        self.tabs.addTab(
            self.diagnostics_tab,
            "Diagnostyka",
        )

        # --------------------------------------------------
        # OPERACJE
        # --------------------------------------------------

        self.operations_tab = OperationsTab(
            self.controller
        )

        self.tabs.addTab(
            self.operations_tab,
            "Operacje",
        )

        # ==================================================
        # ADD TABS
        # ==================================================

        layout.addWidget(
            self.tabs
        )