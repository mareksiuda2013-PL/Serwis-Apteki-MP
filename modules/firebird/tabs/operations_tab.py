from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)

from core.logger import logger


class OperationsTab(QWidget):
    """
    Panel operacji administracyjnych Firebird.

    Obsługiwane operacje:
        - Backup
        - Validate
        - Sweep
        - Restore
        - MEND

    Operacje są wykonywane przez dedykowane serwisy
    znajdujące się w services.firebird.
    """

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        # ==================================================
        # LAYOUT GŁÓWNY
        # ==================================================

        layout = QVBoxLayout(self)

        # ==================================================
        # STATUS
        # ==================================================

        self.status = QLabel(
            "Gotowy."
        )

        self.status.setMinimumHeight(
            28
        )

        layout.addWidget(
            self.status
        )

        # ==================================================
        # OPERACJE — WIERSZ 1
        # ==================================================

        row1 = QHBoxLayout()

        self.backup_button = QPushButton(
            "Backup"
        )

        self.validate_button = QPushButton(
            "Validate"
        )

        self.sweep_button = QPushButton(
            "Sweep"
        )

        row1.addWidget(
            self.backup_button
        )

        row1.addWidget(
            self.validate_button
        )

        row1.addWidget(
            self.sweep_button
        )

        layout.addLayout(
            row1
        )

        # ==================================================
        # OPERACJE — WIERSZ 2
        # ==================================================

        row2 = QHBoxLayout()

        self.restore_button = QPushButton(
            "Restore"
        )

        self.mend_button = QPushButton(
            "MEND"
        )

        row2.addWidget(
            self.restore_button
        )

        row2.addWidget(
            self.mend_button
        )

        layout.addLayout(
            row2
        )

        # ==================================================
        # LOG
        # ==================================================

        layout.addWidget(
            QLabel("Log operacji:")
        )

        self.log_panel = QTextEdit()

        self.log_panel.setReadOnly(
            True
        )

        self.log_panel.setMinimumHeight(
            220
        )

        layout.addWidget(
            self.log_panel
        )

        # ==================================================
        # CZYSZCZENIE LOGU
        # ==================================================

        self.clear_log_button = QPushButton(
            "Wyczyść log"
        )

        self.clear_log_button.clicked.connect(
            self.log_panel.clear
        )

        layout.addWidget(
            self.clear_log_button
        )

        layout.addStretch()

        # ==================================================
        # SIGNALS
        # ==================================================

        self.backup_button.clicked.connect(
            self.backup
        )

        self.validate_button.clicked.connect(
            self.validate
        )

        self.sweep_button.clicked.connect(
            self.sweep
        )

        self.restore_button.clicked.connect(
            self.restore
        )

        self.mend_button.clicked.connect(
            self.mend
        )

        # ==================================================
        # LOGGER
        # ==================================================

        logger.add_callback(
            self.log_panel.append
        )

    # ======================================================
    # STATUS
    # ======================================================

    def set_status(
        self,
        text: str,
    ) -> None:

        self.status.setText(
            text
        )

    # ======================================================
    # ENABLE / DISABLE
    # ======================================================

    def set_operations_enabled(
        self,
        enabled: bool,
    ) -> None:

        self.backup_button.setEnabled(
            enabled
        )

        self.validate_button.setEnabled(
            enabled
        )

        self.sweep_button.setEnabled(
            enabled
        )

        self.restore_button.setEnabled(
            enabled
        )

        self.mend_button.setEnabled(
            enabled
        )

    # ======================================================
    # DATABASE
    # ======================================================

    def refresh_database(
        self,
    ) -> None:

        """
        Odświeża informacje o aktualnej bazie.

        Nie powoduje błędu, jeżeli odświeżenie
        informacji nie powiedzie się po operacji.
        """

        try:

            self.controller.info()

        except Exception as exc:

            logger.error(
                f"Błąd odświeżania informacji Firebird: {exc}"
            )

    # ======================================================
    # OPERATION START
    # ======================================================

    def operation_started(
        self,
        text: str,
    ) -> None:

        self.set_operations_enabled(
            False
        )

        self.set_status(
            text
        )

        logger.info(
            text
        )

    # ======================================================
    # OPERATION FINISH
    # ======================================================

    def operation_finished(
        self,
        text: str,
    ) -> None:

        self.set_operations_enabled(
            True
        )

        self.set_status(
            text
        )

        logger.info(
            text
        )

        self.refresh_database()

    # ======================================================
    # BACKUP
    # ======================================================

    def backup(self) -> None:

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz backup Firebird",
            "",
            "Firebird Backup (*.fbk)",
        )

        if not file_name:
            return

        destination = Path(
            file_name
        )

        if destination.suffix.lower() != ".fbk":

            destination = destination.with_suffix(
                ".fbk"
            )

        # --------------------------------------------------
        # POTWIERDZENIE
        # --------------------------------------------------

        answer = QMessageBox.question(
            self,
            "Backup Firebird",
            (
                "Czy wykonać backup aktualnej bazy?\n\n"
                f"Plik:\n{destination}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if answer != QMessageBox.Yes:
            return

        from services.firebird.backup_service import (
            BackupService,
        )

        self.operation_started(
            "Trwa wykonywanie backupu..."
        )

        try:

            ok, log = BackupService().backup(
                destination
            )

            if ok:

                self.operation_finished(
                    "Backup zakończony pomyślnie."
                )

                QMessageBox.information(
                    self,
                    "Backup",
                    (
                        "Backup zakończony pomyślnie.\n\n"
                        f"Plik:\n{destination}"
                    ),
                )

            else:

                self.operation_finished(
                    "Backup zakończony błędem."
                )

                QMessageBox.critical(
                    self,
                    "Backup",
                    log or "Backup nie powiódł się.",
                )

        except Exception as exc:

            self.set_operations_enabled(
                True
            )

            self.set_status(
                "Błąd backupu."
            )

            logger.error(
                f"BACKUP ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "Backup",
                str(exc),
            )

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(self) -> None:

        answer = QMessageBox.question(
            self,
            "Validate Firebird",
            (
                "Czy wykonać pełną walidację bazy danych?\n\n"
                "Operacja może potrwać dłuższą chwilę."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if answer != QMessageBox.Yes:
            return

        from services.firebird.validate_service import (
            ValidateService,
        )

        self.operation_started(
            "Trwa walidacja bazy..."
        )

        try:

            result = ValidateService().validate()

            if result.success:

                self.operation_finished(
                    "Walidacja zakończona."
                )

                QMessageBox.information(
                    self,
                    "Validate",
                    result.stdout
                    or "Walidacja zakończona pomyślnie.",
                )

            else:

                self.operation_finished(
                    "Walidacja wykazała problem."
                )

                QMessageBox.warning(
                    self,
                    "Validate",
                    result.stderr
                    or result.stdout
                    or "Walidacja wykazała problem.",
                )

        except Exception as exc:

            self.set_operations_enabled(
                True
            )

            self.set_status(
                "Błąd walidacji."
            )

            logger.error(
                f"VALIDATE ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "Validate",
                str(exc),
            )

    # ======================================================
    # SWEEP
    # ======================================================

    def sweep(self) -> None:

        answer = QMessageBox.question(
            self,
            "Sweep Firebird",
            (
                "Czy wykonać Sweep bazy danych?\n\n"
                "Operacja może potrwać dłuższą chwilę."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )

        if answer != QMessageBox.Yes:
            return

        from services.firebird.sweep_service import (
            SweepService,
        )

        self.operation_started(
            "Trwa Sweep..."
        )

        try:

            result = SweepService().sweep()

            if result.success:

                self.operation_finished(
                    "Sweep zakończony pomyślnie."
                )

                QMessageBox.information(
                    self,
                    "Sweep",
                    result.stdout
                    or "Sweep zakończony pomyślnie.",
                )

            else:

                self.operation_finished(
                    "Sweep zakończony błędem."
                )

                QMessageBox.warning(
                    self,
                    "Sweep",
                    result.stderr
                    or result.stdout
                    or "Sweep nie powiódł się.",
                )

        except Exception as exc:

            self.set_operations_enabled(
                True
            )

            self.set_status(
                "Błąd Sweep."
            )

            logger.error(
                f"SWEEP ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "Sweep",
                str(exc),
            )

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(self) -> None:

        backup_file, _ = QFileDialog.getOpenFileName(
            self,
            "Wybierz backup Firebird",
            "",
            "Firebird Backup (*.fbk)",
        )

        if not backup_file:
            return

        database_file, _ = QFileDialog.getSaveFileName(
            self,
            "Wybierz bazę docelową",
            "",
            "Firebird Database (*.fdb)",
        )

        if not database_file:
            return

        database_file = str(
            Path(database_file)
        )

        # --------------------------------------------------
        # OSTRZEŻENIE
        # --------------------------------------------------

        answer = QMessageBox.warning(
            self,
            "UWAGA — RESTORE",
            (
                "Restore utworzy / nadpisze bazę docelową.\n\n"
                f"Backup:\n{backup_file}\n\n"
                f"Baza docelowa:\n{database_file}\n\n"
                "Czy na pewno chcesz kontynuować?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        from services.firebird.restore_service import (
            RestoreService,
        )

        self.operation_started(
            "Trwa przywracanie bazy..."
        )

        try:

            ok, log = RestoreService().restore(
                backup_file,
                database_file,
                replace=True,
            )

            if ok:

                self.operation_finished(
                    "Restore zakończony pomyślnie."
                )

                QMessageBox.information(
                    self,
                    "Restore",
                    (
                        "Restore zakończony pomyślnie.\n\n"
                        f"Baza:\n{database_file}"
                    ),
                )

            else:

                self.operation_finished(
                    "Restore zakończony błędem."
                )

                QMessageBox.critical(
                    self,
                    "Restore",
                    log or "Restore nie powiódł się.",
                )

        except Exception as exc:

            self.set_operations_enabled(
                True
            )

            self.set_status(
                "Błąd Restore."
            )

            logger.error(
                f"RESTORE ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "Restore",
                str(exc),
            )

    # ======================================================
    # MEND
    # ======================================================

    def mend(self) -> None:

        answer = QMessageBox.warning(
            self,
            "UWAGA — MEND",
            (
                "OPERACJA NAPRAWCZA\n\n"
                "MEND jest operacją ingerującą w strukturę "
                "bazy danych.\n\n"
                "Przed wykonaniem upewnij się, że posiadasz "
                "aktualny backup bazy.\n\n"
                "Zalecane jest również wykonanie Validate "
                "przed MEND.\n\n"
                "Czy na pewno chcesz kontynuować?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        from services.firebird.mend_service import (
            MendService,
        )

        self.operation_started(
            "Trwa operacja MEND..."
        )

        try:

            result = MendService().mend()

            if result.success:

                self.operation_finished(
                    "MEND zakończony pomyślnie."
                )

                QMessageBox.information(
                    self,
                    "MEND",
                    result.stdout
                    or "MEND zakończony pomyślnie.",
                )

            else:

                self.operation_finished(
                    "MEND zakończony błędem."
                )

                QMessageBox.critical(
                    self,
                    "MEND",
                    result.stderr
                    or result.stdout
                    or "MEND nie powiódł się.",
                )

        except Exception as exc:

            self.set_operations_enabled(
                True
            )

            self.set_status(
                "Błąd MEND."
            )

            logger.error(
                f"MEND ERROR: {exc}"
            )

            QMessageBox.critical(
                self,
                "MEND",
                str(exc),
            )

    # ======================================================
    # CLEANUP
    # ======================================================

    def closeEvent(self, event) -> None:

        try:

            logger.remove_callback(
                self.log_panel.append
            )

        except Exception:

            pass

        event.accept()