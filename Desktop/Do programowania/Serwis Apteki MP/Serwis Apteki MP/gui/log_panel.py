from PySide6.QtWidgets import QTextEdit


class LogPanel(QTextEdit):

    def __init__(self):

        super().__init__()

        self.setReadOnly(True)

    def add(self, text):

        self.append(text)