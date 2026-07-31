from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from .tabs import InformationTab


class FirebirdPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        tabs.addTab(
            InformationTab(),
            "Informacje",
        )

        layout.addWidget(tabs)