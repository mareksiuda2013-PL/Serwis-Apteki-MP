from __future__ import annotations

from pathlib import Path

from services.firebird.base_firebird_service import BaseFirebirdService


class RestoreService(BaseFirebirdService):
    """
    Serwis odpowiedzialny za przywracanie bazy Firebird
    z pliku FBK za pomocą gbak.
    """

    def __init__(self) -> None:
        super().__init__()

        if self.installation.gbak is None:
            raise RuntimeError(
                "Nie znaleziono gbak.exe."
            )

        self.gbak = self.installation.gbak

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(
        self,
        backup_file: str | Path,
        database_file: str | Path,
        replace: bool = True,
    ) -> tuple[bool, str]:

        backup_file = Path(
            backup_file
        )

        database_file = Path(
            database_file
        )

        # ==================================================
        # SPRAWDZENIE BACKUPU
        # ==================================================

        if not backup_file.exists():

            return (
                False,
                f"Nie znaleziono backupu:\n{backup_file}",
            )

        if not backup_file.is_file():

            return (
                False,
                f"Podana ścieżka backupu nie jest plikiem:\n"
                f"{backup_file}",
            )

        # ==================================================
        # SPRAWDZENIE BAZY DOCELOWEJ
        # ==================================================

        if database_file.exists() and not replace:

            return (
                False,
                f"Baza już istnieje:\n{database_file}",
            )

        # ==================================================
        # KATALOG DOCELOWY
        # ==================================================

        parent = database_file.parent

        if not parent.exists():

            try:

                parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

            except OSError as exc:

                return (
                    False,
                    (
                        "Nie udało się utworzyć katalogu "
                        f"docelowego:\n{parent}\n\n"
                        f"{exc}"
                    ),
                )

        # ==================================================
        # KOMENDA GBAK
        # ==================================================

        command = [
            str(self.gbak),
            "-c",
            "-v",
        ]

        if replace:

            command.append(
                "-rep"
            )

        command.extend(
            [
                "-user",
                self.cfg.user,
                "-password",
                self.cfg.password,
                str(backup_file),
                str(database_file),
            ]
        )

        # ==================================================
        # WYKONANIE
        # ==================================================

        result = self.runner.run(
            command,
            timeout=1800,
            operation="RESTORE",
        )

        # ==================================================
        # WYNIK
        # ==================================================

        if result.success:

            return (
                True,
                result.stdout,
            )

        return (
            False,
            result.stderr
            or result.stdout
            or "Restore nie powiódł się.",
        )