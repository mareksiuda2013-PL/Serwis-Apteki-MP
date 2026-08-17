from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SystemInfo:

    # ==================================================
    # KOMPUTER
    # ==================================================

    computer_name: str = ""
    user: str = ""

    # ==================================================
    # WINDOWS
    # ==================================================

    windows: str = ""
    windows_version: str = ""
    windows_architecture: str = ""

    # ==================================================
    # CPU
    # ==================================================

    cpu_name: str = ""
    cpu_usage: float = 0.0
    cpu_cores: int = 0
    cpu_threads: int = 0
    cpu_frequency_mhz: float = 0.0

    # ==================================================
    # RAM
    # ==================================================

    ram_total_gb: float = 0.0
    ram_used_gb: float = 0.0
    ram_percent: int = 0

    # ==================================================
    # SYSTEM
    # ==================================================

    uptime: str = ""
    boot_time: str = ""

    # ==================================================
    # PYTHON
    # ==================================================

    python_version: str = ""