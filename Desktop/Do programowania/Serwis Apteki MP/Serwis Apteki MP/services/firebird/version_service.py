from __future__ import annotations

from pathlib import Path
from typing import Optional
import subprocess


class VersionService:
    """
    Odczytuje wersję Firebirda z firebird.exe.
    """

    def get_version(self, bin_path: Path | None) -> str:

        if bin_path is None:
            return ""

        exe = bin_path / "firebird.exe"

        if not exe.exists():
            return ""

        try:

            result = subprocess.run(
                [str(exe), "-z"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            text = (
                result.stdout
                + "\n"
                + result.stderr
            )

            for line in text.splitlines():

                line = line.strip()

                if line.lower().startswith("firebird"):

                    return line

        except Exception:
            pass

        return ""