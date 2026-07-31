from __future__ import annotations

import getpass
import platform
import socket
import time
from dataclasses import dataclass

import psutil


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


class SystemService:

    def get_info(self) -> SystemInfo:

        memory = psutil.virtual_memory()

        uptime_seconds = int(time.time() - psutil.boot_time())

        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60

        uptime = f"{days} dni {hours:02}:{minutes:02}"

        cpu_name = platform.processor()

        if not cpu_name:
            cpu_name = "Nieznany"

        return SystemInfo(
            computer_name=socket.gethostname(),
            user=getpass.getuser(),
            windows=platform.system(),
            windows_version=platform.release(),
            cpu_name=cpu_name,
            cpu_usage=psutil.cpu_percent(interval=0.3),
            ram_total_gb=round(memory.total / 1024**3, 1),
            ram_used_gb=round(memory.used / 1024**3, 1),
            ram_percent=memory.percent,
            uptime=uptime,
        )