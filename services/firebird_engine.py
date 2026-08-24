from __future__ import annotations

from pathlib import Path

from core.logger import logger
from models.operation_result import OperationResult

from services.firebird.backup_service import BackupService
from services.firebird.mend_service import MendService
from services.firebird.restore_service import RestoreService
from services.firebird.sweep_service import SweepService
from services.firebird.validate_service import ValidateService


class FirebirdEngine:
    """
    Główna fasada operacji Firebird.

    Engine nie wykonuje bezpośrednio poleceń gbak/gfix.

    Odpowiedzialność Engine:

        Engine
            ↓
        odpowiedni Service
            ↓
        ProcessRunner
            ↓
        gbak / gfix
    """

    # ==================================================
    # BACKUP
    # ==================================================

    def backup(
        self,
        destination: str | Path,
    ) -> OperationResult:

        logger.info(
            "Engine: rozpoczęcie BACKUP."
        )

        try:

            success, message = (
                BackupService().backup(
                    destination
                )
            )

            return OperationResult(
                success=success,
                message=str(message or ""),
            )

        except Exception as exc:

            logger.error(
                f"Engine BACKUP ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

    # ==================================================
    # RESTORE
    # ==================================================

    def restore(
        self,
        backup_file: str | Path,
        database_file: str | Path,
        replace: bool = True,
    ) -> OperationResult:

        logger.info(
            "Engine: rozpoczęcie RESTORE."
        )

        try:

            success, message = (
                RestoreService().restore(
                    backup_file=backup_file,
                    database_file=database_file,
                    replace=replace,
                )
            )

            return OperationResult(
                success=success,
                message=str(message or ""),
            )

        except Exception as exc:

            logger.error(
                f"Engine RESTORE ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

    # ==================================================
    # VALIDATE
    # ==================================================

    def validate(self) -> OperationResult:

        logger.info(
            "Engine: rozpoczęcie VALIDATE."
        )

        try:

            result = (
                ValidateService().validate()
            )

            return self._from_process_result(
                result
            )

        except Exception as exc:

            logger.error(
                f"Engine VALIDATE ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

    # ==================================================
    # SWEEP
    # ==================================================

    def sweep(self) -> OperationResult:

        logger.info(
            "Engine: rozpoczęcie SWEEP."
        )

        try:

            result = (
                SweepService().sweep()
            )

            return self._from_process_result(
                result
            )

        except Exception as exc:

            logger.error(
                f"Engine SWEEP ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

    # ==================================================
    # MEND
    # ==================================================

    def mend(self) -> OperationResult:

        logger.info(
            "Engine: rozpoczęcie MEND."
        )

        try:

            result = (
                MendService().mend()
            )

            return self._from_process_result(
                result
            )

        except Exception as exc:

            logger.error(
                f"Engine MEND ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

    # ==================================================
    # PROCESS RESULT
    # ==================================================

    @staticmethod
    def _from_process_result(
        result,
    ) -> OperationResult:
        """
        Konwertuje wynik ProcessRunner
        na wspólny OperationResult.
        """

        output = str(
            getattr(
                result,
                "stdout",
                "",
            )
            or getattr(
                result,
                "output",
                "",
            )
            or ""
        )

        error = str(
            getattr(
                result,
                "stderr",
                "",
            )
            or getattr(
                result,
                "error",
                "",
            )
            or ""
        )

        success = bool(
            getattr(
                result,
                "success",
                False,
            )
        )

        return OperationResult(
            success=success,
            message=(
                output
                if success
                else error or output
            ),
            output=output,
            error=error,
            command=str(
                getattr(
                    result,
                    "command",
                    "",
                )
                or ""
            ),
            exit_code=int(
                getattr(
                    result,
                    "exit_code",
                    0,
                )
                or 0
            ),
            started=getattr(
                result,
                "started",
                None,
            ),
            finished=getattr(
                result,
                "finished",
                None,
            ),
            duration=float(
                getattr(
                    result,
                    "duration",
                    0.0,
                )
                or 0.0
            ),
        )


engine = FirebirdEngine()