from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DiskInfo:
    drive: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: int