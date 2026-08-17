from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class Page(QWidget):

    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)

        label = QLabel(title)
        label.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)

        layout.addWidget(label)
        layout.addStretch()