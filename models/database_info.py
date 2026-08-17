from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class DatabaseInfo:
    path: Path | None = None

    exists: bool = False

    size_bytes: int = 0
    size_mb: float = 0
    size_gb: float = 0

    modified: datetime | None = None

    ods: str = ""
    page_size: int = 0
    dialect: int = 0

    forced_writes: str = ""
    sweep_interval: int = 0

    read_only: bool = False

    owner: str = ""