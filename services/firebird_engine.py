from core.logger import logger
from models.operation_result import OperationResult


class FirebirdEngine:

    def detect_installations(self):

        logger.info("Wyszukiwanie instalacji Firebird...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def detect_version(self):

        logger.info("Wykrywanie wersji Firebird...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def backup(self):

        logger.info("Backup bazy danych...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def restore(self):

        logger.info("Restore bazy danych...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def validate(self):

        logger.info("Validate bazy danych...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def sweep(self):

        logger.info("Sweep bazy danych...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )

    def mend(self):

        logger.info("Mend bazy danych...")

        return OperationResult(
            success=True,
            message="Jeszcze nie zaimplementowano"
        )


engine = FirebirdEngine()