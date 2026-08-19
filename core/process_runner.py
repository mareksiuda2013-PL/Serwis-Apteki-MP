from __future__ import annotations

import subprocess
import time

from core.logger import logger


class ProcessResult:

    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
        duration: float = 0.0,
    ):
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.duration = duration


class ProcessRunner:

    def __init__(self):
        self.logger = logger

    def run(
        self,
        command: list[str],
        input_text: str | None = None,
        timeout: int = 600,
        operation: str = "PROCESS",
        log_operation: bool = True,
    ) -> ProcessResult:

        start = time.perf_counter()

        # ==================================================
        # START
        # ==================================================

        if log_operation:

            self.logger.log(
                operation,
                True,
                "START",
            )

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

            duration = (
                time.perf_counter()
                - start
            )

            process_result = ProcessResult(
                success=result.returncode == 0,
                stdout=result.stdout.strip(),
                stderr=result.stderr.strip(),
                return_code=result.returncode,
                duration=duration,
            )

            # ==================================================
            # SUKCES
            # ==================================================

            if process_result.success:

                message = (
                    f"czas: {duration:.2f} s"
                )

            # ==================================================
            # BŁĄD PROCESU
            # ==================================================

            else:

                error = (
                    process_result.stderr
                    or process_result.stdout
                    or "Brak informacji o błędzie."
                )

                message = (
                    f"czas: {duration:.2f} s | "
                    f"{error[:500]}"
                )

            # ==================================================
            # KONIEC
            # ==================================================

            if log_operation:

                self.logger.log(
                    operation,
                    process_result.success,
                    message,
                )

            return process_result

        # ======================================================
        # TIMEOUT
        # ======================================================

        except subprocess.TimeoutExpired:

            duration = (
                time.perf_counter()
                - start
            )

            if log_operation:

                self.logger.log(
                    operation,
                    False,
                    f"TIMEOUT | czas: {duration:.2f} s",
                )

            return ProcessResult(
                success=False,
                stderr=(
                    "Przekroczono czas "
                    "wykonywania procesu."
                ),
                return_code=-1,
                duration=duration,
            )

        # ======================================================
        # WYJĄTEK
        # ======================================================

        except Exception as exc:

            duration = (
                time.perf_counter()
                - start
            )

            if log_operation:

                self.logger.log(
                    operation,
                    False,
                    f"{exc} | czas: {duration:.2f} s",
                )

            return ProcessResult(
                success=False,
                stderr=str(exc),
                return_code=-1,
                duration=duration,
            )