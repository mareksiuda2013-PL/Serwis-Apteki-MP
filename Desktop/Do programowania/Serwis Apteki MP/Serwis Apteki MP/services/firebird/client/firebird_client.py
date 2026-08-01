from __future__ import annotations

import subprocess

from services.firebird.installation_service import FirebirdInstallation


class FirebirdClient:

    def __init__(self, installation: FirebirdInstallation):

        self.installation = installation

    def execute(
        self,
        database: str,
        user: str,
        password: str,
        sql: str,
    ) -> tuple[bool, str]:

        if self.installation is None:
            return False, "Brak instalacji Firebird."

        if self.installation.isql is None:
            return False, "Nie znaleziono programu isql."

        script = (
    "SET HEADING OFF;\n"
    "SET LIST OFF;\n"
    "SET ECHO OFF;\n"
    f"{sql.strip()}\n"
    "QUIT;\n"
)

        result = subprocess.run(
            [
                str(self.installation.isql),
                "-user",
                user,
                "-password",
                password,
                database,
            ],
            input=script,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        output = (
            result.stdout
            .replace("SQL>", "")
            .replace("CON>", "")
            .strip()
        )

        if result.returncode != 0:
            return False, result.stderr.strip()

        return True, output