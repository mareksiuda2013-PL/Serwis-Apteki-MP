from PySide6.QtWidgets import QWidget, QListWidget, QVBoxLayout


class Sidebar(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)

        self.menu = QListWidget()

        items = [
            
        ]

        self.menu.addItems(items)
        self.menu.setCurrentRow(0)

        layout.addWidget(self.menu)