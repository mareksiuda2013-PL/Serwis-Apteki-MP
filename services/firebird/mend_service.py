from __future__ import annotations

from pathlib import Path

from config import Config
from core.process_runner import ProcessRunner

from .discovery.installation_service import InstallationService
from .service_service import ServiceService
from .validate_service import ValidateService


class MendService:

    def __init__(
        self,
        database: str | Path | None = None,
    ) -> None:

        self.cfg = Config()

        self.service = ServiceService()
        self.runner = ProcessRunner()

        # ==================================================
        # AKTYWNA BAZA
        # ==================================================

        if database:

            self.database = Path(
                database
            )

        else:

            self.database = Path(
                self.cfg.database
            )

        # ==================================================
        # FIREBIRD
        # ==================================================

        self.installation = (
            InstallationService()
            .first_installation()
        )

        if self.installation is None:

            raise RuntimeError(
                "Nie znaleziono instalacji Firebird."
            )

        if self.installation.gfix is None:

            raise RuntimeError(
                "Nie znaleziono gfix.exe."
            )

        self.gfix = self.installation.gfix

    # ======================================================
    # MEND
    # ======================================================

    def mend(self):

        service_name = (
            self.service.find_firebird_service()
        )

        if not service_name:

            raise RuntimeError(
                "Nie znaleziono usługi Firebird."
            )

        original_status = (
            self.service.status(
                service_name
            )
        )

        if original_status == "Not Installed":

            raise RuntimeError(
                f"Usługa Firebird nie istnieje: "
                f"{service_name}"
            )

        # ==================================================
        # ZATRZYMANIE USŁUGI
        # ==================================================

        if not self.service.stop(
            service_name
        ):

            raise RuntimeError(
                "Nie udało się zatrzymać usługi "
                f"Firebird: {service_name}"
            )

        try:

            # ==================================================
            # MEND
            # ==================================================

            command = [
                str(self.gfix),
                "-mend",
                "-full",
                str(self.database),
                "-user",
                self.cfg.user,
                "-password",
                self.cfg.password,
            ]

            result = self.runner.run(
                command,
                timeout=1800,
                operation="MEND",
            )

            if not result.success:

                return result

            # ==================================================
            # URUCHOMIENIE USŁUGI
            # ==================================================

            if not self.service.start(
                service_name
            ):

                raise RuntimeError(
                    "MEND zakończony, ale nie udało się "
                    "uruchomić usługi Firebird."
                )

            # ==================================================
            # WALIDACJA PO MEND
            # ==================================================

            validation = (
                ValidateService(
                    database=self.database
                ).validate()
            )

            if not validation.success:

                raise RuntimeError(
                    "MEND zakończony, ale walidacja "
                    "po naprawie wykazała problem.\n\n"
                    + (
                        validation.stderr
                        or validation.stdout
                        or "Brak informacji o błędzie."
                    )
                )

            return result

        except Exception:

            # ==================================================
            # AWARYJNE URUCHOMIENIE USŁUGI
            # ==================================================

            if (
                self.service.status(
                    service_name
                )
                != "Running"
            ):

                self.service.start(
                    service_name
                )

            raise