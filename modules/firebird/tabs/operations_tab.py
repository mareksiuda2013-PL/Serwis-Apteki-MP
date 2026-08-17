from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
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

    def __init__(
        self,
        controller,
    ) -> None:

        super().__init__()

        self.controller = controller

        # ==================================================
        # GŁÓWNY LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        layout.setSpacing(
            12
        )

        # ==================================================
        # NAGŁÓWEK
        # ==================================================

        title = QLabel(
            "Operacje administracyjne Firebird"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Operacje wykonywane są na aktualnie skonfigurowanej bazie danych."
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #555555;
            }
            """
        )

        layout.addWidget(
            description
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status = QLabel(
            "Gotowy."
        )

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.status.setMinimumHeight(
            32
        )

        self.status.setStyleSheet(
            """
            QLabel {
                background-color: #e9ecef;
                color: #202020;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            self.status
        )

        # ==================================================
        # OPERACJE BEZPIECZNE
        # ==================================================

        safe_group = QGroupBox(
            "Operacje diagnostyczne i konserwacyjne"
        )

        safe_layout = QHBoxLayout(
            safe_group
        )

        safe_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        safe_layout.setSpacing(
            10
        )

        # --------------------------------------------------
        # BACKUP
        # --------------------------------------------------

        self.backup_button = QPushButton(
            "Backup"
        )

        self.backup_button.setMinimumHeight(
            38
        )

        self.backup_button.setToolTip(
            "Utwórz kopię zapasową bazy Firebird."
        )

        # --------------------------------------------------
        # VALIDATE
        # --------------------------------------------------

        self.validate_button = QPushButton(
            "Validate"
        )

        self.validate_button.setMinimumHeight(
            38
        )

        self.validate_button.setToolTip(
            "Sprawdź poprawność struktury bazy danych."
        )

        # --------------------------------------------------
        # SWEEP
        # --------------------------------------------------

        self.sweep_button = QPushButton(
            "Sweep"
        )

        self.sweep_button.setMinimumHeight(
            38
        )

        self.sweep_button.setToolTip(
            "Wykonaj Sweep bazy danych."
        )

        safe_layout.addWidget(
            self.backup_button
        )

        safe_layout.addWidget(
            self.validate_button
        )

        safe_layout.addWidget(
            self.sweep_button
        )

        layout.addWidget(
            safe_group
        )

        # ==================================================
        # OPERACJE INGERUJĄCE
        # ==================================================

        dangerous_group = QGroupBox(
            "Operacje wymagające szczególnej ostrożności"
        )

        dangerous_layout = QHBoxLayout(
            dangerous_group
        )

        dangerous_layout.setContentsMargins(
            10,
            14,
            10,
            10,
        )

        dangerous_layout.setSpacing(
            10
        )

        # --------------------------------------------------
        # RESTORE
        # --------------------------------------------------

        self.restore_button = QPushButton(
            "Restore"
        )

        self.restore_button.setMinimumHeight(
            38
        )

        self.restore_button.setToolTip(
            "Przywróć bazę z pliku FBK."
        )

        # --------------------------------------------------
        # MEND
        # --------------------------------------------------

        self.mend_button = QPushButton(
            "MEND"
        )

        self.mend_button.setMinimumHeight(
            38
        )

        self.mend_button.setToolTip(
            "Wykonaj operację naprawczą MEND."
        )

        dangerous_layout.addWidget(
            self.restore_button
        )

        dangerous_layout.addWidget(
            self.mend_button
        )

        layout.addWidget(
            dangerous_group
        )

        # ==================================================
        # LOG
        # ==================================================

        log_header = QHBoxLayout()

        log_label = QLabel(
            "Log operacji"
        )

        log_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
            }
            """
        )

        log_header.addWidget(
            log_label
        )

        log_header.addStretch()

        self.clear_log_button = QPushButton(
            "Wyczyść log"
        )

        self.clear_log_button.setFixedWidth(
            110
        )

        log_header.addWidget(
            self.clear_log_button
        )

        layout.addLayout(
            log_header
        )

        # ==================================================
        # PANEL LOGU
        # ==================================================

        self.log_panel = QTextEdit()

        self.log_panel.setReadOnly(
            True
        )

        self.log_panel.setMinimumHeight(
            220
        )

        self.log_panel.setPlaceholderText(
            "Tutaj pojawi się wynik wykonanych operacji..."
        )

        self.log_panel.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #fafafa;
                padding: 6px;
                font-family: Consolas;
                font-size: 10pt;
            }
            """
        )

        layout.addWidget(
            self.log_panel
        )

        # ==================================================
        # ROZPYCHACZ
        # ==================================================

        layout.addStretch(
            1
        )

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

        self.clear_log_button.clicked.connect(
            self.log_panel.clear
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
        color: str = "normal",
    ) -> None:

        colors = {
            "normal": (
                "#e9ecef",
                "#202020",
            ),
            "success": (
                "#28a745",
                "#ffffff",
            ),
            "warning": (
                "#ffc107",
                "#202020",
            ),
            "error": (
                "#dc3545",
                "#ffffff",
            ),
            "info": (
                "#0d6efd",
                "#ffffff",
            ),
        }

        background, foreground = colors.get(
            color,
            colors["normal"],
        )

        self.status.setText(
            str(text)
        )

        self.status.setStyleSheet(
            f"""
            QLabel {{
                background-color: {background};
                color: {foreground};
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }}
            """
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
            text,
            "info",
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
        color: str = "success",
    ) -> None:

        self.set_operations_enabled(
            True
        )

        self.set_status(
            text,
            color,
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
                    "Backup zakończony pomyślnie.",
                    "success",
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
                    "Backup zakończony błędem.",
                    "error",
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
                "Błąd backupu.",
                "error",
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
                    "Walidacja zakończona.",
                    "success",
                )

                QMessageBox.information(
                    self,
                    "Validate",
                    result.stdout
                    or "Walidacja zakończona pomyślnie.",
                )

            else:

                self.operation_finished(
                    "Walidacja wykazała problem.",
                    "warning",
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
                "Błąd walidacji.",
                "error",
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
                    "Sweep zakończony pomyślnie.",
                    "success",
                )

                QMessageBox.information(
                    self,
                    "Sweep",
                    result.stdout
                    or "Sweep zakończony pomyślnie.",
                )

            else:

                self.operation_finished(
                    "Sweep zakończony błędem.",
                    "error",
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
                "Błąd Sweep.",
                "error",
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
                    "Restore zakończony pomyślnie.",
                    "success",
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
                    "Restore zakończony błędem.",
                    "error",
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
                "Błąd Restore.",
                "error",
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

        from services.firebird.operation_service import (
            FirebirdOperationService,
        )

        self.operation_started(
            "Trwa operacja MEND..."
        )

        operation_service = FirebirdOperationService()

        result = operation_service.execute(
            lambda: MendService().mend(),
            "MEND",
        )

        if result.success:

            self.operation_finished(
                "MEND zakończony pomyślnie.",
                "success",
            )

            QMessageBox.information(
                self,
                "MEND",
                result.message
                or "MEND zakończony pomyślnie.",
            )

        else:

            self.operation_finished(
                "MEND zakończony błędem.",
                "error",
            )

            QMessageBox.critical(
                self,
                "MEND",
                result.message
                or "MEND nie powiódł się.",
            )

    # ======================================================
    # CLEANUP
    # ======================================================

    def closeEvent(
        self,
        event,
    ) -> None:

        try:

            logger.remove_callback(
                self.log_panel.append
            )

        except Exception:

            pass

        event.accept()