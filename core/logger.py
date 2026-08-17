from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, Signal, Qt


class Logger(QObject):

    message = Signal(str)

    def __init__(
        self,
        log_dir: str | Path = "logs",
    ):
        super().__init__()

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._callbacks: list[
            Callable[[str], None]
        ] = []

    def set_callback(
        self,
        callback: Callable[[str], None] | None,
    ):

        self._callbacks.clear()

        if callback is not None:
            self.add_callback(callback)

    def add_callback(
        self,
        callback: Callable[[str], None],
    ):

        if callback not in self._callbacks:

            self._callbacks.append(callback)

            try:
                self.message.connect(
                    callback,
                    Qt.QueuedConnection,
                )
            except Exception:
                pass

    def _write(
        self,
        level: str,
        message: str,
    ):

        now = datetime.now()

        text = (
            f"{now:%Y-%m-%d %H:%M:%S} | "
            f"{level} | "
            f"{message}"
        )

        file_path = (
            self.log_dir
            / f"{now:%Y-%m-%d}.log"
        )

        with file_path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(text + "\n")

        self.message.emit(text)

    def info(
        self,
        message: str,
    ):

        self._write(
            "INFO",
            message,
        )

    def warning(
        self,
        message: str,
    ):

        self._write(
            "WARNING",
            message,
        )

    def error(
        self,
        message: str,
    ):

        self._write(
            "ERROR",
            message,
        )

    def debug(
        self,
        message: str,
    ):

        self._write(
            "DEBUG",
            message,
        )

    def log(
        self,
        operation: str,
        success: bool,
        message: str = "",
    ):

        status = (
            "OK"
            if success
            else "ERROR"
        )

        text = (
            f"{operation} | "
            f"{status}"
        )

        if message:
            text += f" | {message}"

        self._write(
            "OPERATION",
            text,
        )


logger = Logger()