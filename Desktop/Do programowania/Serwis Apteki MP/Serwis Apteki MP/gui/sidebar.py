from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout


class Sidebar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.menu = QListWidget()

        items = [
            "Dashboard",
            "Bazy danych",
            "Firebird",
            "Kamsoft",
            "Diagnostyka",
            "Narzędzia",
            "Raporty",
            "Ustawienia"
        ]

        self.menu.addItems(items)
        self.menu.setCurrentRow(0)

        layout.addWidget(self.menu)