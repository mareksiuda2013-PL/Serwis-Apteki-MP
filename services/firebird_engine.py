from __future__ import annotations

from pathlib import Path

from core.logger import logger
from models.operation_result import OperationResult

from services.firebird.backup_service import BackupService
from services.firebird.mend_service import MendService
from services.firebird.operation_service import (
    FirebirdOperationService,
)
from services.firebird.restore_service import RestoreService
from services.firebird.sweep_service import SweepService
from services.firebird.validate_service import ValidateService


class FirebirdEngine:
    """
    Główna fasada operacji Firebird.

    Engine nie wykonuje bezpośrednio poleceń gbak/gfix.

    Odpowiedzialność:

        FirebirdEngine
              ↓
        FirebirdOperationService
              ↓
        odpowiedni Service
              ↓
        ProcessRunner
              ↓
        gbak / gfix
    """

    def __init__(
        self,
        operation_service: (
            FirebirdOperationService | None
        ) = None,
    ) -> None:

        self.operation_service = (
            operation_service
            or FirebirdOperationService()
        )

    # ==================================================
    # BACKUP
    # ==================================================

    def backup(
        self,
        destination: str | Path,
    ) -> OperationResult:

        return self.operation_service.execute(
            lambda: BackupService().backup(
                destination
            ),
            "BACKUP",
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

        return self.operation_service.execute(
            lambda: RestoreService().restore(
                backup_file=backup_file,
                database_file=database_file,
                replace=replace,
            ),
            "RESTORE",
        )

    # ==================================================
    # VALIDATE
    # ==================================================

    def validate(self) -> OperationResult:

        return self.operation_service.execute(
            lambda: ValidateService().validate(),
            "VALIDATE",
        )

    # ==================================================
    # SWEEP
    # ==================================================

    def sweep(self) -> OperationResult:

        return self.operation_service.execute(
            lambda: SweepService().sweep(),
            "SWEEP",
        )

    # ==================================================
    # MEND
    # ==================================================

    def mend(self) -> OperationResult:

        return self.operation_service.execute(
            lambda: MendService().mend(),
            "MEND",
        )


engine = FirebirdEngine()