from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from core.logger import logger


@dataclass(slots=True)
class OperationResult:
    """
    Wspólny wynik operacji administracyjnej Firebird.
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
        - zwrócenie jednolitego wyniku.
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
                result=None,
            )

        # --------------------------------------------------
        # OPERACJE ZWRACAJĄCE (bool, log)
        # --------------------------------------------------

        if (
            isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[0], bool)
        ):

            success, message = result

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
                message=str(message or ""),
                result=result,
            )

        # --------------------------------------------------
        # OPERACJE ZWRACAJĄCE OBIEKT Z .SUCCESS
        # --------------------------------------------------

        if hasattr(result, "success"):

            success = bool(
                result.success
            )

            message = (
                getattr(result, "stdout", "")
                or getattr(result, "stderr", "")
                or ""
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
                message=str(message),
                result=result,
            )

        # --------------------------------------------------
        # STANDARDOWY SUKCES
        # --------------------------------------------------

        logger.info(
            f"Operacja zakończona pomyślnie: {name}"
        )

        return OperationResult(
            success=True,
            message="Operacja zakończona pomyślnie.",
            result=result,
        )