from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QThread,
    Slot,
)

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
from core.operation_worker import OperationWorker

from services.firebird.operation_service import (
    FirebirdOperationService,
)


class OperationsTab(QWidget):
    """
    Panel operacji administracyjnych Firebird.

    Obsługiwane operacje:

        - Backup
        - Validate
        - Sweep
        - Restore
        - MEND

    Operacje wykonywane są w osobnym wątku,
    aby nie blokować interfejsu aplikacji.
    """

    def __init__(
        self,
        controller,
    ) -> None:

        super().__init__()

        self.controller = controller

        # ==================================================
        # THREAD / WORKER
        # ==================================================

        self._thread = None
        self._worker = None

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
        # LOG HEADER
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
        # LOG PANEL
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
    # ASYNCHRONICZNA OPERACJA
    # ======================================================

    def run_async_operation(
        self,
        operation,
        name: str,
        success_text: str,
        error_text: str,
        dialog_title: str,
        warning_on_failure: bool = False,
    ) -> None:

        # --------------------------------------------------
        # CZY INNA OPERACJA DZIAŁA?
        # --------------------------------------------------

        if self._thread is not None:

            if self._thread.isRunning():
                return

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        self.operation_started(
            f"Trwa operacja {name}..."
        )

        operation_service = (
            FirebirdOperationService()
        )

        # --------------------------------------------------
        # WORKER
        # --------------------------------------------------

        worker = OperationWorker(
            lambda: operation_service.execute(
                operation,
                name,
            )
        )

        # --------------------------------------------------
        # THREAD
        # --------------------------------------------------

        thread = QThread()

        worker.moveToThread(
            thread
        )

        self._worker = worker
        self._thread = thread

        # ==================================================
        # SIGNALS THREAD
        # ==================================================

        thread.started.connect(
            worker.run
        )

        # ==================================================
        # WAŻNE:
        # wynik trafia do GUI THREAD
        # ==================================================

        worker.finished.connect(
            self._operation_result,
            Qt.ConnectionType.QueuedConnection,
        )

        worker.error.connect(
            self._operation_error,
            Qt.ConnectionType.QueuedConnection,
        )

        # ==================================================
        # KONIEC THREADU
        # ==================================================

        worker.finished.connect(
            thread.quit
        )

        worker.error.connect(
            thread.quit
        )

        thread.finished.connect(
            worker.deleteLater
        )

        thread.finished.connect(
            thread.deleteLater
        )

        thread.finished.connect(
            self._thread_finished
        )

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        thread.start()

    # ======================================================
    # WYNIK OPERACJI
    # ======================================================

    @Slot(object)
    def _operation_result(
        self,
        result,
    ) -> None:

        if result.success:

            self.operation_finished(
                self._success_text,
                "success",
            )

            QMessageBox.information(
                self,
                self._dialog_title,
                result.message
                or self._success_text,
            )

        else:

            color = (
                "warning"
                if self._warning_on_failure
                else "error"
            )

            self.operation_finished(
                self._error_text,
                color,
            )

            if self._warning_on_failure:

                QMessageBox.warning(
                    self,
                    self._dialog_title,
                    result.message
                    or self._error_text,
                )

            else:

                QMessageBox.critical(
                    self,
                    self._dialog_title,
                    result.message
                    or self._error_text,
                )

    # ======================================================
    # BŁĄD WORKERA
    # ======================================================

    @Slot(str)
    def _operation_error(
        self,
        message: str,
    ) -> None:

        self.set_operations_enabled(
            True
        )

        self.set_status(
            "Błąd operacji.",
            "error",
        )

        logger.error(
            f"OPERATION ERROR: {message}"
        )

        QMessageBox.critical(
            self,
            "Błąd operacji",
            message,
        )

    # ======================================================
    # KONIEC THREADU
    # ======================================================

    @Slot()
    def _thread_finished(
        self,
    ) -> None:

        self._worker = None
        self._thread = None

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

    def backup(
        self,
    ) -> None:

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

        self._start_operation(
            operation=lambda: BackupService().backup(
                destination
            ),
            name="BACKUP",
            success_text="Backup zakończony pomyślnie.",
            error_text="Backup zakończony błędem.",
            dialog_title="Backup",
        )

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(
        self,
    ) -> None:

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

        self._start_operation(
            operation=lambda: ValidateService().validate(),
            name="VALIDATE",
            success_text="Walidacja zakończona.",
            error_text="Walidacja wykazała problem.",
            dialog_title="Validate",
            warning_on_failure=True,
        )

    # ======================================================
    # SWEEP
    # ======================================================

    def sweep(
        self,
    ) -> None:

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

        self._start_operation(
            operation=lambda: SweepService().sweep(),
            name="SWEEP",
            success_text="Sweep zakończony pomyślnie.",
            error_text="Sweep zakończony błędem.",
            dialog_title="Sweep",
        )

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(
        self,
    ) -> None:

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

        self._start_operation(
            operation=lambda: RestoreService().restore(
                backup_file,
                database_file,
                replace=True,
            ),
            name="RESTORE",
            success_text="Restore zakończony pomyślnie.",
            error_text="Restore zakończony błędem.",
            dialog_title="Restore",
        )

    # ======================================================
    # MEND
    # ======================================================

    def mend(
        self,
    ) -> None:

        # --------------------------------------------------
        # OKNO OSTRZEŻENIA
        # --------------------------------------------------

        message_box = QMessageBox(
            self
        )

        message_box.setIcon(
            QMessageBox.Warning
        )

        message_box.setWindowTitle(
            "UWAGA — MEND"
        )

        message_box.setText(
            (
                "OPERACJA NAPRAWCZA\n\n"
                "MEND jest operacją ingerującą w strukturę "
                "bazy danych.\n\n"
                "Przed wykonaniem upewnij się, że posiadasz "
                "aktualny backup bazy.\n\n"
                "Zalecane jest również wykonanie Validate "
                "przed MEND.\n\n"
                "Czy na pewno chcesz kontynuować?"
            )
        )

        message_box.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No
        )

        message_box.setDefaultButton(
            QMessageBox.No
        )

        yes_button = message_box.button(
            QMessageBox.Yes
        )

        no_button = message_box.button(
            QMessageBox.No
        )

        if yes_button:
            yes_button.setText(
                "Tak"
            )

        if no_button:
            no_button.setText(
                "Nie"
            )

        answer = message_box.exec()

        if answer != QMessageBox.Yes:
            return

        from services.firebird.mend_service import (
            MendService,
        )

        self._start_operation(
            operation=lambda: MendService().mend(),
            name="MEND",
            success_text="MEND zakończony pomyślnie.",
            error_text="MEND zakończony błędem.",
            dialog_title="MEND",
        )

    # ======================================================
    # START OPERACJI
    # ======================================================

    def _start_operation(
        self,
        operation,
        name: str,
        success_text: str,
        error_text: str,
        dialog_title: str,
        warning_on_failure: bool = False,
    ) -> None:

        # Zapamiętujemy informacje o operacji.
        self._success_text = success_text
        self._error_text = error_text
        self._dialog_title = dialog_title
        self._warning_on_failure = warning_on_failure

        self.run_async_operation(
            operation=operation,
            name=name,
            success_text=success_text,
            error_text=error_text,
            dialog_title=dialog_title,
            warning_on_failure=warning_on_failure,
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

        if self._thread is not None:

            if self._thread.isRunning():

                self._thread.quit()

                self._thread.wait()

        event.accept()