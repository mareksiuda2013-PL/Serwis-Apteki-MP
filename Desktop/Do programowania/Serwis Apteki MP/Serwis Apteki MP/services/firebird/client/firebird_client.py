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
            return False, "Nie znaleziono isql.exe."

        query = sql.strip()

        if not query.endswith(";"):
            query += ";"

        script = (
            "SET HEADING OFF;\n"
            "SET LIST OFF;\n"
            "SET ECHO OFF;\n"
            f"{query}\n"
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

        if result.returncode != 0:
            return False, result.stderr.strip()

        lines = []

        for line in result.stdout.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("Database:"):
                continue

            if line.startswith("SQL>"):
                continue

            if line.startswith("CON>"):
                continue

            lines.append(line)

        return True, "\n".join(lines)

    def fetch_one(
        self,
        database: str,
        user: str,
        password: str,
        sql: str,
    ) -> str | None:

        ok, result = self.execute(
            database,
            user,
            password,
            sql,
        )

        if not ok:
            raise RuntimeError(result)

        rows = [line.strip() for line in result.splitlines() if line.strip()]

        if not rows:
            return None

        return rows[0]

    def fetch_all(
        self,
        database: str,
        user: str,
        password: str,
        sql: str,
    ) -> list[str]:

        ok, result = self.execute(
            database,
            user,
            password,
            sql,
        )

        if not ok:
            raise RuntimeError(result)

        return [line.strip() for line in result.splitlines() if line.strip()]