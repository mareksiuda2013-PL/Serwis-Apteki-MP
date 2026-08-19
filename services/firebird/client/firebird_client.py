from __future__ import annotations

from config import Config
from core.process_runner import ProcessRunner
from services.firebird.discovery.installation_service import FirebirdInstallation


class FirebirdClient:

    def __init__(self, installation: FirebirdInstallation):

        self.installation = installation
        self.cfg = Config()
        self.runner = ProcessRunner()

    def execute(self, sql: str) -> tuple[bool, str]:

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

        result = self.runner.run(
            [
                str(self.installation.isql),
                "-user",
                self.cfg.user,
                "-password",
                self.cfg.password,
                self.cfg.database,
        ],
        input_text=script,
        operation="ISQL",
        log_operation=False,
    )

        if not result.success:
            return False, result.stderr

        lines = []

        for line in result.stdout.splitlines():

            line = line.strip()

            if (
                not line
                or line.startswith("Database:")
                or line.startswith("SQL>")
                or line.startswith("CON>")
            ):
                continue

            lines.append(line)

        return True, "\n".join(lines)

    def fetch_one(self, sql: str) -> str | None:

        ok, result = self.execute(sql)

        if not ok:
            raise RuntimeError(result)

        rows = [r.strip() for r in result.splitlines() if r.strip()]

        return rows[0] if rows else None

    def fetch_all(self, sql: str) -> list[str]:

        ok, result = self.execute(sql)

        if not ok:
            raise RuntimeError(result)

        return [r.strip() for r in result.splitlines() if r.strip()]