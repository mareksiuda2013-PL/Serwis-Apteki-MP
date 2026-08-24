from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from core.logger import logger
from models.operation_result import OperationResult


@dataclass(slots=True)
class OperationExecutionResult:
    """
    Wewnętrzny wynik wykonania operacji.

    Klasa pozostaje kompatybilna z istniejącym
    mechanizmem FirebirdOperationService.
    """

    success: bool
    message: str = ""
    result: Any = None


class FirebirdOperationService:
    """
    Centralny wykonawca operacji Firebird.

    Odpowiada za:
        - rozpoczęcie operacji,
        - wykonanie funkcji serwisowej,
        - obsługę wyjątków,
        - logowanie,
        - normalizację wyniku do OperationResult.
    """

    def execute(
        self,
        operation: Callable[[], Any],
        name: str,
    ) -> OperationResult:

        logger.info(
            f"Rozpoczęto operację: {name}"
        )

        try:
            result = operation()

        except Exception as exc:

            logger.error(
                f"{name} ERROR: {exc}"
            )

            return OperationResult(
                success=False,
                message=str(exc),
                error=str(exc),
            )

        # ==================================================
        # WYNIK JUŻ BĘDĄCY OperationResult
        # ==================================================

        if isinstance(
            result,
            OperationResult,
        ):

            if result.success:

                logger.info(
                    f"Operacja zakończona pomyślnie: {name}"
                )

            else:

                logger.error(
                    f"Operacja zakończona błędem: {name}"
                )

            return result

        # ==================================================
        # TUPLE: (bool, message)
        # ==================================================

        if (
            isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[0], bool)
        ):

            success, message = result

            success = bool(success)

            message = str(
                message or ""
            )

            if success:

                logger.info(
                    f"Operacja zakończona pomyślnie: {name}"
                )

            else:

                logger.error(
                    f"Operacja zakończona błędem: {name}"
                )

            return OperationResult(
                success=success,
                message=message,
                output=message
                if success
                else "",
                error=message
                if not success
                else "",
            )

        # ==================================================
        # OBIEKT Z .SUCCESS
        # ==================================================

        if hasattr(
            result,
            "success",
        ):

            success = bool(
                getattr(
                    result,
                    "success",
                    False,
                )
            )

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

            message = (
                output
                if success
                else error or output
            )

            if success:

                logger.info(
                    f"Operacja zakończona pomyślnie: {name}"
                )

            else:

                logger.error(
                    f"Operacja zakończona błędem: {name}"
                )

            return OperationResult(
                success=success,
                message=message,
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

        # ==================================================
        # STANDARDOWY SUKCES
        # ==================================================

        logger.info(
            f"Operacja zakończona pomyślnie: {name}"
        )

        return OperationResult(
            success=True,
            message="Operacja zakończona pomyślnie.",
        )