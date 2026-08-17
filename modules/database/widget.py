from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QGridLayout,
    QVBoxLayout
)


class DatabaseWidget(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title = QLabel("Bazy danych")
        title.setStyleSheet("""
            font-size:26px;
            font-weight:bold;
        """)

        main_layout.addWidget(title)

        grid = QGridLayout()

        self.btn_backup = QPushButton("💾 Backup")
        self.btn_restore = QPushButton("♻ Restore")
        self.btn_validate = QPushButton("✔ Validate")
        self.btn_sweep = QPushButton("🧹 Sweep")
        self.btn_rebuild = QPushButton("🔧 Odbudowa")

        buttons = [
            self.btn_backup,
            self.btn_restore,
            self.btn_validate,
            self.btn_sweep,
            self.btn_rebuild
        ]

        for button in buttons:
            button.setMinimumHeight(70)

        grid.addWidget(self.btn_backup, 0, 0)
        grid.addWidget(self.btn_restore, 0, 1)
        grid.addWidget(self.btn_validate, 1, 0)
        grid.addWidget(self.btn_sweep, 1, 1)
        grid.addWidget(self.btn_rebuild, 2, 0, 1, 2)

        main_layout.addLayout(grid)
        main_layout.addStretch()