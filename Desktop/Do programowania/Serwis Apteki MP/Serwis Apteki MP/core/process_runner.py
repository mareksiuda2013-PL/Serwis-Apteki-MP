from __future__ import annotations

import subprocess
from pathlib import Path


class ProcessResult:

    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code


class ProcessRunner:

    def run(
        self,
        command: list[str],
        input_text: str | None = None,
        timeout: int = 600,
    ) -> ProcessResult:

        try:

            result = subprocess.run(
                command,
                input=input_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=timeout,
            )

            return ProcessResult(
                success=result.returncode == 0,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
            )

        except subprocess.TimeoutExpired:

            return ProcessResult(
                success=False,
                stderr="Przekroczono czas wykonywania procesu.",
                return_code=-1,
            )

        except Exception as e:

            return ProcessResult(
                success=False,
                stderr=str(e),
                return_code=-1,
            )