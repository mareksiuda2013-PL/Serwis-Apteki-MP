from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OperationResult:
    """
    Wynik wykonania operacji.
    """

    success: bool = False

    message: str = ""

    command: str = ""

    output: str = ""

    error: str = ""

    exit_code: int = 0

    started: datetime | None = None
    finished: datetime | None = None

    duration: float = 0.0