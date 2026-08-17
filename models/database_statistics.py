from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DatabaseStatistics:

    ods: str = ""
    page_size: int = 0
    page_buffers: int = 0

    sweep_interval: int = 0

    forced_writes: bool = False
    no_reserve: bool = False

    oldest_transaction: int = 0
    oldest_active: int = 0
    oldest_snapshot: int = 0
    next_transaction: int = 0

    database_dialect: int = 0
    generation: int = 0
    creation_date: str = ""