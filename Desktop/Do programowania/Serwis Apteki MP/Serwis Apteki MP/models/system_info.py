from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SystemInfo:
    computer_name: str
    user: str
    windows: str
    windows_version: str
    cpu_name: str
    cpu_usage: float
    ram_total_gb: float
    ram_used_gb: float
    ram_percent: int
    uptime: str
