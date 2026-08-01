from __future__ import annotations

import subprocess
from pathlib import Path


class FirebirdClient:

    def __init__(self, firebird_path: str | Path):

        root = Path(firebird_path)

        candidates = [
            root / "isql",
            root / "isql.exe",
            root / "bin" / "isql",
            root / "bin" / "isql.exe",
        ]

        self.isql = None

        for file in candidates:
            if file.exists():
                self.isql = file
                break

    def execute(
        self,
        database: str,
        user: str,
        password: str,
        sql: str,
    ) -> tuple[bool, str]:

        if self.isql is None:
            return False, "Nie znaleziono programu ISQL."

        result = subprocess.run(
            [
                str(self.isql),
                "-user",
                user,
                "-password",
                password,
                database,
            ],
            input=sql + "\nquit;\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

        if result.returncode != 0:
            return False, result.stderr

        return True, result.stdout